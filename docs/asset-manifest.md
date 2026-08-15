# Asset Manifest Contract

The generator writes \`output/asset-manifest.json\` for every run.

Required fields:
- \`schema_version\`
- \`created_at\`
- \`scenario\`
- \`style\`
- \`provider\`
- \`model\`
- \`seed\`
- \`assets\`
- \`publication\`

Each asset records its panel number, source description, dialogue text, final prompt, output path, and generation status. This makes a run reproducible and allows later continuity, review, or publishing tools to identify exactly which source produced each image.
