
from datetime import datetime

def build_markdown_report(
    resolution,
    completeness,
    mean_conf,
    mean_q,
    red_flags,
    run_enhancement,
    run_modelangelo,
    run_refinement,
    run_protein_id,
    run_nucleic=True,
    run_ligands=True,
    run_mutations=True,
):
    modules = []
    if run_enhancement:
        modules.append("map enhancement")
    if run_modelangelo:
        modules.append("AI atomic model building")
    if run_protein_id:
        modules.append("unknown-protein identification")
    if run_nucleic:
        modules.append("RNA/DNA checker")
    if run_ligands:
        modules.append("ligand/cofactor triage")
    if run_refinement:
        modules.append("refinement")
    if run_mutations:
        modules.append("variant impact overlay")
    module_text = ", ".join(modules) if modules else "no modules selected"

    return f"""# CryoModel Studio AI Report

Generated: {datetime.now().isoformat(timespec="seconds")}

## Summary

CryoModel Studio AI performed a guided demo workflow including {module_text}.

## Key demo metrics

| Metric | Value |
|---|---:|
| Estimated map resolution | {resolution:.2f} Å |
| Model completeness | {completeness*100:.1f}% |
| Mean residue confidence | {mean_conf:.2f} |
| Mean Q-score | {mean_q:.2f} |
| Residues needing manual review | {red_flags} |

## Interpretation

The model is separated into reliable, check, and manual-review regions. Reliable regions have stronger density, better local Q-score, and better geometry support. Check regions may have a usable backbone but uncertain side chains, loops, nucleotide bases, or homologous-chain assignments. Manual-review regions should not be used for mechanistic interpretation without expert inspection and refinement.

## Added modules

- **Map Doctor:** local resolution, density class, and action recommendation.
- **Enhancement Lab:** denoising/sharpening plan with over-sharpening-risk gauge.
- **AI Build:** residue-level confidence, amino-acid probability explanation, and 3D viewer.
- **Chain Graph:** dependency graph connecting map QC, model building, refinement, validation, and reporting.
- **Unknown Protein Finder:** ranked profile-HMM candidate proteins.
- **RNA/DNA Checker:** separates backbone confidence from base-identity confidence.
- **Ligand/Cofactor Triage:** flags chemically plausible unmodelled density.
- **Variant Overlay:** maps variants onto structure-confidence context.
- **Publication Figure Studio:** generates manuscript panel concepts.

## Recommended next actions

1. Inspect all low-confidence residues in the 3D viewer.
2. Refine the model against the map.
3. Validate stereochemistry, map-model fit, rotamers, clashes, local confidence, and nucleotide identity.
4. For unknown chains, verify ranked HMM/proteome hits using side-chain density and orthogonal biological evidence.
5. For ligand-like density, validate chemistry, coordination, occupancy, and biological plausibility.
6. Export final figures on a white background for manuscript use.

## Caveat

This report was generated from demo-mode simulated values. Real biological conclusions require real cryo-EM maps, sequences, refinement, and validation.
"""
