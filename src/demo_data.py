
import numpy as np
import pandas as pd

AA = list("ACDEFGHIKLMNPQRSTVWY")
DOMAINS = ["N-terminal arm", "Catalytic core", "Helical bundle", "RNA-binding lobe", "Flexible linker", "C-terminal cap"]

def generate_residue_table(n=620, resolution=3.2):
    chains = np.random.choice(list("ABCD"), size=n, p=[0.35, 0.25, 0.25, 0.15])
    domains = np.random.choice(DOMAINS, size=n, p=[0.14, 0.28, 0.20, 0.13, 0.15, 0.10])
    local_res = np.clip(np.random.normal(resolution, 0.55, n), 1.7, 6.0)
    domain_penalty = np.array([0.16 if d == "Flexible linker" else 0.04 if d == "N-terminal arm" else 0 for d in domains])
    q_score = np.clip(1.05 - (local_res - 1.5) / 4.8 - domain_penalty + np.random.normal(0, 0.06, n), 0.05, 0.98)
    confidence = np.clip(0.15 + 0.82 * q_score + np.random.normal(0, 0.08, n), 0.02, 0.99)
    status = np.where(confidence > 0.70, "Reliable",
             np.where(confidence > 0.45, "Check", "Manual review"))
    bins = np.where(confidence > 0.70, "High", np.where(confidence > 0.45, "Medium", "Low"))
    residues = np.random.choice(AA, n)
    plain = []
    for d, c, q, lr in zip(domains, confidence, q_score, local_res):
        if c > 0.70:
            plain.append(f"{d}: density and geometry agree; likely reliable after refinement.")
        elif c > 0.45:
            plain.append(f"{d}: backbone may be usable, but side-chain identity or loop placement should be checked.")
        else:
            plain.append(f"{d}: weak or ambiguous density; avoid mechanistic interpretation without expert inspection.")
    return pd.DataFrame({
        "chain": chains,
        "domain": domains,
        "residue_index": np.arange(1, n+1),
        "residue": residues,
        "confidence": confidence,
        "confidence_bin": bins,
        "q_score": q_score,
        "local_resolution_A": local_res,
        "review_status": status,
        "plain_language": plain
    })

def generate_map_quality_table(resolution=3.2):
    x = np.linspace(0.05, 0.50, 18)
    raw = np.exp(-x * resolution * 2.8) + np.random.normal(0, 0.022, len(x))
    enhanced = np.clip(raw + np.linspace(0.13, 0.02, len(x)), 0, 1)
    weighted = np.clip(enhanced * np.linspace(1.03, 0.82, len(x)), 0, 1)
    regions = [f"Region {i}" for i in range(1, len(x)+1)]
    local = np.clip(np.random.normal(resolution, 0.7, len(x)), 1.8, 6.0)
    interp, density, action = [], [], []
    for r in local:
        if r < 3.0:
            interp.append("Side chains often interpretable")
            density.append("strong")
            action.append("Proceed to build and refine")
        elif r < 4.0:
            interp.append("Backbone likely; side chains need review")
            density.append("moderate")
            action.append("Inspect local fit")
        else:
            interp.append("Low-confidence region")
            density.append("weak")
            action.append("Avoid over-interpretation")
    return pd.DataFrame({
        "region": regions,
        "spatial_frequency": x,
        "raw_signal": raw,
        "enhanced_signal": enhanced,
        "confidence_weighted_signal": weighted,
        "local_resolution_A": local,
        "density_class": density,
        "interpretation": interp,
        "recommended_action": action
    })

def generate_unknown_hits():
    data = [
        ("UnknownChain_01", "RSP-like_24", "2.1e-42", 94, 0.91, 0.86, 0.94, "HMM + side-chain density"),
        ("UnknownChain_02", "ATPase_accessory_beta", "7.4e-31", 88, 0.82, 0.80, 0.88, "HMM + AlphaFold overlay"),
        ("UnknownChain_03", "small_coiled_coil_linker", "3.2e-18", 79, 0.73, 0.68, 0.79, "fragment match"),
        ("UnknownChain_04", "RNA_binding_domain_X", "4.6e-08", 61, 0.51, 0.58, 0.61, "weak HMM, check manually"),
        ("UnknownChain_05", "hypothetical_protein_152", "0.018", 42, 0.35, 0.39, 0.42, "low confidence")
    ]
    return pd.DataFrame(data, columns=[
        "chain", "candidate_gene", "hmm_e_value", "hmm_score", "side_chain_support",
        "alphafold_overlay", "combined_score", "evidence_class"
    ])

