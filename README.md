

# CryoModel Studio AI

**An explainable AI workspace for cryo-EM map enhancement, atomic model building, protein identification, and structure validation.**

CryoModel Studio AI is a visually guided structural-biology app inspired by ModelAngelo-style multimodal model building. It is designed as a portfolio-ready prototype that can run immediately in demo mode and can later be connected to real cryo-EM engines.
<img width="1536" height="1024" alt="CryoModel Studio AI" src="https://github.com/user-attachments/assets/9e1f2299-7a73-4560-96b2-e2584b9afece" />
## New enhanced modules

1. **Map Doctor**: map quality, local resolution, density classification, and recommended actions.
2. **Enhancement Lab**: denoising, sharpening, confidence masking, and over-sharpening risk.
3. **Explainable AI Model Builder**: residue-level confidence landscape, residue inspector, amino-acid probability plot, and 3D molecular viewer.
4. **Chain Graph**: interactive dependency graph for the cryo-EM modelling workflow.
5. **Unknown Protein Finder**: ranked HMM/proteome candidates with evidence radar.
6. **RNA/DNA Checker**: separates backbone confidence from base-identity confidence.
7. **Ligand and Cofactor Density Triage**: flags cofactors, ions, lipids, glycans, and unassigned density.
8. **Variant Impact Overlay**: maps mutations onto structural confidence and biological context.
9. **Validation Dashboard**: Q-score, local resolution, geometry metrics, and manual-review warnings.
10. **Publication Figure Studio**: workflow, confidence heatmap, domain summary, and evidence graphics.
11. **Report Builder**: exports a Markdown report.
12. **Real Workflow Commands**: command templates for future real-engine integration.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate      # macOS/Linux
pip install -r requirements.txt
streamlit run app.py
```

## Push to GitHub

```bash
chmod +x scripts/push_to_github.sh
./scripts/push_to_github.sh
```

Target repository:

```text
https://github.com/mpetalcorin/CryoModel-Studio-AI
```

## Real-engine integration points

The current app runs in safe demo mode. To connect real tools, edit:

- `src/commands.py`
- `src/demo_data.py`
- `scripts/export_report.py`

Suggested integrations:

- ModelAngelo for automated model building and HMM profiles.
- HMMER for proteome search.
- Servalcat or Phenix for refinement and validation.
- DeepEMhancer or EMReady-style preprocessing for map enhancement.
- Mol*, NGL Viewer, or 3Dmol.js for full 3D map/model rendering.

## Scientific rationale

The workflow follows the principle that reliable cryo-EM interpretation should combine map evidence, sequence evidence, structural geometry, confidence scoring, refinement, and expert validation. The app is intentionally explainable: it highlights what the AI thinks is reliable, what needs checking, and what should not yet be interpreted mechanistically.
