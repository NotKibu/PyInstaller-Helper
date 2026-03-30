"""
build.py - PyInstaller helper
Drop this in your project folder and run it to compile any .py file with ease.
"""

import os
import sys
import subprocess
import glob

# ── ANSI colors ──────────────────────────────────────────────────────────────
R  = "\033[0m"
B  = "\033[1m"
C  = "\033[96m"
G  = "\033[92m"
Y  = "\033[93m"
M  = "\033[95m"
RD = "\033[91m"
DIM = "\033[2m"

def clr(text, color): return f"{color}{text}{R}"
def bold(text): return f"{B}{text}{R}"

def banner():
    print()
    print(clr("  ╔═══════════════════════════════════╗", C))
    print(clr("  ║", C) + bold("        PyInstaller Helper         ") + clr("║", C))
    print(clr("  ║", C) + clr("             by Kibu               ", DIM) + clr("║", C))
    print(clr("  ╚═══════════════════════════════════╝", C))
    print()

def ask_yn(prompt, default=True):
    default_hint = "[Y/n]" if default else "[y/N]"
    while True:
        ans = input(clr(f"  {prompt} {default_hint}: ", Y)).strip().lower()
        if ans == "":
            return default
        if ans in ("y", "yes"):
            return True
        if ans in ("n", "no"):
            return False
        print(clr("  → Please enter y or n.", RD))

def ask_choice(prompt, choices):
    print(clr(f"\n  {prompt}", M))
    for i, c in enumerate(choices, 1):
        print(clr(f"    [{i}]", C) + f" {c}")
    while True:
        ans = input(clr(f"  Your choice (1-{len(choices)}): ", Y)).strip()
        if ans.isdigit() and 1 <= int(ans) <= len(choices):
            return int(ans) - 1
        print(clr("  → Invalid choice, try again.", RD))

def ask_text(prompt, default=""):
    hint = f" (default: {default})" if default else ""
    ans = input(clr(f"  {prompt}{hint}: ", Y)).strip()
    return ans if ans else default

def find_py_files():
    """Find all .py files in the current directory, excluding build.py itself."""
    script_name = os.path.basename(__file__)
    files = [
        f for f in glob.glob("*.py")
        if f != script_name
    ]
    return sorted(files)

def detect_icon():
    """Auto-detect a .ico file in the current directory."""
    icons = glob.glob("*.ico")
    if icons:
        return icons[0]
    return None

def detect_version():
    """Auto-detect version.txt in the current directory."""
    if os.path.isfile("version.txt"):
        with open("version.txt", "r") as f:
            ver = f.read().strip().splitlines()[0].strip()
        return ver
    return None

def run_build(cmd):
    print()
    print(clr("  ─────────────────────────────────────────", C))
    print(clr("  Running PyInstaller...", G))
    print(clr("  ─────────────────────────────────────────", C))
    print(clr(f"\n  $ {' '.join(cmd)}\n", DIM))
    result = subprocess.run(cmd)
    print()
    if result.returncode == 0:
        print(clr("  ✅ Build successful! Check the /dist folder.", G))
    else:
        print(clr("  ❌ Build failed. Check the output above for errors.", RD))
    print()

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))  # always run from script dir

    banner()

    # ── Pick target .py file ─────────────────────────────────────────────────
    py_files = find_py_files()

    if not py_files:
        print(clr("  No .py files found in this directory!", RD))
        sys.exit(1)

    if len(py_files) == 1:
        target = py_files[0]
        print(clr(f"  Found script: ", C) + bold(target))
    else:
        idx = ask_choice("Which file do you want to compile?", py_files)
        target = py_files[idx]

    print()
    print(clr(f"  🎯 Target: ", G) + bold(target))

    # ── Auto-detect icon & version ───────────────────────────────────────────
    icon = detect_icon()
    version = detect_version()

    if icon:
        print(clr(f"  🖼  Icon found: ", G) + bold(icon))
    else:
        print(clr(f"  🖼  No .ico file found — building without icon.", DIM))

    if version:
        print(clr(f"  🏷  Version found: ", G) + bold(version))
    else:
        print(clr(f"  🏷  No version.txt found — building without version info.", DIM))

    # ── Options ──────────────────────────────────────────────────────────────
    print()
    print(clr("  ── Build Options ─────────────────────────", C))

    no_console  = ask_yn("Hide console window? (--noconsole)", default=False)
    one_file    = ask_yn("Bundle into a single .exe? (--onefile)", default=True)
    clean_build = ask_yn("Clean previous build cache? (--clean)", default=True)

    # Optional: custom output name
    default_name = os.path.splitext(target)[0]
    custom_name  = ask_text(f"Output name", default=default_name)

    # Optional: extra data files
    print()
    add_data_list = []
    if ask_yn("Add extra data files/folders? (--add-data)", default=False):
        print(clr("  Enter paths one by one. Leave blank to stop.", DIM))
        print(clr("  Format: src;dest  (e.g. assets;assets)", DIM))
        while True:
            entry = input(clr("    data entry: ", Y)).strip()
            if not entry:
                break
            add_data_list.append(entry)

    # Optional: hidden imports
    hidden_imports = []
    if ask_yn("Add hidden imports? (--hidden-import)", default=False):
        print(clr("  Enter module names one by one. Leave blank to stop.", DIM))
        while True:
            entry = input(clr("    module name: ", Y)).strip()
            if not entry:
                break
            hidden_imports.append(entry)

    # ── Assemble command ─────────────────────────────────────────────────────
    cmd = [sys.executable, "-m", "PyInstaller"]

    if one_file:
        cmd.append("--onefile")
    else:
        cmd.append("--onedir")

    if no_console:
        cmd.append("--noconsole")
    else:
        cmd.append("--console")

    if clean_build:
        cmd.append("--clean")

    if icon:
        cmd.extend(["--icon", icon])

    if version:
        cmd.extend(["--version-file", "version.txt"])

    if custom_name != default_name:
        cmd.extend(["--name", custom_name])
    else:
        cmd.extend(["--name", default_name])

    for data in add_data_list:
        cmd.extend(["--add-data", data])

    for imp in hidden_imports:
        cmd.extend(["--hidden-import", imp])

    cmd.append(target)

    # ── Confirm & run ────────────────────────────────────────────────────────
    print()
    print(clr("  ── Summary ───────────────────────────────", C))
    print(clr(f"    Script    : ", DIM) + bold(target))
    print(clr(f"    Output    : ", DIM) + bold(f"{custom_name}.exe"))
    print(clr(f"    One file  : ", DIM) + (clr("yes", G) if one_file else clr("no", Y)))
    print(clr(f"    No console: ", DIM) + (clr("yes", G) if no_console else clr("no", Y)))
    print(clr(f"    Icon      : ", DIM) + (bold(icon) if icon else clr("none", DIM)))
    print(clr(f"    Version   : ", DIM) + (bold(version) if version else clr("none", DIM)))
    if add_data_list:
        print(clr(f"    Data files: ", DIM) + ", ".join(add_data_list))
    if hidden_imports:
        print(clr(f"    Hidden imp: ", DIM) + ", ".join(hidden_imports))

    print()
    if ask_yn("Looks good? Start the build?", default=True):
        run_build(cmd)
    else:
        print(clr("\n  Build cancelled. No files were changed.\n", Y))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(clr("\n\n  Interrupted. Bye! 👋\n", Y))
