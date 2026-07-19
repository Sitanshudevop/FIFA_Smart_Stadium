import re

with open('static/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

def extract_div(content, start_marker):
    start_idx = content.find(start_marker)
    if start_idx == -1: return None, content
    div_start = content.find('<div', start_idx)
    count = 0
    i = div_start
    end_idx = -1
    while i < len(content):
        if content.startswith('<div', i): count += 1
        elif content.startswith('</div', i):
            count -= 1
            if count == 0:
                end_idx = i + 6
                break
        i += 1
    if end_idx != -1:
        extracted = content[start_idx:end_idx]
        new_content = content[:start_idx] + content[end_idx:]
        return extracted, new_content
    return None, content

stream, html = extract_div(html, '<!-- Live Incident Stream -->')
dispatcher, html = extract_div(html, '<!-- Resource Dispatcher -->')
heatmap, html = extract_div(html, '<!-- Zone Anomaly Heatmap -->')

if not (stream and dispatcher and heatmap):
    print("Failed to extract")
    exit(1)

# Remove old grid span classes
stream = re.sub(r'lg:col-span-\d+', '', stream)
dispatcher = re.sub(r'col-span-\d+\s+lg:col-span-\d+', '', dispatcher)
heatmap = re.sub(r'lg:col-span-\d+', '', heatmap)

# Create a new container
new_container = f'''
        <!-- Unified Side-by-Side Layout -->
        <div class="col-span-1 lg:col-span-3 grid grid-cols-1 xl:grid-cols-3 gap-6 w-full">
            {{stream}}
            {{heatmap}}
            {{dispatcher}}
        </div>
'''
new_container = new_container.replace('{stream}', stream).replace('{heatmap}', heatmap).replace('{dispatcher}', dispatcher)

insert_marker = '<!-- Fluid Responsive Grid -->\n<div class="grid grid-cols-1 lg:grid-cols-3 gap-6 w-full">\n'
insert_idx = html.find(insert_marker)
if insert_idx != -1:
    insert_pos = insert_idx + len(insert_marker)
    html = html[:insert_pos] + new_container + html[insert_pos:]
    with open('static/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Success")
else:
    print("Failed to find insert marker")
    exit(1)
