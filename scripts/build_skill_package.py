#!/usr/bin/env python3
import os
import zipfile
import shutil

def build_package():
    # Base directory is workspace root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir) if os.path.basename(script_dir) == "scripts" else script_dir
    dist_dir = os.path.join(base_dir, "dist")
    os.makedirs(dist_dir, exist_ok=True)
    
    # Define files to include in universal .skill package
    files_map = {
        "SKILL.md": "SKILL.md",
        "README.md": "README.md",
        "manifest-entry.yaml": "manifest-entry.yaml",
        "soul.md": "soul.md",
        "ADAPTER-CONTRACT.md": "ADAPTER-CONTRACT.md",
        "PAL-PROTOCOL.md": "PAL-PROTOCOL.md",
        "scoring.yaml": "scoring.yaml",
        "SCORING.md": "SCORING.md",
        "templates/plan.json": "plan.json",
        "templates/leads.json": "leads.json",
        "templates/crm-preview.json": "crm-preview.template.json",
        "scripts/prospect.py": "prospect.py",
        "scripts/validate_output.py": "validate_output.py",
        "scripts/demo_adapter.py": "demo_adapter.py",
        "tests/cases.yaml": "cases.yaml",
        "tests/tests.md": "tests.md",
        "references/sure-list-contract.md": "prospector-core/references/sure-list-contract.md",
        "references/architecture.md": "docs/ARCHITECTURE_AND_EXPLAINER.md"
    }

    valid_files = {}
    for archive_path, local_rel_path in files_map.items():
        local_abs = os.path.join(base_dir, local_rel_path)
        if os.path.exists(local_abs):
            valid_files[archive_path] = local_abs
        else:
            print(f"Warning: {local_rel_path} not found at {local_abs}")
            
    # Also include extra scripts/evals if available
    extra_dirs = ["prospector-core/evals", "prospector-core/scripts"]
    for ed in extra_dirs:
        ed_abs = os.path.join(base_dir, ed)
        if os.path.exists(ed_abs):
            for root, _, files in os.walk(ed_abs):
                for f in files:
                    if f.endswith(('.py', '.md', '.csv', '.json', '.yaml')) and not f.startswith('.'):
                        full_p = os.path.join(root, f)
                        rel_in_archive = os.path.relpath(full_p, base_dir)
                        valid_files[rel_in_archive] = full_p

    # Build .skill and .zip files
    skill_outputs = [
        os.path.join(base_dir, "signal-to-email-prospecting.skill"),
        os.path.join(base_dir, "prospector-pal.skill"),
        os.path.join(base_dir, "prospector.skill"),
        os.path.join(base_dir, "signal-to-email-prospecting.zip"),
        os.path.join(dist_dir, "signal-to-email-prospecting.skill"),
        os.path.join(dist_dir, "prospector-pal.skill"),
        os.path.join(dist_dir, "prospector.skill")
    ]

    for out_file in skill_outputs:
        with zipfile.ZipFile(out_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for arcname, srcpath in sorted(valid_files.items()):
                zf.write(srcpath, arcname)
        print(f"✅ Created bundle: {os.path.basename(out_file)} ({os.path.getsize(out_file):,} bytes, {len(valid_files)} files)")

if __name__ == "__main__":
    build_package()
