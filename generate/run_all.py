
import subprocess
import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent.parent
GENERATE_DIR = PROJECT_DIR / "generate"

SCRIPTS = [
    "get_pokemon.py",
    "get_moves.py",
    "get_abilities.py",
    "get_items.py",
    "get_rulesets.py",
    "get_metagame.py",
]


def main():
    print("=" * 60)
    print("POKEMON CHAMPIONS — DATABASE GENERATION")
    print("=" * 60)

    for script_name in SCRIPTS:
        script_path = GENERATE_DIR / script_name

        if not script_path.is_file():
            print(f"\nERROR: Script not found: {script_path}")
            sys.exit(1)

        print(f"\n{'=' * 60}")
        print(f"Running: {script_name}")
        print("=" * 60)

        try:
            subprocess.run(
                [sys.executable, str(script_path)],
                cwd=PROJECT_DIR,
                check=True,
            )
        except subprocess.CalledProcessError as exc:
            print(f"\nERROR: {script_name} failed with exit code {exc.returncode}.")
            print("Database generation stopped.")
            sys.exit(exc.returncode)

        print(f"\nSUCCESS: {script_name}")

    print("\n" + "=" * 60)
    print("ALL DATABASES GENERATED SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":
    main()