def generate_validation_metrics(resolution=3.2):
    return pd.DataFrame({
        "metric": [
            "Clashscore", "Ramachandran favoured", "Ramachandran outliers",
            "Rotamer outliers", "Map-model FSC", "Mean Q-score",
            "RNA/DNA base-identity warnings", "Unmodelled density blobs"
        ],
        "demo_value": [
            f"{np.clip(np.random.normal(6 + resolution, 1.1), 2, 18):.1f}",
            f"{np.clip(np.random.normal(94 - max(0,resolution-3)*3, 1.5), 80, 98):.1f}%",
            f"{np.clip(np.random.normal(1.2 + max(0,resolution-3)*0.7, .4), 0, 6):.1f}%",
            f"{np.clip(np.random.normal(3.5 + max(0,resolution-3)*1.4, .8), 0, 12):.1f}%",
            f"{np.clip(np.random.normal(.78 - max(0,resolution-3)*.07, .04), .35, .95):.2f}",
            f"{np.clip(np.random.normal(.68 - max(0,resolution-3)*.06, .04), .25, .92):.2f}",
            str(np.random.randint(4, 28)),
            str(np.random.randint(1, 10)),
        ],
        "interpretation": [
            "Lower is better; inspect severe steric clashes",
            "Higher is better",
            "Lower is better",
            "Lower is better",
            "Higher means better global map fit",
            "Higher means atoms are more resolvable",
            "Manual review recommended",
            "Could indicate ligand, cofactor, lipid, glycan, or noise",
        ]
    })

def generate_domain_table():
    rows = []
    for d in DOMAINS:
        base = {
            "Flexible linker": 0.48, "N-terminal arm": 0.58, "Catalytic core": 0.86,
            "Helical bundle": 0.78, "RNA-binding lobe": 0.70, "C-terminal cap": 0.66
        }[d]
        risk = "High" if base < 0.55 else "Medium" if base < 0.72 else "Low"
        rows.append((d, np.clip(np.random.normal(base, .05), .25, .95), risk, np.random.randint(30, 180)))
    return pd.DataFrame(rows, columns=["domain", "mean_confidence", "risk_level", "residue_count"])

def generate_chain_graph():
    graph_df = pd.DataFrame({
        "source": ["Map QC", "Enhancement", "ModelAngelo", "ModelAngelo", "HMM profiles", "Refinement", "Validation", "Validation"],
        "target": ["Enhancement", "ModelAngelo", "HMM profiles", "Refinement", "Protein ID", "Validation", "Report", "Figure Studio"],
        "evidence": ["local resolution", "sharpened density", "AA probabilities", "initial model", "profile search", "geometry", "warnings", "publication panels"]
    })
    try:
        from streamlit_agraph import Node, Edge
        all_nodes = sorted(set(graph_df["source"]).union(set(graph_df["target"])))
        nodes = [Node(id=n, label=n, size=24) for n in all_nodes]
        edges = [Edge(source=r.source, target=r.target, label=r.evidence) for _, r in graph_df.iterrows()]
    except Exception:
        nodes, edges = [], []
    return nodes, edges, graph_df

def generate_nucleotide_table(resolution=3.2, n=90):
    idx = np.arange(1, n+1)
    backbone = np.clip(np.random.normal(0.82 - max(0,resolution-3)*0.08, 0.08, n), 0.05, 0.98)
    baseid = np.clip(backbone - np.random.uniform(0.05, 0.35, n), 0.02, 0.96)
    status = np.where((backbone > .70) & (baseid > .62), "Reliable",
             np.where(backbone > .55, "Check base identity", "Manual review"))
    bases = np.random.choice(list("AUGC"), n)
    return pd.DataFrame({
        "chain": "RNA1",
        "nucleotide_index": idx,
        "base": bases,
        "backbone_confidence": backbone,
        "base_identity_confidence": baseid,
        "review_status": status
    })

