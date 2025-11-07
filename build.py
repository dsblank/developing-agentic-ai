#!/usr/bin/env python3
"""
Build script for Jupyter Book with custom LaTeX template.
Automatically sets up the custom template before building.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

def setup_template():
    """Copy custom template to build directory."""
    script_dir = Path(__file__).parent
    template_source = script_dir / "templates" / "tex" / "custom"
    template_dest = script_dir / "_build" / "templates" / "tex" / "myst" / "custom_latex_book"
    
    if not template_source.exists():
        print(f"⚠️  Warning: Template source not found at {template_source}")
        return False
    
    print("📋 Copying custom LaTeX template...")
    template_dest.mkdir(parents=True, exist_ok=True)
    
    for file in template_source.glob("*"):
        if file.is_file():
            shutil.copy2(file, template_dest / file.name)
            print(f"   ✓ Copied {file.name}")
    
    return True

def build_book(execute=True, pdf=True, extra_args=None):
    """Build the Jupyter Book."""
    cmd = ["jupyter", "book", "build"]
    
    if execute:
        cmd.append("--execute")
    if pdf:
        cmd.append("--pdf")
    
    if extra_args:
        cmd.extend(extra_args)
    
    print("🔨 Building Jupyter Book...")
    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    return result.returncode == 0

def main():
    """Main entry point."""
    # Parse command line arguments first
    execute = "--no-execute" not in sys.argv
    pdf = "--no-pdf" not in sys.argv
    extra_args = [arg for arg in sys.argv[1:] if not arg.startswith("--no-")]
    
    # Set up template before building
    if not setup_template():
        print("❌ Failed to set up template. Exiting.")
        sys.exit(1)
    
    success = build_book(execute=execute, pdf=pdf, extra_args=extra_args)
    
    if success:
        print("✅ Build complete! PDF available at _build/exports/intro.pdf")
    else:
        print("❌ Build failed. Check the output above for errors.")
        sys.exit(1)

if __name__ == "__main__":
    main()

