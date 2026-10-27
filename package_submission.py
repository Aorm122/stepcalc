"""Automated submission packager for StepCalc (CMPSC 132 Final Project).

Verifies the test suite, bundles the source code and documentation into a clean ZIP archive
ready for Google Drive upload, excluding cache and temporary files.
"""

import os
import sys
import zipfile
import subprocess
from datetime import datetime

ZIP_FILENAME = "StepCalc_CMPSC132_Final_Project.zip"

INCLUDED_ITEMS = [
    "stepcalc",
    "examples",
    "tests",
    "main.py",
    "requirements.txt",
    "README.md",
]

EXCLUDED_EXTENSIONS = [
    ".pyc",
    ".pyo",
]

EXCLUDED_DIRS = [
    "__pycache__",
    ".pytest_cache",
    ".git",
    ".agents",
]


def run_tests() -> bool:
    """Run pytest suite before packaging."""
    print("Step 1: Running pytest verification suite...")
    result = subprocess.run([sys.executable, "-m", "pytest", "tests"], capture_output=False)
    if result.returncode != 0:
        print("\n[ERROR] Tests failed! Packaging aborted.")
        return False
    print("\n[SUCCESS] All tests passed cleanly.\n")
    return True


def create_zip() -> None:
    """Create the submission ZIP file."""
    print(f"Step 2: Creating submission archive '{ZIP_FILENAME}'...")
    workspace_dir = os.path.dirname(os.path.abspath(__file__))
    zip_path = os.path.join(workspace_dir, ZIP_FILENAME)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for item in INCLUDED_ITEMS:
            full_item_path = os.path.join(workspace_dir, item)
            if not os.path.exists(full_item_path):
                print(f"  [WARN] Missing item: {item}")
                continue

            if os.path.isfile(full_item_path):
                zip_file.write(full_item_path, arcname=item)
                print(f"  + Added file: {item}")
            elif os.path.isdir(full_item_path):
                for root, dirs, files in os.walk(full_item_path):
                    # Filter out excluded directories in-place
                    dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
                    for f in files:
                        if any(f.endswith(ext) for ext in EXCLUDED_EXTENSIONS):
                            continue
                        file_path = os.path.join(root, f)
                        rel_path = os.path.relpath(file_path, workspace_dir)
                        zip_file.write(file_path, arcname=rel_path)
                        print(f"  + Added file: {rel_path}")

    size_kb = os.path.getsize(zip_path) / 1024
    print("\n" + "=" * 60)
    print(f"  SUBMISSION ZIP READY: {ZIP_FILENAME}")
    print(f"  Size: {size_kb:.2f} KB")
    print(f"  Path: {zip_path}")
    print(f"  Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print("Upload this ZIP file to your Google Drive and share the link on MVLE.")


if __name__ == "__main__":
    if run_tests():
        create_zip()
