import re

with open('static/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Unify Zone Data Schema
html = html.replace('Zone B4', 'Z-B2')
html = html.replace('Concourse C', 'Z-C2')
html = html.replace('Zone A1', 'Z-A1')
html = html.replace('Zone D3', 'Z-D3')

# 2. Dynamic Heatmap State Rendering - HTML replacement
old_zb2 = """                <!-- Active Monitoring Zone -->
                <div id="zone-B2" class="bg-blue-50 dark:bg-blue-900/40 border-2 border-blue-400 dark:border-blue-600 rounded-xl min-h-[90px] h-auto p-3 flex flex-col items-center justify-center text-center shadow-sm relative overflow-hidden transition-all duration-300 cursor-pointer">
                    <div class="absolute inset-0 bg-blue-400/10 dark:bg-blue-600/10 animate-pulse"></div>
                    <span class="font-bold text-blue-700 dark:text-blue-300 text-lg relative z-10">Z-B2</span>
                    <span class="text-[11px] uppercase font-bold text-blue-600 dark:text-blue-400 mt-1 break-words relative z-10 tracking-widest">Monitoring</span>
                </div>"""
new_zb2 = """                <!-- Normal Zone B2 -->
                <div id="zone-B2" class="bg-white dark:bg-zinc-800 border border-gray-200 dark:border-zinc-700 rounded-xl min-h-[90px] h-auto p-3 flex items-center justify-center font-bold text-gray-500 dark:text-gray-400 shadow-sm transition-all duration-300 cursor-pointer">Z-B2</div>"""
html = html.replace(old_zb2, new_zb2)

old_zc2 = """                <!-- Bottleneck Zone -->
                <div id="zone-C2" class="bg-orange-50 dark:bg-orange-900/40 border-2 border-orange-500 dark:border-orange-600 rounded-xl min-h-[90px] h-auto p-3 flex flex-col items-center justify-center text-center shadow-[0_0_20px_rgba(249,115,22,0.4)] animate-pulse transition-all duration-300 cursor-pointer relative">
                    <span class="font-bold text-orange-700 dark:text-orange-300 text-lg relative z-10">Z-C2</span>
                    <span class="text-[11px] uppercase font-bold text-orange-600 dark:text-orange-400 mt-1 break-words tracking-widest relative z-10">Bottleneck</span>
                </div>"""
new_zc2 = """                <!-- Normal Zone C2 -->
                <div id="zone-C2" class="bg-white dark:bg-zinc-800 border border-gray-200 dark:border-zinc-700 rounded-xl min-h-[90px] h-auto p-3 flex items-center justify-center font-bold text-gray-500 dark:text-gray-400 shadow-sm transition-all duration-300 cursor-pointer">Z-C2</div>"""
html = html.replace(old_zc2, new_zc2)

# Add renderHeatmap JS function and call it
# We will find the global opsState injection from earlier and modify it
old_state = """            // Global Ops State
            const opsState = {
                activeIncident: null,
                activeZone: null,
                activeResource: null
            };"""
new_state = """            // Global Ops State
            const opsState = {
                activeIncident: null,
                activeZone: null,
                activeResource: null,
                confidenceScore: 0.0
            };

            function renderHeatmap() {
                const activeIncidents = Array.from(document.querySelectorAll('#view-ops-room .space-y-4 > div')).map(card => {
                    const zoneSpan = card.querySelector('.text-sm.font-semibold.text-gray-500');
                    if (zoneSpan && !card.classList.contains('hidden')) {
                        return zoneSpan.innerText.trim();
                    }
                    return null;
                }).filter(Boolean);
                
                const zoneCards = document.querySelectorAll('[id^="zone-"]');
                zoneCards.forEach(zone => {
                    const zoneId = zone.id.replace('zone-', 'Z-');
                    
                    // Reset to normal
                    zone.className = 'bg-white dark:bg-zinc-800 border border-gray-200 dark:border-zinc-700 rounded-xl min-h-[90px] h-auto p-3 flex flex-col items-center justify-center font-bold text-gray-500 dark:text-gray-400 shadow-sm transition-all duration-300 cursor-pointer text-center relative overflow-hidden';
                    zone.innerHTML = `<span class="text-lg relative z-10">${zoneId}</span>`;

                    // 1. Alert State (Orange)
                    if (activeIncidents.includes(zoneId)) {
                        zone.className = 'bg-orange-50 dark:bg-orange-900/40 border-2 border-orange-500 dark:border-orange-600 rounded-xl min-h-[90px] h-auto p-3 flex flex-col items-center justify-center text-center shadow-[0_0_20px_rgba(249,115,22,0.4)] animate-pulse transition-all duration-300 cursor-pointer relative';
                        zone.innerHTML = `
                            <span class="font-bold text-orange-700 dark:text-orange-300 text-lg relative z-10">${zoneId}</span>
                            <span class="text-[11px] uppercase font-bold text-orange-600 dark:text-orange-400 mt-1 break-words tracking-widest relative z-10">Alert</span>
                        `;
                    }

                    // 2. Selection State (Blue Monitoring)
                    if (opsState.activeZone === zoneId) {
                        zone.className = 'bg-blue-50 dark:bg-blue-900/40 border-2 border-blue-400 dark:border-blue-600 rounded-xl min-h-[90px] h-auto p-3 flex flex-col items-center justify-center text-center shadow-sm relative overflow-hidden transition-all duration-300 cursor-pointer ring-4 ring-blue-500';
                        zone.innerHTML = `
                            <div class="absolute inset-0 bg-blue-400/10 dark:bg-blue-600/10 animate-pulse"></div>
                            <span class="font-bold text-blue-700 dark:text-blue-300 text-lg relative z-10">${zoneId}</span>
                            <span class="text-[11px] uppercase font-bold text-blue-600 dark:text-blue-400 mt-1 break-words relative z-10 tracking-widest">Monitoring</span>
                        `;
                    }
                });
            }"""
if old_state in html:
    html = html.replace(old_state, new_state)
else:
    print("Could not find old_state")
    exit(1)

# Now we must update zoneCards click listener to call renderHeatmap
old_zone_listener = """            // 2. Zone Selection
            const zoneCards = document.querySelectorAll('[id^="zone-"]');
            zoneCards.forEach(zone => {
                zone.addEventListener('click', () => {
                    opsState.activeZone = zone.id.replace('zone-', 'Z-');
                    zoneCards.forEach(z => z.classList.remove('ring-4', 'ring-orange-500', 'border-orange-500'));
                    zone.classList.add('ring-4', 'ring-orange-500', 'border-orange-500');
                });
            });"""
new_zone_listener = """            // 2. Zone Selection
            const zoneCards = document.querySelectorAll('[id^="zone-"]');
            zoneCards.forEach(zone => {
                zone.addEventListener('click', () => {
                    opsState.activeZone = zone.id.replace('zone-', 'Z-');
                    renderHeatmap();
                });
            });"""
html = html.replace(old_zone_listener, new_zone_listener)

# Inject renderHeatmap on init
init_injection = "            renderHeatmap();\n"
html = html.replace("            // 3. Resource Selection", init_injection + "            // 3. Resource Selection")

# Simulate Inference
old_dispatch = """                const originalText = btnMatch.innerHTML;
                btnMatch.innerHTML = `<span class="material-symbols-outlined text-[16px] animate-spin">refresh</span> DISPATCHING...`;"""

new_dispatch = """                const originalText = btnMatch.innerHTML;
                btnMatch.innerHTML = `<span class="material-symbols-outlined text-[16px] animate-spin">refresh</span> DISPATCHING...`;
                
                opsState.confidenceScore = (Math.random() * (98.9 - 89.0) + 89.0).toFixed(1);
                const confText = document.getElementById('agent-confidence-text');
                if (confText) confText.innerText = opsState.confidenceScore;"""
html = html.replace(old_dispatch, new_dispatch)

with open('static/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Success")
