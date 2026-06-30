
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

def workflow_sankey():
    labels = [
        "Raw map", "Map QC", "Enhanced map", "ModelAngelo build",
        "Residue confidence", "HMM profiles", "Protein ID",
        "Refinement", "Validation", "Report"
    ]
    source = [0,1,2,3,3,5,3,7,8]
    target = [1,2,3,4,5,6,7,8,9]
    value =  [8,7,7,5,3,3,5,5,6]
    fig = go.Figure(data=[go.Sankey(
        arrangement="snap",
        node=dict(label=labels, pad=18, thickness=18),
        link=dict(source=source, target=target, value=value)
    )])
    fig.update_layout(title_text="End-to-end cryo-EM AI workflow", height=430)
    return fig

def model_quality_gauge(title, value):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=float(value)*100,
        number={"suffix": "%"},
        title={"text": title},
        gauge={"axis": {"range": [0, 100]}}
    ))
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
    return fig

def residue_radar(row):
    labels = ["Confidence", "Q-score", "Resolution support", "Geometry", "Sequence fit"]
    vals = [
        float(row["confidence"]),
        float(row["q_score"]),
        max(0.02, min(1.0, 1.1 - float(row["local_resolution_A"])/5.5)),
        float(np.clip(row["confidence"] + np.random.normal(0.04, .05), .05, .98)),
        float(np.clip(row["q_score"] + np.random.normal(0.02, .06), .05, .98)),
    ]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=vals + [vals[0]], theta=labels + [labels[0]], fill="toself", name="selected residue"))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0,1])), showlegend=False, height=330,
                      title="Explainability radar")
    return fig

def local_resolution_surface(resolution=3.2):
    x = np.linspace(-3, 3, 45)
    y = np.linspace(-3, 3, 45)
    X, Y = np.meshgrid(x, y)
    Z = resolution + 0.45*np.sin(X*1.7)*np.cos(Y*1.3) + 0.28*np.exp(-(X**2+Y**2)/3)
    fig = go.Figure(data=[go.Surface(z=Z, x=X, y=Y, opacity=.92)])
    fig.update_layout(title="Demo local-resolution surface, Å", height=430,
                      scene=dict(xaxis_title="map x", yaxis_title="map y", zaxis_title="Å"))
    return fig

def protein_id_evidence_plot(hits_df):
    categories = ["hmm_score", "side_chain_support", "alphafold_overlay", "combined_score"]
    fig = go.Figure()
    for _, row in hits_df.iterrows():
        vals = [float(row[c]) if c != "hmm_score" else float(row[c])/100 for c in categories]
        fig.add_trace(go.Scatterpolar(
            r=vals + [vals[0]],
            theta=["HMM", "Side-chain", "AF overlay", "Combined", "HMM"],
            fill="toself",
            name=row["candidate_gene"]
        ))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0,1])),
                      title="Unknown-protein evidence radar", height=520)
    return fig
