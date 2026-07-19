import re

file_path = "static/index.html"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.content = f.read()

# 1. Variable Renaming
content = re.sub(r'\bres\b', 'apiResponsePayload', content)
content = re.sub(r'\berr\b', 'errorResponse', content)
content = re.sub(r'\bsimConf\b', 'simulationConfidenceScore', content)
content = re.sub(r'\b(catch\s*\(\s*)e(\s*\))\b', r'\1errorResponse\2', content)
content = re.sub(r'console\.error\([\'"].*?[\'"],\s*e\);', 'console.error("Error:", errorResponse);', content)
content = re.sub(r'console\.error\(\s*e\s*\);', 'console.error(errorResponse);', content)
content = re.sub(r'\.catch\(\s*e\s*=>', '.catch(errorResponse =>', content)
content = re.sub(r'\b(async\s*\(|function\s*\(|\()\s*e\s*(\))', r'\1clickEvent\2', content)
content = re.sub(r'\be\.preventDefault', 'clickEvent.preventDefault', content)
content = re.sub(r'\be\.stopPropagation', 'clickEvent.stopPropagation', content)
content = re.sub(r'\be\.target', 'clickEvent.target', content)
content = re.sub(r'\be\.key', 'clickEvent.key', content)

# 2. Add try-catch resilience to fetch blocks where it might be missing or empty.
# In the previous code, there was a block in btnSimulate:
# (btnSimulate actually doesn't have a fetch, it's just timeout based)

# 3. Handle intervals and cleanups.
# Find `setInterval(` and prepend `window.telemetrySyncIntervalId = setInterval(`
# Actually, I'll search for specific intervals.
content = re.sub(r'setInterval\(async\s*\(\)\s*=>\s*\{\s*const\s*viewOps', 'window.opsMetricsIntervalId = setInterval(async () => {\n                const viewOps', content)
content = re.sub(r'setInterval\(async\s*\(\)\s*=>\s*\{\s*try\s*\{\s*const\s*apiResponsePayload\s*=\s*await\s*fetch\(\`\$\{API_BASE\}\/cost-tracker', 'window.costTrackerIntervalId = setInterval(async () => {\n                try {\n                    const apiResponsePayload = await fetch(`${API_BASE}/cost-tracker', content)

# 4. Remove dead code / Code Graveyards
# Remove `// Feature 3: Heatmap Dynamics in Auto Forecasting Fetch Logic` and its duplicate code if it exists.
# There is a block starting with `// Feature 3: Heatmap Dynamics` and we can just leave it as it's active UI code, but remove `// e.g. "Z-B2" -> "zone-B4"`
content = re.sub(r'// e\.g\. "Z-B2" -> "zone-B4"\n', '', content)

# Let's save the file back
with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Refactored static/index.html")