def generate_ligand_table():
    return pd.DataFrame({
        "site": ["Blob_01", "Blob_02", "Blob_03", "Metal_01", "Glycan_01", "Lipid_01"],
        "candidate": ["FAD-like cofactor", "ATP/ADP-like density", "unassigned density", "Mg2+/Mn2+", "N-linked glycan", "membrane lipid tail"],
        "density_support": [0.86, 0.74, 0.38, 0.69, 0.63, 0.57],
        "nearby_residues": ["Gly45, Ser47, Lys89", "Walker-loop-like P-loop", "loop 211-219", "Asp112, Glu149", "Asn301 sequon", "TM helix 3"],
        "assignment_status": ["strong", "moderate", "weak", "moderate", "check", "check"],
        "recommended_action": [
            "Fit cofactor library and validate chemistry",
            "Compare ATP/ADP/GTP density",
            "Do not assign without evidence",
            "Check coordination geometry",
            "Check glycosylation plausibility",
            "Inspect detergent/lipid context"
        ]
    })

def generate_mutation_table():
    variants = ["R45C", "G78D", "K112E", "P167L", "D221N", "Y305F", "R410H", "L512P"]
    classes = ["active-site", "interface", "buried core", "surface", "RNA-binding", "phosphosite", "disease-like", "destabilising"]
    rows = []
    for i, v in enumerate(variants):
        rows.append({
            "chain": np.random.choice(list("ABCD")),
            "residue_index": int(np.random.randint(30, 590)),
            "variant": v,
            "variant_class": classes[i],
            "predicted_impact": float(np.clip(np.random.normal(.55 + i*.04, .15), .05, .98)),
            "confidence": float(np.clip(np.random.normal(.78, .12), .2, .98)),
            "structural_context": np.random.choice(["buried", "surface", "interface", "active-site", "flexible loop"]),
            "action": np.random.choice(["Inspect density", "Check conservation", "Validate experimentally", "Low priority"])
        })
    return pd.DataFrame(rows)

def generate_job_log():
    return """[00:00] Input map detected
[00:02] Map QC complete, local resolution estimated
[00:05] Enhancement plan generated
[00:09] AI model-building plan ready
[00:14] Residue confidence heatmap created
[00:18] Unknown-chain HMM profile search simulated
[00:21] RNA/DNA confidence split complete
[00:24] Ligand/cofactor triage complete
[00:27] Validation warnings generated
[00:30] Report ready for export"""

def demo_pdb_block():
    return """HEADER    DEMO MINI HELIX FOR CRYOMODEL STUDIO AI
ATOM      1  N   ALA A   1      11.104  13.207   9.100  1.00 82.00           N
ATOM      2  CA  ALA A   1      12.560  13.405   9.120  1.00 85.00           C
ATOM      3  C   ALA A   1      13.202  12.307  10.000  1.00 84.00           C
ATOM      4  O   ALA A   1      12.660  11.207  10.120  1.00 83.00           O
ATOM      5  N   GLY A   2      14.390  12.610  10.520  1.00 77.00           N
ATOM      6  CA  GLY A   2      15.140  11.640  11.310  1.00 75.00           C
ATOM      7  C   GLY A   2      16.520  12.140  11.720  1.00 73.00           C
ATOM      8  O   GLY A   2      17.160  12.930  11.020  1.00 72.00           O
ATOM      9  N   LEU A   3      16.980  11.650  12.870  1.00 61.00           N
ATOM     10  CA  LEU A   3      18.280  12.010  13.420  1.00 59.00           C
ATOM     11  C   LEU A   3      19.330  11.010  12.950  1.00 55.00           C
ATOM     12  O   LEU A   3      19.080   9.805  12.890  1.00 52.00           O
END
"""
