import re

file_path = "static/index.html"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace c => with cardElement =>
content = re.sub(r'\bc\s*=>\s*c\.', 'cardElement => cardElement.', content)
# Replace z => with zoneElement =>
content = re.sub(r'\bz\s*=>\s*z\.', 'zoneElement => zoneElement.', content)
# Replace r => with resourceRow =>
content = re.sub(r'\br\s*=>\s*r\.', 'resourceRow => resourceRow.', content)

# Check for cleanup phase on unload
if "window.addEventListener('beforeunload" not in content:
    cleanup_code = """
        window.addEventListener('beforeunload', () => {
            if (window.telemetrySyncIntervalId) clearInterval(window.telemetrySyncIntervalId);
            if (window.opsMetricsIntervalId) clearInterval(window.opsMetricsIntervalId);
            if (window.costTrackerIntervalId) clearInterval(window.costTrackerIntervalId);
            if (window.incidentFeedIntervalId) clearInterval(window.incidentFeedIntervalId);
        });
    """
    content = content.replace("</script>", cleanup_code + "\n    </script>")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Refactored more in static/index.html")
