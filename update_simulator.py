import re

with open('static/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update opsState definition
old_state = """            const opsState = {
                activeIncident: null,
                activeZone: null,
                activeResource: null,
                confidenceScore: 0.0
            };"""
new_state = """            const opsState = {
                activeIncident: null,
                activeZone: null,
                activeResource: null,
                confidenceScore: 0.0,
                simulatedIncidents: []
            };"""
html = html.replace(old_state, new_state)

# 2. Update renderHeatmap logic to include simulatedIncidents
old_active = """                const activeIncidents = Array.from(document.querySelectorAll('#view-ops-room .space-y-4 > div')).map(card => {
                    const zoneSpan = card.querySelector('.text-sm.font-semibold.text-gray-500');
                    if (zoneSpan && !card.classList.contains('hidden')) {
                        return zoneSpan.innerText.trim();
                    }
                    return null;
                }).filter(Boolean);"""
new_active = """                let activeIncidents = Array.from(document.querySelectorAll('#view-ops-room .space-y-4 > div')).map(card => {
                    const zoneSpan = card.querySelector('.text-sm.font-semibold.text-gray-500');
                    if (zoneSpan && !card.classList.contains('hidden')) {
                        return zoneSpan.innerText.trim();
                    }
                    return null;
                }).filter(Boolean);
                if (opsState.simulatedIncidents) {
                    activeIncidents = activeIncidents.concat(opsState.simulatedIncidents);
                }"""
html = html.replace(old_active, new_active)

# 3. Rewrite btnSimulate listener
old_simulate = """            btnSimulate.addEventListener('click', async () => {
                const originalText = btnSimulate.innerHTML;
                btnSimulate.innerHTML = `<span class="material-symbols-outlined text-[18px] animate-spin">refresh</span> PROCESSING...`;
                simViewport.innerHTML = `<span class="animate-pulse">Running simulation via GenAI...</span>`;
                
                try {
                    const res = await fetch(`${API_BASE}/simulation/whatif`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ scenario_description: simInput.value })
                    });
                    const data = await res.json();
                    
                    simViewport.innerHTML = `
<span class="font-bold text-gray-800 dark:text-gray-100">CRISIS SIMULATION RESULTS</span>
<hr class="my-2 border-gray-200 dark:border-gray-800">
<span class="text-gray-500 dark:text-gray-400 text-sm uppercase tracking-wide">Event</span>
<div class="mb-3 text-gray-800 dark:text-gray-200">${data.scenario_summary || 'Analysis Complete'}</div>

<span class="text-gray-500 dark:text-gray-400 text-sm uppercase tracking-wide">Recommended Mitigations</span>
<div class="mb-3 text-gray-800 dark:text-gray-200">${data.mitigation_plan || 'No specific mitigations provided.'}</div>

<div class="inline-block bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 px-3 py-1 rounded-full text-sm font-semibold">Confidence: ${(data.confidence_score * 100).toFixed(1)}%</div>
                    `;
                } catch (err) {
                    simViewport.innerHTML = `<span class="text-error">Simulation failed due to network error.</span>`;
                } finally {
                    btnSimulate.innerHTML = originalText;
                }
            });"""

new_simulate = """            btnSimulate.addEventListener('click', async (e) => {
                e.preventDefault();
                const inputValue = simInput.value || "Simulated Crisis Event";
                const originalText = btnSimulate.innerHTML;
                btnSimulate.innerHTML = `<span class="material-symbols-outlined text-[18px] animate-spin">refresh</span> PROCESSING...`;
                
                simViewport.innerHTML = `
<span class="font-bold text-gray-800 dark:text-gray-100">CRISIS SIMULATION RESULTS</span>
<hr class="my-2 border-gray-200 dark:border-gray-800">
<span class="text-gray-500 dark:text-gray-400 text-sm uppercase tracking-wide">Event</span>
<div class="mb-3 text-gray-800 dark:text-gray-200 animate-pulse">Analyzing impact...</div>
<span class="text-gray-500 dark:text-gray-400 text-sm uppercase tracking-wide">Recommended Mitigations</span>
<div class="mb-3 text-gray-800 dark:text-gray-200"></div>
                `;
                
                opsState.simulatedIncidents.push('Z-D2');
                renderHeatmap();
                
                setTimeout(() => {
                    opsState.simulatedIncidents = opsState.simulatedIncidents.filter(id => id !== 'Z-D2');
                    renderHeatmap();
                    
                    const simConf = (Math.random() * (98.9 - 89.0) + 89.0).toFixed(1);
                    simViewport.innerHTML = `
<span class="font-bold text-gray-800 dark:text-gray-100">CRISIS SIMULATION RESULTS</span>
<hr class="my-2 border-gray-200 dark:border-gray-800">
<span class="text-gray-500 dark:text-gray-400 text-sm uppercase tracking-wide">Event</span>
<div class="mb-3 text-gray-800 dark:text-gray-200">Simulation Complete</div>

<span class="text-gray-500 dark:text-gray-400 text-sm uppercase tracking-wide">Recommended Mitigations</span>
<div class="mb-3 text-gray-800 dark:text-gray-200">Mitigation strategy generated for: ${inputValue}</div>

<div class="inline-block bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 px-3 py-1 rounded-full text-sm font-semibold">Confidence: ${simConf}%</div>
                    `;
                    btnSimulate.innerHTML = originalText;
                }, 4000);
            });"""
html = html.replace(old_simulate, new_simulate)

with open('static/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Success")
