
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

try:
    from streamlit_agraph import agraph, Node, Edge, Config
    HAS_AGRAPH = True
except Exception:
    HAS_AGRAPH = False

try:
    import py3Dmol
    import streamlit.components.v1 as components
    HAS_3DMOL = True
except Exception:
    HAS_3DMOL = False

from src.demo_data import (
    generate_residue_table,
    generate_map_quality_table,
    generate_unknown_hits,
    generate_validation_metrics,
    generate_domain_table,
    generate_chain_graph,
    generate_nucleotide_table,
    generate_ligand_table,
    generate_mutation_table,
    generate_job_log,
    demo_pdb_block,
)
from src.commands import build_command_templates
from src.report import build_markdown_report
from src.visuals import (
    workflow_sankey,
    model_quality_gauge,
    residue_radar,
    local_resolution_surface,
    protein_id_evidence_plot,
)

st.set_page_config(
    page_title="CryoModel Studio AI",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');
html, body, [class*="css"] {font-family: 'Inter', sans-serif;}
.block-container {padding-top: 1.2rem; padding-bottom: 2rem; max-width: 1500px;}
.hero {
    border-radius: 30px;
    padding: 34px 34px 30px 34px;
    background:
      radial-gradient(circle at 15% 20%, rgba(102,227,255,.30), transparent 28%),
      radial-gradient(circle at 85% 5%, rgba(169,121,255,.25), transparent 28%),
      radial-gradient(circle at 55% 100%, rgba(70,255,174,.18), transparent 34%),
      linear-gradient(135deg, rgba(10,25,47,.94), rgba(8,13,26,.92));
    border: 1px solid rgba(255,255,255,.16);
    box-shadow: 0 20px 70px rgba(0,0,0,.45);
}
.big-title {
    font-size: 4.0rem; font-weight: 950; line-height: 1.0; letter-spacing: -0.055em;
    background: linear-gradient(90deg, #66E3FF, #A979FF, #46FFAE, #FFE066);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.subtitle {font-size: 1.25rem; color: #D8E3F7; max-width: 980px; margin-top: 10px;}
.pill {
    display: inline-block; padding: 7px 12px; border-radius: 999px;
    background: rgba(255,255,255,.10); border: 1px solid rgba(255,255,255,.16);
    color: #EAF2FF; font-weight: 700; margin-right: 8px; margin-top: 14px; font-size: .88rem;
}
.metric-card {
    border: 1px solid rgba(255,255,255,.13);
    border-radius: 22px; padding: 18px 20px;
    background: linear-gradient(180deg, rgba(255,255,255,.08), rgba(255,255,255,.035));
    box-shadow: 0 10px 35px rgba(0,0,0,.22);
}
.metric-label {color: #9FB0CE; font-size: .9rem; font-weight: 700;}
.metric-value {font-size: 2.15rem; font-weight: 900; color: #F7FBFF;}
.workflow-step {
    border-radius: 18px; padding: 16px 12px; text-align:center; font-weight:800;
    border: 1px solid rgba(255,255,255,.13);
    background: linear-gradient(180deg, rgba(102,227,255,.16), rgba(169,121,255,.07));
    min-height: 72px;
}
.step-sub {color: #B9C6DD; font-size: .78rem; font-weight: 600; margin-top: 4px;}
.small-muted {color: #9FB0CE; font-size: .93rem;}
.panel {
    border-radius: 22px; padding: 20px; margin-bottom: 16px;
    background: rgba(255,255,255,.045); border: 1px solid rgba(255,255,255,.12);
}
.warning-box {
    border-left: 5px solid #FFE066; padding: 14px 18px; border-radius: 14px;
    background: rgba(255, 224, 102, .10);
}
.success-box {
    border-left: 5px solid #46FFAE; padding: 14px 18px; border-radius: 14px;
    background: rgba(70, 255, 174, .10);
}
.danger-box {
    border-left: 5px solid #FF6B8A; padding: 14px 18px; border-radius: 14px;
    background: rgba(255, 107, 138, .10);
}
.module-badge {
    font-size: .78rem; font-weight: 800; color: #06101D;
    background: #66E3FF; border-radius: 999px; padding: 4px 9px;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 🧬 CryoModel Studio AI")
    mode = st.radio("Run mode", ["Demo mode", "Real workflow planner"], index=0)
    st.caption("Demo mode creates realistic-looking structural-biology outputs for interface development.")
    st.divider()

    st.markdown("### Input files")
    map_file = st.file_uploader("Cryo-EM map (.mrc/.map)", type=["mrc", "map"])
    halfmap1 = st.file_uploader("Optional half-map 1", type=["mrc", "map"])
    halfmap2 = st.file_uploader("Optional half-map 2", type=["mrc", "map"])
    seq_file = st.file_uploader("Sequence FASTA", type=["fasta", "fa", "txt"])
    model_file = st.file_uploader("Optional starting model (.pdb/.cif)", type=["pdb", "cif"])
    proteome_file = st.file_uploader("Optional proteome FASTA", type=["fasta", "fa", "txt"])
    st.divider()

    st.markdown("### Workflow controls")
    resolution = st.slider("Estimated map resolution, Å", 1.5, 6.0, 3.2, 0.1)
    model_size = st.slider("Demo residue count", 100, 1800, 620, 20)
    seed = st.number_input("Demo seed", min_value=1, max_value=9999, value=77)
    np.random.seed(int(seed))

    run_enhancement = st.checkbox("Map enhancement", value=True)
    run_modelangelo = st.checkbox("ModelAngelo build", value=True)
    run_refinement = st.checkbox("Refinement", value=True)
    run_protein_id = st.checkbox("Unknown protein finder", value=True)
    run_nucleic = st.checkbox("RNA/DNA checker", value=True)
    run_ligands = st.checkbox("Ligand/cofactor density triage", value=True)
    run_mutations = st.checkbox("Variant impact overlay", value=True)
    st.divider()

    st.markdown("### Visual style")
    color_by = st.selectbox("Primary colouring", ["review_status", "chain", "domain", "confidence_bin"], index=0)
    white_bg_export = st.checkbox("White-background export mode", value=True)

st.markdown("""
<div class="hero">
  <div class="big-title">CryoModel Studio AI</div>
  <div class="subtitle">
    Explainable cryo-EM workspace for map enhancement, automated model building, unknown protein discovery, structure validation, RNA/DNA checking, ligand triage, and reviewer-ready reporting.
  </div>
  <span class="pill">CNN + GNN model building</span>
  <span class="pill">HMM protein ID</span>
  <span class="pill">Q-score confidence</span>
  <span class="pill">Refinement planner</span>
  <span class="pill">Publication figures</span>
</div>
""", unsafe_allow_html=True)

st.markdown("### Mission-control workflow")
step_cols = st.columns(8)
steps = [
    ("1 Map QC", "resolution, FSC, density"),
    ("2 Enhance", "denoise, sharpen"),
    ("3 Build", "ModelAngelo plan"),
    ("4 Protein ID", "HMM profiles"),
    ("5 RNA/DNA", "backbone, bases"),
    ("6 Refine", "geometry, fit"),
    ("7 Validate", "review warnings"),
    ("8 Report", "figures, methods"),
]
for c, (title, sub) in zip(step_cols, steps):
    c.markdown(f'<div class="workflow-step">{title}<div class="step-sub">{sub}</div></div>', unsafe_allow_html=True)

residue_df = generate_residue_table(n=model_size, resolution=resolution)
map_df = generate_map_quality_table(resolution=resolution)
hits_df = generate_unknown_hits()
valid_df = generate_validation_metrics(resolution=resolution)
domain_df = generate_domain_table()
nt_df = generate_nucleotide_table(resolution=resolution)
ligand_df = generate_ligand_table()
mutation_df = generate_mutation_table()
job_log = generate_job_log()

completeness = float((residue_df["confidence"] > 0.55).mean())
mean_conf = residue_df["confidence"].mean()
red_flags = int((residue_df["review_status"] == "Manual review").sum())
mean_q = residue_df["q_score"].mean()
unknown_hit = hits_df.iloc[0]["candidate_gene"]

st.markdown("### Executive dashboard")
mcols = st.columns(6)
metrics = [
    ("Completeness", f"{completeness*100:.1f}%", "built + assigned"),
    ("Mean confidence", f"{mean_conf:.2f}", "local backbone"),
    ("Mean Q-score", f"{mean_q:.2f}", "map resolvability"),
    ("Manual checks", f"{red_flags}", "residues"),
    ("Top unknown hit", str(unknown_hit), "candidate"),
    ("Resolution", f"{resolution:.1f} Å", "estimated"),
]
for c, (label, value, sub) in zip(mcols, metrics):
    c.markdown(f"""
    <div class="metric-card">
      <div class="metric-label">{label}</div>
      <div class="metric-value">{value}</div>
      <div class="small-muted">{sub}</div>
    </div>
    """, unsafe_allow_html=True)

if resolution > 3.8:
    st.markdown('<div class="danger-box">Low-resolution warning: use backbone traces cautiously, inspect side chains manually, and avoid over-interpreting weak density.</div>', unsafe_allow_html=True)
elif resolution > 3.2:
    st.markdown('<div class="warning-box">Intermediate-resolution map: model building is useful, but loops, side-chain assignments, homologous proteins, and RNA/DNA bases need careful validation.</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="success-box">High-confidence operating range: proceed with AI-assisted building, refinement, and reviewer-grade validation.</div>', unsafe_allow_html=True)

tabs = st.tabs([
    "🗺️ Map Doctor",
    "✨ Enhancement Lab",
    "🧠 AI Build",
    "🕸️ Chain Graph",
    "🧬 Unknown Protein Finder",
    "🧫 RNA/DNA Checker",
    "💊 Ligands & Cofactors",
    "🧪 Variants",
    "✅ Validation",
    "📊 Publication Figures",
    "🧾 Report",
    "⚙️ Commands",
])

with tabs[0]:
    st.markdown('<span class="module-badge">MODULE 1</span>  Map Doctor', unsafe_allow_html=True)
    c1, c2 = st.columns([1.2, 1])
    with c1:
        fig = px.line(map_df, x="spatial_frequency", y=["raw_signal", "enhanced_signal", "confidence_weighted_signal"],
                      markers=True, title="Map signal profile, raw versus enhanced versus confidence-weighted")
        fig.update_layout(height=430, legend_title_text="")
        st.plotly_chart(fig, width="stretch")
    with c2:
        fig = local_resolution_surface(resolution)
        st.plotly_chart(fig, width="stretch")
    st.markdown("#### Map-region interpretation")
    st.dataframe(map_df[["region", "local_resolution_A", "density_class", "interpretation", "recommended_action"]],
                 width="stretch", hide_index=True)

with tabs[1]:
    st.markdown('<span class="module-badge">MODULE 2</span>  Enhancement Lab', unsafe_allow_html=True)
    st.write("Plan map-enhancement and show whether sharpening improves interpretability without encouraging overfitting.")
    c1, c2, c3 = st.columns(3)
    c1.plotly_chart(model_quality_gauge("Raw map clarity", max(0.05, 1.0 - resolution/6.5)), width="stretch")
    c2.plotly_chart(model_quality_gauge("Enhanced clarity", min(0.96, 1.18 - resolution/6.5)), width="stretch")
    c3.plotly_chart(model_quality_gauge("Over-sharpening risk", min(0.95, max(0.05, (resolution-2.2)/4.2))), width="stretch")

    enhance_steps = pd.DataFrame({
        "Step": ["Normalize map", "Estimate local resolution", "Denoise", "Sharpen", "Confidence mask", "Export"],
        "Purpose": [
            "Put density on a comparable scale",
            "Find strong and weak regions",
            "Reduce background noise",
            "Improve side-chain visibility",
            "Avoid interpreting unreliable density",
            "Send enhanced map to model building",
        ],
        "Status": ["Ready", "Ready", "Ready", "Ready", "Ready", "Ready"]
    })
    st.dataframe(enhance_steps, width="stretch", hide_index=True)

with tabs[2]:
    st.markdown('<span class="module-badge">MODULE 3</span>  Explainable AI Model Builder', unsafe_allow_html=True)
    c1, c2 = st.columns([1.25, 1])
    with c1:
        fig = px.scatter(
            residue_df, x="residue_index", y="confidence", color=color_by,
            hover_data=["chain", "domain", "residue", "q_score", "local_resolution_A", "review_status"],
            title="Residue-level confidence landscape"
        )
        fig.add_hline(y=0.70, line_dash="dash", annotation_text="Reliable threshold")
        fig.add_hline(y=0.45, line_dash="dash", annotation_text="Manual-review threshold")
        fig.update_layout(height=470)
        st.plotly_chart(fig, width="stretch")
    with c2:
        selected = st.slider("Inspect residue index", 1, int(residue_df.residue_index.max()), 25)
        row = residue_df.iloc[selected - 1]
        st.markdown("#### Residue inspector")
        st.json({
            "chain": row["chain"],
            "domain": row["domain"],
            "residue_index": int(row["residue_index"]),
            "predicted_residue": row["residue"],
            "confidence": round(float(row["confidence"]), 3),
            "q_score": round(float(row["q_score"]), 3),
            "local_resolution_A": round(float(row["local_resolution_A"]), 2),
            "review_status": row["review_status"],
            "plain_language": row["plain_language"]
        })
        st.plotly_chart(residue_radar(row), width="stretch")

    st.markdown("#### Amino-acid probability explanation")
    probs = pd.DataFrame({
        "amino_acid": list("ACDEFGHIKLMNPQRSTVWY"),
        "probability": np.sort(np.random.dirichlet(np.ones(20) * 0.9))[::-1]
    })
    fig2 = px.bar(probs.head(10), x="amino_acid", y="probability", title="Top amino-acid probability guesses for selected residue")
    st.plotly_chart(fig2, width="stretch")

    if HAS_3DMOL:
        st.markdown("#### Demo 3D molecular viewer")
        view = py3Dmol.view(width=900, height=420)
        view.addModel(demo_pdb_block(), "pdb")
        view.setStyle({"cartoon": {"color": "spectrum"}})
        view.addSurface(py3Dmol.VDW, {"opacity": 0.25})
        view.zoomTo()
        components.html(view._make_html(), height=450)
    else:
        st.code(demo_pdb_block()[:1200] + "\n...", language="text")

with tabs[3]:
    st.markdown('<span class="module-badge">MODULE 4</span>  Chain Graph and Domain Connectivity', unsafe_allow_html=True)
    nodes, edges, graph_df = generate_chain_graph()
    if HAS_AGRAPH:
        config = Config(width="100%", height=520, directed=True, physics=True, hierarchical=False)
        agraph(nodes=nodes, edges=edges, config=config)
    else:
        st.info("Install streamlit-agraph for interactive network graph.")
    st.dataframe(graph_df, width="stretch", hide_index=True)
    st.plotly_chart(workflow_sankey(), width="stretch", key="workflow_sankey_chain_graph")

with tabs[4]:
    st.markdown('<span class="module-badge">MODULE 5</span>  Unknown Protein Finder', unsafe_allow_html=True)
    st.write("Rank candidate proteins by profile-HMM evidence, side-chain density support, model confidence, and biological plausibility.")
    st.dataframe(hits_df, width="stretch", hide_index=True)
    st.plotly_chart(protein_id_evidence_plot(hits_df), width="stretch", key="protein_id_evidence_main")
    fig = px.scatter(
        hits_df, x="side_chain_support", y="hmm_score", size="combined_score",
        color="evidence_class", hover_name="candidate_gene",
        title="Evidence map for unknown-chain assignment"
    )
    fig.update_layout(height=460)
    st.plotly_chart(fig, width="stretch")

with tabs[5]:
    st.markdown('<span class="module-badge">MODULE 6</span>  RNA/DNA Checker', unsafe_allow_html=True)
    c1, c2 = st.columns([1.15, 1])
    with c1:
        fig = px.line(nt_df, x="nucleotide_index", y=["backbone_confidence", "base_identity_confidence"],
                      title="Nucleotide backbone versus base-identity confidence")
        fig.update_layout(height=430, legend_title_text="")
        st.plotly_chart(fig, width="stretch")
    with c2:
        st.markdown("#### RNA/DNA warning logic")
        st.write("""
        The backbone can be reliable even when the base identity is uncertain. The app separates
        backbone confidence from A/G or C/U identity confidence, then flags bases that need manual review
        or secondary-structure support.
        """)
        st.dataframe(nt_df[nt_df["review_status"] != "Reliable"].head(18), width="stretch", hide_index=True)

with tabs[6]:
    st.markdown('<span class="module-badge">MODULE 7</span>  Ligand and Cofactor Density Triage', unsafe_allow_html=True)
    st.write("Detect density that may correspond to cofactors, ligands, ions, glycans, lipids, or uninterpreted blobs.")
    st.dataframe(ligand_df, width="stretch", hide_index=True)
    fig = px.bar(ligand_df, x="site", y="density_support", color="assignment_status",
                 hover_data=["candidate", "nearby_residues", "recommended_action"],
                 title="Ligand/cofactor density support")
    st.plotly_chart(fig, width="stretch")

with tabs[7]:
    st.markdown('<span class="module-badge">MODULE 8</span>  Variant Impact Overlay', unsafe_allow_html=True)
    st.write("Overlay missense variants, conserved residues, active-site positions, and low-confidence model regions.")
    st.dataframe(mutation_df, width="stretch", hide_index=True)
    fig = px.scatter(
        mutation_df, x="residue_index", y="predicted_impact", size="confidence",
        color="variant_class", hover_data=["variant", "chain", "structural_context", "action"],
        title="Variant-impact overlay on AI-built structure"
    )
    st.plotly_chart(fig, width="stretch")

with tabs[8]:
    st.markdown('<span class="module-badge">MODULE 9</span>  Validation', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        status_counts = residue_df["review_status"].value_counts().reset_index()
        status_counts.columns = ["status", "count"]
        fig = px.pie(status_counts, values="count", names="status", title="Residue review status")
        st.plotly_chart(fig, width="stretch")
    with c2:
        fig = px.scatter(
            residue_df, x="local_resolution_A", y="q_score", color="review_status",
            hover_data=["chain", "residue_index", "residue", "domain"],
            title="Q-score versus local resolution"
        )
        fig.add_vline(x=3.5, line_dash="dash", annotation_text="caution zone")
        fig.add_vline(x=4.0, line_dash="dash", annotation_text="manual review")
        st.plotly_chart(fig, width="stretch")

    st.markdown("#### Structure validation metrics")
    st.dataframe(valid_df, width="stretch", hide_index=True)
    flagged = residue_df[residue_df["review_status"] == "Manual review"].head(30)
    st.markdown("#### Top residues needing manual review")
    st.dataframe(flagged[["chain", "domain", "residue_index", "residue", "confidence", "q_score", "local_resolution_A", "plain_language"]],
                 width="stretch", hide_index=True)

with tabs[9]:
    st.markdown('<span class="module-badge">MODULE 10</span>  Publication Figure Studio', unsafe_allow_html=True)
    st.write("Generate manuscript-style figures and panels for a structural-biology report.")
    fc1, fc2 = st.columns(2)
    with fc1:
        st.plotly_chart(workflow_sankey(), width="stretch", key="workflow_sankey_publication")
        st.plotly_chart(protein_id_evidence_plot(hits_df), width="stretch", key="protein_id_evidence_publication")
    with fc2:
        fig = px.imshow(
            residue_df.pivot_table(index="chain", columns="residue_index", values="confidence", aggfunc="mean").fillna(0),
            aspect="auto", title="Confidence heatmap by chain"
        )
        st.plotly_chart(fig, width="stretch")
        fig2 = px.bar(domain_df, x="domain", y="mean_confidence", color="risk_level",
                      title="Domain-level confidence summary")
        st.plotly_chart(fig2, width="stretch")
    st.markdown("""
    **Suggested manuscript panels:**  
    A, workflow overview. B, map enhancement and local resolution. C, confidence-coloured atomic model.
    D, unknown-chain identification. E, RNA/DNA confidence separation. F, validation and manual-review warnings.
    """)

with tabs[10]:
    st.markdown('<span class="module-badge">MODULE 11</span>  Report Builder', unsafe_allow_html=True)
    report = build_markdown_report(
        resolution=resolution,
        completeness=completeness,
        mean_conf=mean_conf,
        mean_q=mean_q,
        red_flags=red_flags,
        run_enhancement=run_enhancement,
        run_modelangelo=run_modelangelo,
        run_refinement=run_refinement,
        run_protein_id=run_protein_id,
        run_nucleic=run_nucleic,
        run_ligands=run_ligands,
        run_mutations=run_mutations,
    )
    st.download_button("Download Markdown report", report, file_name="CryoModel_Studio_AI_report.md")
    st.markdown(report)
    st.markdown("#### Demo job log")
    st.code(job_log, language="text")

with tabs[11]:
    st.markdown('<span class="module-badge">MODULE 12</span>  Real Workflow Commands', unsafe_allow_html=True)
    commands = build_command_templates(
        map_path=map_file.name if map_file else "input_map.mrc",
        fasta_path=seq_file.name if seq_file else "input_sequences.fasta",
        model_path=model_file.name if model_file else "modelangelo_output.cif",
        proteome_path=proteome_file.name if proteome_file else "organism_proteome.fasta",
        run_enhancement=run_enhancement,
        run_modelangelo=run_modelangelo,
        run_refinement=run_refinement,
        run_protein_id=run_protein_id,
        run_nucleic=run_nucleic,
        run_ligands=run_ligands,
        run_mutations=run_mutations,
    )
    for title, cmd in commands.items():
        st.markdown(f"#### {title}")
        st.code(cmd, language="bash")

st.divider()
st.caption("CryoModel Studio AI, enhanced prototype. Demo outputs are simulated and should not be used for biological conclusions.")
