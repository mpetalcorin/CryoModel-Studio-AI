
def build_command_templates(
    map_path,
    fasta_path,
    model_path,
    proteome_path,
    run_enhancement=True,
    run_modelangelo=True,
    run_refinement=True,
    run_protein_id=True,
    run_nucleic=True,
    run_ligands=True,
    run_mutations=True,
):
    cmds = {}
    if run_enhancement:
        cmds["1. Map enhancement"] = f"""# Replace with installed map-enhancement engine.
deepemhancer -i {map_path} -o enhanced_map.mrc

# Optional local-resolution estimation:
phenix.mtriage enhanced_map.mrc"""
    if run_modelangelo:
        cmds["2. ModelAngelo model building"] = f"""model_angelo build \\
  --volume enhanced_map.mrc \\
  --fasta {fasta_path} \\
  --output-dir modelangelo_output \\
  --device 0"""
    if run_protein_id:
        cmds["3. Unknown-protein identification"] = f"""model_angelo build_no_seq \\
  --volume enhanced_map.mrc \\
  --output-dir no_sequence_output \\
  --device 0

model_angelo hmm_search \\
  --input-dir no_sequence_output \\
  --fasta-path {proteome_path} \\
  --output-dir protein_id_results"""
    if run_nucleic:
        cmds["4. RNA/DNA review"] = """# Conceptual module:
# 1. Extract nucleotide chains from ModelAngelo output.
# 2. Score backbone confidence separately from base-identity confidence.
# 3. Cross-check with RNA/DNA secondary-structure constraints."""
    if run_ligands:
        cmds["5. Ligand/cofactor triage"] = """# Conceptual module:
# Search unmodelled density blobs near chemically plausible residues.
# Compare against cofactor, nucleotide, ion, lipid, glycan, and buffer-component libraries."""
    if run_refinement:
        cmds["6. Refinement"] = f"""servalcat refine_spa \\
  --model {model_path} \\
  --map enhanced_map.mrc \\
  --resolution 3.2 \\
  --output refined_model

# Alternative:
phenix.real_space_refine {model_path} enhanced_map.mrc resolution=3.2"""
    if run_mutations:
        cmds["7. Variant overlay"] = """python scripts/export_report.py \\
  --model refined_model.pdb \\
  --map enhanced_map.mrc \\
  --variants variants.csv \\
  --out reports/CryoModel_Studio_AI_report.md"""
    cmds["8. Validation and report"] = """python scripts/export_report.py \\
  --model refined_model.pdb \\
  --map enhanced_map.mrc \\
  --out reports/CryoModel_Studio_AI_report.md"""
    return cmds
