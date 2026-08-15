import json
import os
from datetime import datetime, timezone

from generate_panels import generate_panels
from stability_ai import text_to_image, seed
from add_text import add_text_to_panel
from create_strip import create_strip

SCENARIO = """
Characters: Peter is a tall guy with blond hair. Steven is a small guy with black hair.
Peter and Steven walk together in new york when aliens attack the city. They are afraid and try to run for their lives. The army arrive and save them.
"""

STYLE = "american comic, colored"
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print(f"Generate panels with style '{STYLE}' for this scenario: \n {SCENARIO}")

panels = generate_panels(SCENARIO)
with open(os.path.join(OUTPUT_DIR, "panels.json"), "w", encoding="utf-8") as outfile:
    json.dump(panels, outfile, indent=2, ensure_ascii=False)

panel_images = []
manifest = {
    "schema_version": "1.0",
    "created_at": datetime.now(timezone.utc).isoformat(),
    "scenario": SCENARIO.strip(),
    "style": STYLE,
    "provider": "stability-ai",
    "model": "stable-diffusion-xl-1024-v1-0",
    "seed": seed,
    "assets": [],
}

for panel in panels:
    panel_prompt = panel["description"] + ", cartoon box, " + STYLE
    panel_number = panel["number"]
    print(f"Generate panel {panel_number} with prompt: {panel_prompt}")
    panel_image = text_to_image(panel_prompt)
    panel_image_with_text = add_text_to_panel(panel["text"], panel_image)
    output_path = os.path.join(OUTPUT_DIR, f"panel-{panel_number}.png")
    panel_image_with_text.save(output_path)
    panel_images.append(panel_image_with_text)
    manifest["assets"].append({
        "asset_id": f"panel-{panel_number}",
        "panel_number": panel_number,
        "input_description": panel["description"],
        "text": panel["text"],
        "prompt": panel_prompt,
        "path": output_path,
        "status": "generated",
    })

strip_path = os.path.join(OUTPUT_DIR, "strip.png")
create_strip(panel_images).save(strip_path)
manifest["publication"] = {"asset_id": "strip", "path": strip_path, "status": "generated"}

with open(os.path.join(OUTPUT_DIR, "asset-manifest.json"), "w", encoding="utf-8") as manifest_file:
    json.dump(manifest, manifest_file, indent=2, ensure_ascii=False)
