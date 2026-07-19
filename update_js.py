import re

with open('static/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Fix Forecast Bug
old_forecast = """                    const data = await res.json();
                    document.getElementById('forecast-banner').classList.remove('hidden');
                    document.getElementById('forecast-zone').textContent = data.zone;
                    document.getElementById('forecast-time').textContent = new Date(data.timestamp).toLocaleTimeString();
                    document.getElementById('forecast-message').textContent = `${data.prediction} → ${data.warning}`;
                    document.getElementById('forecast-action').textContent = `Recommended Action: ${data.action_recommended}`;"""

new_forecast = """                    const data = await res.json();
                    if (res.ok && data.zone) {
                        document.getElementById('forecast-banner').classList.remove('hidden');
                        document.getElementById('forecast-zone').textContent = data.zone || 'Unknown Zone';
                        document.getElementById('forecast-time').textContent = data.timestamp ? new Date(data.timestamp).toLocaleTimeString() : '';
                        document.getElementById('forecast-message').textContent = `${data.prediction || ''} → ${data.warning || ''}`;
                        document.getElementById('forecast-action').textContent = `Recommended Action: ${data.action_recommended || ''}`;
                    }"""
html = html.replace(old_forecast, new_forecast)

# Inject Global State and Binding
js_injection = """
            // Global Ops State
            const opsState = {
                activeIncident: null,
                activeZone: null,
                activeResource: null
            };

            // 1. Incident Selection
            const incidentCards = document.querySelectorAll('#view-ops-room .space-y-4 > div');
            incidentCards.forEach((card, index) => {
                if(card.id === 'forecast-banner') return;
                card.classList.add('cursor-pointer');
                card.addEventListener('click', (e) => {
                    if (e.target.closest('button')) return; // ignore button clicks
                    const typeSpan = card.querySelector('.font-label-md.uppercase');
                    if(typeSpan) opsState.activeIncident = typeSpan.innerText;
                    incidentCards.forEach(c => c.classList.remove('ring-2', 'ring-primary', 'bg-blue-50', 'dark:bg-blue-900/20'));
                    card.classList.add('ring-2', 'ring-primary', 'bg-blue-50', 'dark:bg-blue-900/20');
                });
            });

            // 2. Zone Selection
            const zoneCards = document.querySelectorAll('[id^="zone-"]');
            zoneCards.forEach(zone => {
                zone.addEventListener('click', () => {
                    opsState.activeZone = zone.id.replace('zone-', 'Z-');
                    zoneCards.forEach(z => z.classList.remove('ring-4', 'ring-orange-500', 'border-orange-500'));
                    zone.classList.add('ring-4', 'ring-orange-500', 'border-orange-500');
                });
            });

            // 3. Resource Selection
            const resourceRows = document.querySelectorAll('table tbody tr');
            resourceRows.forEach(row => {
                row.classList.add('cursor-pointer');
                row.addEventListener('click', () => {
                    opsState.activeResource = row.cells[0].innerText.trim();
                    resourceRows.forEach(r => r.classList.remove('bg-blue-100', 'dark:bg-blue-900/40'));
                    row.classList.add('bg-blue-100', 'dark:bg-blue-900/40');
                });
            });
"""
# Insert after `tabOps.addEventListener...`
insert_marker = "tabOps.addEventListener('click', () => switchTab(tabOps, tabFan, viewOps, viewFan));"
insert_idx = html.find(insert_marker)
if insert_idx != -1:
    insert_pos = insert_idx + len(insert_marker)
    html = html[:insert_pos] + "\n" + js_injection + html[insert_pos:]
else:
    print("Failed to inject JS state")
    exit(1)

# Modify Dispatch button
old_dispatch = """            // Agentic Match Interaction (/api/v1/dispatch/volunteer)
            btnMatch.addEventListener('click', async () => {
                const originalText = btnMatch.innerHTML;
                btnMatch.innerHTML = `<span class="material-symbols-outlined text-[16px] animate-spin">refresh</span> RUNNING...`;
                
                const statusDot = document.getElementById('agent-status-dot');
                const statusText = document.getElementById('agent-status-text');
                const confText = document.getElementById('agent-confidence-text');
                const actionText = document.getElementById('agent-action-text');
                
                if(statusText) statusText.innerText = "Processing...";
                if(statusDot) statusDot.className = "w-2.5 h-2.5 rounded-full bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.5)] animate-pulse";
                if(actionText) actionText.innerText = "Querying vector store and LLM agent...";
                
                try {
                    const res = await fetch(`${API_BASE}/dispatch/volunteer`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ incident_description: "Medical emergency in Zone B4" })
                    });
                    const data = await res.json();
                    
                    if(statusText) statusText.innerText = data.status || "Completed";
                    if(statusDot) statusDot.className = "w-2.5 h-2.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]";
                    if(confText) confText.innerText = data.confidence_score ? (data.confidence_score * 100).toFixed(1) : "0.0";
                    
                    if(actionText) {
                        actionText.classList.remove('italic', 'text-gray-500', 'dark:text-gray-400');
                        actionText.classList.add('text-gray-900', 'dark:text-gray-100');
                        actionText.innerText = data.recommended_action || "No action recommended.";
                    }
                } catch (err) {
                    if(statusText) statusText.innerText = "Error";
                    if(statusDot) statusDot.className = "w-2.5 h-2.5 rounded-full bg-red-500";
                    if(actionText) actionText.innerText = "Failed to connect to dispatcher.";
                } finally {
                    btnMatch.innerHTML = originalText;
                }
            });"""

new_dispatch = """            // Tactical Dispatch Action
            btnMatch.addEventListener('click', async () => {
                if (!opsState.activeZone || !opsState.activeResource) {
                    alert("Please select a Resource and a Zone first.");
                    return;
                }
                
                const originalText = btnMatch.innerHTML;
                btnMatch.innerHTML = `<span class="material-symbols-outlined text-[16px] animate-spin">refresh</span> DISPATCHING...`;
                
                try {
                    const payload = {
                        resource: opsState.activeResource,
                        zone: opsState.activeZone,
                        incident: opsState.activeIncident
                    };
                    const res = await fetch(`${API_BASE}/ops/dispatch`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                    
                    // Reset UI
                    opsState.activeIncident = null;
                    opsState.activeZone = null;
                    opsState.activeResource = null;
                    
                    document.querySelectorAll('#view-ops-room .space-y-4 > div').forEach(c => c.classList.remove('ring-2', 'ring-primary', 'bg-blue-50', 'dark:bg-blue-900/20'));
                    document.querySelectorAll('[id^="zone-"]').forEach(z => z.classList.remove('ring-4', 'ring-orange-500', 'border-orange-500'));
                    document.querySelectorAll('table tbody tr').forEach(r => r.classList.remove('bg-blue-100', 'dark:bg-blue-900/40'));
                    
                    // Show Notification
                    const actionText = document.getElementById('agent-action-text');
                    const statusDot = document.getElementById('agent-status-dot');
                    const statusText = document.getElementById('agent-status-text');
                    if (actionText) {
                        actionText.classList.remove('italic', 'text-gray-500', 'dark:text-gray-400');
                        actionText.classList.add('text-green-700', 'bg-green-50', 'border-green-200');
                        actionText.innerText = `Success: ${payload.resource} dispatched to Zone ${payload.zone}.`;
                    }
                    if(statusText) statusText.innerText = "Dispatched";
                    if(statusDot) statusDot.className = "w-2.5 h-2.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]";
                    
                    setTimeout(() => {
                        if (actionText) {
                            actionText.classList.add('italic', 'text-gray-500', 'dark:text-gray-400');
                            actionText.classList.remove('text-green-700', 'bg-green-50', 'border-green-200');
                            actionText.innerText = "Awaiting tactical input...";
                        }
                        if(statusText) statusText.innerText = "Idle";
                        if(statusDot) statusDot.className = "w-2.5 h-2.5 rounded-full bg-gray-400 shadow-sm";
                    }, 5000);
                    
                } catch (err) {
                    alert("Failed to dispatch");
                } finally {
                    btnMatch.innerHTML = originalText;
                }
            });"""
if old_dispatch in html:
    html = html.replace(old_dispatch, new_dispatch)
else:
    print("Could not find old_dispatch to replace")
    exit(1)

with open('static/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Success")
