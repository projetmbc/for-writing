#!/usr/bin/env python3

exit()


from typing import Any, Optional, TypeAlias

from pathlib import Path
import              sys

THIS_DIR = Path(__file__).parent
PROJ_DIR = THIS_DIR.parent

sys.path.append(str(PROJ_DIR / "tools"))

from cbutils.core import *
from cbutils      import *

from shutil import rmtree

import requests
import hashlib


# --------------- #
# -- CONSTANTS -- #
# --------------- #

PaletteCols:TypeAlias = list[[float, float, float]]


PROD_JSON_DIR = PROJ_DIR / "products" / "json"
REPORT_DIR    = PROJ_DIR / "tools" / "REPORT"


PAL_JSON_FILE = PROD_JSON_DIR / "palettes.json"

with PAL_JSON_FILE.open(mode = "r") as f:
    ALL_PALETTES = json_load(f)


PAL_CREDITS_FILE = REPORT_DIR / "PAL-CREDITS.json"

with PAL_CREDITS_FILE.open(mode = "r") as f:
    PAL_CREDITS = json_load(f)



from rich import print
print(PAL_CREDITS)
exit()

# ----------- #
# -- TOOLS -- #
# ----------- #

class PaletteValidator:
    def __init__(self, url: str) -> None:
        self.url            = url
        self.palettes_data  = None
        self.palette_hashes = {}

    def fetch_palettes(self) -> dict[str, PaletteCols]:
        response = requests.get(self.url)
        response.raise_for_status()

        self.palettes_data = response.json()

        return self.palettes_data

    def compute_palette_hash(self, palette: Any) -> str:
        palette_json = json_dumps(
            palette,
            sort_keys    = True,
            ensure_ascii = False
        )

        return hashlib.sha256(
            palette_json.encode('utf-8')
        ).hexdigest()

    def compute_all_hashes(self) -> dict[str, str]:
        if not self.palettes_data:
            print("No palette data loaded. Call fetch_palettes() first.")
            return {}

        self.palette_hashes = {}

        if isinstance(self.palettes_data, dict):
            for palette_name, palette_data in self.palettes_data.items():
                self.palette_hashes[
                    palette_name
                ] = self.compute_palette_hash(palette_data)

        elif isinstance(self.palettes_data, list):
            for i, palette_data in enumerate(self.palettes_data):
                palette_name = palette_data.get(
                    'name',
                    f'palette_{i}'
                )

                self.palette_hashes[
                    palette_name
                ] = self.compute_palette_hash(palette_data)

        return self.palette_hashes

    def validate_changes(
        self,
        previous_hashes: dict[str, str]
    ) -> dict[str, Any]:
        changes = {
            'modified' : [],
            'added'    : [],
            'removed'  : [],
            'unchanged': []
        }

        current_hashes = self.palette_hashes

        for palette_name, current_hash in current_hashes.items():
            if palette_name in previous_hashes:
                if previous_hashes[palette_name] != current_hash:
                    changes['modified'].append(palette_name)

                else:
                    changes['unchanged'].append(palette_name)

            else:
                changes['added'].append(palette_name)

        for palette_name in previous_hashes:
            if palette_name not in current_hashes:
                changes['removed'].append(palette_name)

        return changes

    def save_hashes(
        self,
        filename: str = 'palette_hashes.json'
    ):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(
                self.palette_hashes,
                f,
                indent       = 2,
                ensure_ascii = False
            )

        print(f"Hashes saved to {filename}")

    def load_hashes(
        self,
        filename: str = 'palette_hashes.json'
    ) -> Optional[dict[str, str]]:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json_load(f)

        except FileNotFoundError:
            print(f"File {filename} not found")
            return None

        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            return None

def main():
    # URL of the JSON file (use raw URL)
    url = "https://raw.githubusercontent.com/projetmbc/for-writing/main/%40prism/products/json/palettes.json"

    # Create the validator
    validator = PaletteValidator(url)

    # Download palettes
    print("Downloading palettes...")
    if validator.fetch_palettes():
        print("✓ Palettes downloaded successfully")
    else:
        print("✗ Download failed")
        return

    # Compute hashes
    print("\nComputing hashes...")
    hashes = validator.compute_all_hashes()
    print(f"✓ {len(hashes)} palettes processed")

    # Display hashes
    print("\n=== Palette hashes ===")
    for name, hash_value in hashes.items():
        print(f"{name}: {hash_value[:16]}...")

    # Save hashes
    validator.save_hashes()

    # Example of change validation
    print("\n=== Validation test ===")
    # Load previous hashes (if available)
    previous_hashes = validator.load_hashes()

    if previous_hashes:
        changes = validator.validate_changes(previous_hashes)

        print(f"Modified: {len(changes['modified'])}")
        if changes['modified']:
            print(f"  → {', '.join(changes['modified'])}")

        print(f"Added: {len(changes['added'])}")
        if changes['added']:
            print(f"  → {', '.join(changes['added'])}")

        print(f"Removed: {len(changes['removed'])}")
        if changes['removed']:
            print(f"  → {', '.join(changes['removed'])}")

        print(f"Unchanged: {len(changes['unchanged'])}")
    else:
        print("No previous hashes found. First computation.")


if __name__ == "__main__":
    main()
