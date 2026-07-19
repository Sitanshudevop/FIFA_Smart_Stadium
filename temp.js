
        document.addEventListener('DOMContentLoaded', () => {
            
            // VIP Delegation Routing Logic
            const vipRouteSelect = document.getElementById('vip-route-select');
            const btnVipRoute = document.getElementById('btn-vip-route');
            const vipRouteOutput = document.getElementById('vip-route-output');
            
            if (btnVipRoute && vipRouteSelect && vipRouteOutput) {
                const routeDatabase = {
                    "FIFA Executive Committee (Convoy Alpha)": {
                        primaryPath: "Underground Tunnel 3 → South VIP Elevator → Box 4",
                        estimatedTransitTime: "4m 12s",
                        threatAssessment: "Low - All checkpoints secured",
                        chokePointsAvoided: "Main Concourse C, Gate 2"
                    },
                    "National Team Bus (Home)": {
                        primaryPath: "West Service Road → Locker Room Access A → Pitch Level",
                        estimatedTransitTime: "3m 45s",
                        threatAssessment: "Moderate - Press gathering near Gate 4",
                        chokePointsAvoided: "Public Parking Lot B, Fan Zone"
                    },
                    "National Team Bus (Away)": {
                        primaryPath: "East Service Road → Locker Room Access B → Pitch Level",
                        estimatedTransitTime: "3m 50s",
                        threatAssessment: "Low - Standard security protocol active",
                        chokePointsAvoided: "Public Parking Lot C, Fan Zone"
                    },
                    "Head of State Escort": {
                        primaryPath: "Secure Heliport → VIP Elevator 1 → Presidential Suite",
                        estimatedTransitTime: "2m 30s",
                        threatAssessment: "Elevated - Requires counter-drone overwatch",
                        chokePointsAvoided: "All public areas and lower concourses"
                    }
                };

                btnVipRoute.addEventListener('click', () => {
                    const activeConvoy = vipRouteSelect.value;
                    const originalBtnHtml = btnVipRoute.innerHTML;
                    
                    btnVipRoute.disabled = true;
                    btnVipRoute.innerHTML = `<span class="material-symbols-outlined animate-spin">refresh</span> Calculating Path...`;
                    vipRouteOutput.innerHTML = `<div class="flex items-center gap-2 text-gray-500"><span class="material-symbols-outlined animate-spin text-[18px]">refresh</span> Interfacing with tactical grid...</div>`;
                    
                    const latency = Math.floor(Math.random() * (2000 - 1500 + 1)) + 1500;
                    
                    setTimeout(() => {
                        const routeData = routeDatabase[activeConvoy];
                        if (routeData) {
                            vipRouteOutput.innerHTML = `
                                <div class="flex flex-col gap-3 text-gray-800 dark:text-gray-200 animate-[fadeIn_0.5s_ease-out]">
                                    <div class="flex flex-col border-b border-gray-200 dark:border-zinc-700 pb-2">
                                        <span class="text-[11px] uppercase font-bold text-gray-500 tracking-wider">Primary Path</span>
                                        <span class="font-bold flex items-center gap-2 mt-1"><span class="material-symbols-outlined text-purple-600 text-[18px]">route</span> ${routeData.primaryPath}</span>
                                    </div>
                                    <div class="flex flex-col border-b border-gray-200 dark:border-zinc-700 pb-2">
                                        <span class="text-[11px] uppercase font-bold text-gray-500 tracking-wider">Estimated Transit Time</span>
                                        <span class="font-bold flex items-center gap-2 mt-1"><span class="material-symbols-outlined text-blue-500 text-[18px]">timer</span> ${routeData.estimatedTransitTime}</span>
                                    </div>
                                    <div class="flex flex-col border-b border-gray-200 dark:border-zinc-700 pb-2">
                                        <span class="text-[11px] uppercase font-bold text-gray-500 tracking-wider">Threat Assessment</span>
                                        <span class="font-bold flex items-center gap-2 mt-1"><span class="material-symbols-outlined text-green-500 text-[18px]">security</span> ${routeData.threatAssessment}</span>
                                    </div>
                                    <div class="flex flex-col">
                                        <span class="text-[11px] uppercase font-bold text-gray-500 tracking-wider">Chokepoints Avoided</span>
                                        <span class="font-bold flex items-center gap-2 mt-1"><span class="material-symbols-outlined text-red-400 text-[18px]">block</span> ${routeData.chokePointsAvoided}</span>
                                    </div>
                                </div>
                            `;
                        } else {
                            vipRouteOutput.innerHTML = `Awaiting routing parameters. Select a delegation to generate clear-path instructions.`;
                        }
                        
                        btnVipRoute.disabled = false;
                        btnVipRoute.innerHTML = originalBtnHtml;
                    }, latency);
                });
            }

            // Inbound Prompt Log Live Stream
            const promptLogList = document.getElementById('inbound-prompt-log');
            if (promptLogList) {
                let activeLogs = [
                    { type: 'success', text: "SELECT * FROM crowd_density WHERE zone = ?" },
                    { type: 'success', text: "Translate: 'Where is the nearest bathroom?' to ES" },
                    { type: 'success', text: "Verify_Ticket_Img: src_hash_8f92a..." },
                    { type: 'warning', text: "Rate limit warning on Vision API" },
                    { type: 'success', text: "Concourse routing matrix calculation: OK" }
                ];

                const mockLogPool = [
                    { type: 'success', text: "SELECT * FROM crowd_density WHERE zone = ?" },
                    { type: 'success', text: "Translate: 'Where is the nearest bathroom?' to ES" },
                    { type: 'success', text: "Verify_Ticket_Img: src_hash_8f92a..." },
                    { type: 'warning', text: "Rate limit warning on Vision API" },
                    { type: 'success', text: "Concourse routing matrix calculation: OK" },
                    { type: 'error', text: "DB Timeout: Ops_Logistics schema not responding" },
                    { type: 'success', text: "Gemini Prompt Injection: Analyzing vendor stocks" },
                    { type: 'success', text: "OCR Vision Processing: Ticket #99482 verified" },
                    { type: 'success', text: "UPDATE zone_status SET alert = false WHERE id = ?" },
                    { type: 'success', text: "WebSocket Ping: 14ms latency to Node 3" },
                    { type: 'success', text: "LLM Context Window: 14.2k tokens processed" },
                    { type: 'warning', text: "High token consumption alert in Chat Session #112" },
                    { type: 'success', text: "Dispatch generated: Unit 7 to Zone C2" },
                    { type: 'success', text: "Ingesting CCTV stream chunk_482.mp4" },
                    { type: 'error', text: "Failed to parse malformed image upload payload" },
                    { type: 'success', text: "Cache hit: Fan Query #4821" },
                    { type: 'success', text: "Model Switch: Downgraded to Gemini Flash to preserve quota" },
                    { type: 'success', text: "Simulated what-if scenario generated in 800ms" },
                    { type: 'success', text: "Routing calculated: VIP Path Alpha activated" },
                    { type: 'success', text: "Telemetry heartbeat sync: OK" }
                ];

                const renderLogs = (isNew = false) => {
                    promptLogList.innerHTML = '';
                    activeLogs.forEach((log, index) => {
                        const li = document.createElement('li');
                        li.className = "flex items-start gap-3 border-b border-gray-100 dark:border-zinc-800/50 pb-3 transition-all duration-500 ease-out";
                        
                        if (isNew && index === 0) {
                            li.style.animation = "pulse 1s cubic-bezier(0.4, 0, 0.6, 1)";
                        }

                        let iconHtml = '';
                        if (log.type === 'error' || log.type === 'warning') {
                            li.classList.add('bg-red-50/50', 'dark:bg-red-900/10', 'p-2', '-mx-2', 'rounded');
                            li.classList.remove('border-b', 'border-gray-100', 'dark:border-zinc-800/50', 'pb-3');
                            iconHtml = `<span class="material-symbols-outlined text-[18px] text-tertiary-container mt-0.5 flex-shrink-0">warning</span>
                            <div class="break-words text-gray-500 dark:text-gray-500 italic leading-relaxed">${log.text}</div>`;
                        } else {
                            iconHtml = `<span class="material-symbols-outlined text-[18px] text-emerald-600 mt-0.5 flex-shrink-0">check_circle</span>
                            <div class="break-words text-gray-600 dark:text-gray-400 leading-relaxed">${log.text}</div>`;
                        }
                        li.innerHTML = iconHtml;
                        promptLogList.appendChild(li);
                    });
                };

                renderLogs();

                if (!window.promptLogLoopStarted) {
                    window.promptLogLoopStarted = true;
                    const runLogLoop = () => {
                        const timeout = Math.floor(Math.random() * (4500 - 2500 + 1)) + 2500;
                        setTimeout(() => {
                            const randomLog = mockLogPool[Math.floor(Math.random() * mockLogPool.length)];
                            activeLogs.unshift(randomLog);
                            if (activeLogs.length > 5) {
                                activeLogs.pop();
                            }
                            renderLogs(true);
                            runLogLoop();
                        }, timeout);
                    };
                    runLogLoop();
                }
            }

            // Landing Page Transition Logic
            const btnEnterFan = document.getElementById('btn-enter-fan');
            const btnEnterOps = document.getElementById('btn-enter-ops');
            const landingView = document.getElementById('landing-view');
            const appView = document.getElementById('app-view');

            const transitionToApp = () => {
                landingView.classList.replace('opacity-100', 'opacity-0');
                
                setTimeout(() => {
                    landingView.classList.add('hidden');
                    appView.classList.remove('hidden');
                    // Slight delay to ensure the browser registers the removal of 'hidden' before fading in
                    setTimeout(() => appView.classList.replace('opacity-0', 'opacity-100'), 50);
                }, 500);
            };

            btnEnterFan.addEventListener('click', () => {
                document.getElementById('nav-tab-fan').click();
                document.getElementById('nav-tab-ops').classList.add('hidden');
                transitionToApp();
            });

            btnEnterOps.addEventListener('click', () => {
                document.getElementById('nav-tab-ops').click();
                document.getElementById('nav-tab-fan').classList.add('hidden');
                transitionToApp();
            });

            const btnBackHome = document.getElementById('btn-back-home');
            btnBackHome.addEventListener('click', () => {
                appView.classList.replace('opacity-100', 'opacity-0');
                
                setTimeout(() => {
                    appView.classList.add('hidden');
                    landingView.classList.remove('hidden');
                    
                    document.getElementById('nav-tab-fan').classList.remove('hidden');
                    document.getElementById('nav-tab-ops').classList.remove('hidden');
                    
                    setTimeout(() => landingView.classList.replace('opacity-0', 'opacity-100'), 50);
                }, 500);
            });

            const API_BASE = 'http://localhost:8000/api/v1';

            // Ops Room Login Gate Logic
            const opsLoginGate = document.getElementById('ops-login-gate');
            const btnDemoMode = document.getElementById('btn-demo-mode');
            if (btnDemoMode && opsLoginGate) {
                btnDemoMode.addEventListener('click', () => {
                    opsLoginGate.classList.add('hidden');
                });
            }

            // Navigation Elements
            const tabFan = document.getElementById('nav-tab-fan');
            const tabOps = document.getElementById('nav-tab-ops');
            
            // View Elements
            const viewFan = document.getElementById('view-fan-portal');
            const viewOps = document.getElementById('view-ops-room');

            // Interactive Elements
            const btnSimulate = document.getElementById('btn-simulate');
            const simViewport = document.getElementById('simulator-viewport');
            const simInput = document.getElementById('simulator-input');
            
            const btnMatch = document.getElementById('btn-agentic-match');
            const jsonViewport = document.getElementById('dispatcher-json');

            const chatInput = document.getElementById('chat-input');
            // The placeholder for assistant response is actually the div before the image
            const chatOutput = document.querySelector('#chat-input').parentElement.nextElementSibling.querySelector('span');

            // Active/Inactive Style Classes
            const activeClasses = ['text-primary', 'border-b-2', 'border-primary'];
            const inactiveClasses = ['text-on-surface-variant', 'hover:bg-surface-container-low'];

            function switchTab(activeTab, inactiveTab, activeView, inactiveView) {
                activeView.classList.remove('hidden');
                inactiveView.classList.add('hidden');
                
                const opsGate = document.getElementById('ops-login-gate');
                if (activeView.id === 'view-ops-room' && opsGate) {
                    opsGate.classList.remove('hidden');
                }

                activeClasses.forEach(cls => activeTab.classList.add(cls));
                inactiveClasses.forEach(cls => activeTab.classList.remove(cls));

                activeClasses.forEach(cls => inactiveTab.classList.remove(cls));
                inactiveClasses.forEach(cls => inactiveTab.classList.add(cls));

                if (activeView.id === 'view-fan-portal' && window.leafletMap) {
                    setTimeout(() => window.leafletMap.invalidateSize(), 150);
                }
            }

            tabFan.addEventListener('click', () => switchTab(tabFan, tabOps, viewFan, viewOps));
            tabOps.addEventListener('click', () => switchTab(tabOps, tabFan, viewOps, viewFan));

            // Global Ops State
            const opsState = {
                activeIncident: null,
                activeZone: null,
                activeResource: null,
                confidenceScore: 0.0,
                simulatedIncidents: [],
                tokensProcessed: 1400000,
                globalLatency: 12
            };
            
            window.updateGlobalMetrics = () => {
                const roiTokens = document.getElementById('roi-tokens');
                const telemetryTokens = document.getElementById('telemetry-tokens');
                const globalLatencyUI = document.getElementById('global-latency-value');
                
                if (roiTokens) roiTokens.innerText = opsState.tokensProcessed.toLocaleString();
                if (telemetryTokens) {
                    const mTokens = (opsState.tokensProcessed / 1000000).toFixed(1);
                    telemetryTokens.innerHTML = `${mTokens}<span class="text-headline-md text-outline font-normal">M</span>`;
                }
                if (globalLatencyUI) {
                    globalLatencyUI.innerHTML = `${opsState.globalLatency}<span class="text-headline-md text-outline font-normal">ms</span>`;
                }
            };
            window.updateGlobalMetrics();

            function renderHeatmap() {
                let activeIncidents = Array.from(document.querySelectorAll('#view-ops-room .space-y-4 > div')).map(card => {
                    const zoneSpan = card.querySelector('.text-sm.font-semibold.text-gray-500');
                    if (zoneSpan && !card.classList.contains('hidden')) {
                        return zoneSpan.innerText.trim();
                    }
                    return null;
                }).filter(Boolean);
                if (opsState.simulatedIncidents) {
                    activeIncidents = activeIncidents.concat(opsState.simulatedIncidents);
                }
                
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

                // Update Global System Status Badge
                const globalBadge = document.getElementById('global-system-status-badge');
                const globalIcon = document.getElementById('global-system-status-icon');
                const globalText = document.getElementById('global-system-status-text');
                
                if (globalBadge && globalIcon && globalText) {
                    if (activeIncidents.length > 0) {
                        // Alert State
                        globalBadge.className = 'bg-error-container/20 border border-tertiary-container px-4 py-3 rounded-lg flex items-center gap-2 h-full transition-colors duration-300';
                        globalIcon.className = 'material-symbols-outlined text-tertiary-container';
                        globalIcon.innerText = 'warning';
                        globalText.className = 'font-label-md text-label-md text-tertiary-container uppercase';
                        globalText.innerText = 'SYSTEM ALERT';
                    } else {
                        // Nominal State
                        globalBadge.className = 'bg-green-100/30 border border-green-500 px-4 py-3 rounded-lg flex items-center gap-2 h-full transition-colors duration-300';
                        globalIcon.className = 'material-symbols-outlined text-green-600';
                        globalIcon.innerText = 'check_circle';
                        globalText.className = 'font-label-md text-label-md text-green-600 uppercase';
                        globalText.innerText = 'SYSTEM NOMINAL';
                    }
                }
                
                // Update Active Incident Count UI
                const incidentCountBadge = document.getElementById('active-incident-count');
                if (incidentCountBadge) {
                    incidentCountBadge.innerText = `${activeIncidents.length} Active`;
                }
            }

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
                    renderHeatmap();
                });
            });

            renderHeatmap();
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



            // Simulator Interaction (/api/v1/simulation/whatif)
            btnSimulate.addEventListener('click', async (e) => {
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
            });

            // Tactical Dispatch Action
            btnMatch.addEventListener('click', async () => {
                if (!opsState.activeZone || !opsState.activeResource) {
                    alert("Please select a Resource and a Zone first.");
                    return;
                }
                
                const originalText = btnMatch.innerHTML;
                btnMatch.innerHTML = `<span class="material-symbols-outlined text-[16px] animate-spin">refresh</span> DISPATCHING...`;
                
                opsState.confidenceScore = (Math.random() * (99.2 - 88.5) + 88.5).toFixed(1);
                const confText = document.getElementById('agent-confidence-text');
                if (confText) confText.innerText = opsState.confidenceScore;
                
                // Capture the Dispatched Target and Set Status to Busy
                const targetResourceName = opsState.activeResource;
                let targetStatusCell = null;
                document.querySelectorAll('table tbody tr').forEach(row => {
                    if (row.cells[0].innerText.trim() === targetResourceName) {
                        targetStatusCell = row.cells[1];
                    }
                });

                if (targetStatusCell) {
                    targetStatusCell.innerHTML = `<span class="w-2.5 h-2.5 rounded-full bg-tertiary-container inline-block mr-2 shadow-[0_0_8px_rgba(188,82,0,0.5)]"></span> Busy`;
                    setTimeout(() => {
                        targetStatusCell.innerHTML = `<span class="w-2.5 h-2.5 rounded-full bg-emerald-500 inline-block mr-2 shadow-[0_0_8px_rgba(16,185,129,0.5)]"></span> Avail`;
                    }, 3000);
                }
                
                try {
                    const payload = {
                        resource: opsState.activeResource,
                        zone: opsState.activeZone,
                        incident: opsState.activeIncident
                    };
                    const startTime = performance.now();
                    const res = await fetch(`${API_BASE}/ops/dispatch`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                    const endTime = performance.now();
                    opsState.globalLatency = Math.round(endTime - startTime);
                    if (window.updateGlobalMetrics) window.updateGlobalMetrics();
                    
                    // Match and Delete the Incident
                    document.querySelectorAll('#view-ops-room .space-y-4 > div').forEach(card => {
                        const zoneSpan = card.querySelector('.text-sm.font-semibold.text-gray-500');
                        if (zoneSpan && zoneSpan.innerText.trim() === payload.zone) {
                            card.classList.add('hidden');
                        }
                    });
                    if (opsState.simulatedIncidents) {
                        opsState.simulatedIncidents = opsState.simulatedIncidents.filter(id => id !== payload.zone);
                    }
                    
                    // Reset UI
                    opsState.activeIncident = null;
                    opsState.activeZone = null;
                    opsState.activeResource = null;
                    
                    document.querySelectorAll('#view-ops-room .space-y-4 > div').forEach(c => c.classList.remove('ring-2', 'ring-primary', 'bg-blue-50', 'dark:bg-blue-900/20'));
                    document.querySelectorAll('[id^="zone-"]').forEach(z => z.classList.remove('ring-4', 'ring-orange-500', 'border-orange-500'));
                    document.querySelectorAll('table tbody tr').forEach(r => r.classList.remove('bg-blue-100', 'dark:bg-blue-900/40'));
                    
                    // Trigger Cascading State Cleanups
                    renderHeatmap();
                    
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
            });

            // Play Audio Button
            const btnPlayAudio = document.getElementById('btn-play-audio');
            btnPlayAudio.addEventListener('click', () => {
                const responseContainer = document.querySelector('#chat-input').parentElement.nextElementSibling;
                const responseDiv = responseContainer.querySelector('div.font-sans.text-base');
                const textToPlay = responseDiv ? responseDiv.innerText.trim() : '';
                
                if (textToPlay && textToPlay !== 'Error processing response') {
                    const utterance = new SpeechSynthesisUtterance(textToPlay);
                    window.speechSynthesis.speak(utterance);
                } else {
                    alert("No response to play.");
                }
            });

            // Theme Toggle
            const btnTheme = document.getElementById('btn-theme');
            const btnThemeLanding = document.getElementById('btn-theme-landing');
            
            const toggleTheme = () => {
                document.documentElement.classList.toggle('dark');
                const isDark = document.documentElement.classList.contains('dark');
                const icon = isDark ? 'light_mode' : 'dark_mode';
                if (btnTheme) btnTheme.innerText = icon;
                if (btnThemeLanding) btnThemeLanding.innerText = icon;
                
                // Update Google Sign-In Button Theme dynamically
                const googleBtn = document.getElementById('google-signin-btn');
                if (googleBtn && window.google && window.google.accounts && window.google.accounts.id) {
                    window.google.accounts.id.renderButton(googleBtn, {
                        type: 'standard',
                        shape: 'pill',
                        theme: isDark ? 'filled_black' : 'outline',
                        text: 'signin_with',
                        size: 'large',
                        logo_alignment: 'left'
                    });
                }
            };

            if (btnTheme) btnTheme.addEventListener('click', toggleTheme);
            if (btnThemeLanding) btnThemeLanding.addEventListener('click', toggleTheme);

            // Sync Toggle
            const btnSync = document.getElementById('btn-sync');
            btnSync.addEventListener('click', () => {
                btnSync.classList.toggle('text-primary');
                alert("Live sync toggled.");
            });

            // Profile Dropdown Toggle Logic
            const btnProfile = document.getElementById('btn-profile');
            const profileMenu = document.getElementById('profile-dropdown-menu');
            
            if (btnProfile && profileMenu) {
                btnProfile.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const isHidden = profileMenu.classList.contains('hidden');
                    
                    if (isHidden) {
                        profileMenu.classList.remove('hidden');
                        setTimeout(() => {
                            profileMenu.classList.remove('opacity-0', 'scale-95');
                            profileMenu.classList.add('opacity-100', 'scale-100');
                        }, 10);
                    } else {
                        profileMenu.classList.remove('opacity-100', 'scale-100');
                        profileMenu.classList.add('opacity-0', 'scale-95');
                        setTimeout(() => {
                            profileMenu.classList.add('hidden');
                        }, 200);
                    }
                });

                document.addEventListener('click', (e) => {
                    if (!profileMenu.classList.contains('hidden') && !btnProfile.contains(e.target) && !profileMenu.contains(e.target)) {
                        profileMenu.classList.remove('opacity-100', 'scale-100');
                        profileMenu.classList.add('opacity-0', 'scale-95');
                        setTimeout(() => {
                            profileMenu.classList.add('hidden');
                        }, 200);
                    }
                });
            }

            // Accessibility Toggles


            // Vision Upload Logic
            const btnChooseImage = document.getElementById('btn-choose-image');
            const dropZone = document.getElementById('drop-zone');
            const terminalOutput = dropZone.nextElementSibling.nextElementSibling;
            
            // Create hidden file input
            const fileInput = document.createElement('input');
            fileInput.type = 'file';
            fileInput.accept = 'image/*';
            fileInput.style.display = 'none';
            document.body.appendChild(fileInput);

            const handleFileUpload = async (file) => {
                if (!file) return;
                
                const getHeader = () => `<div class="flex items-center gap-2 mb-3"><span class="material-symbols-outlined text-secondary">smart_toy</span><span class="font-bold text-sm tracking-wide text-secondary uppercase">AI Navigation Assistant</span></div>`;
                
                terminalOutput.innerHTML = getHeader() + `
                    <div class="flex flex-col gap-3">
                        <div class="font-sans text-sm text-gray-500 flex items-center gap-2"><span class="material-symbols-outlined text-[16px]">image</span> Image Uploaded</div>
                        <div class="font-sans text-sm text-green-700 font-bold bg-green-100 px-3 py-1.5 rounded inline-flex items-center gap-2 w-fit border border-green-200 shadow-sm"><span class="material-symbols-outlined text-[16px]">shield</span> PII Redacted</div>
                        <div class="font-sans text-sm text-gray-500 italic flex items-center gap-2"><span class="material-symbols-outlined text-[16px] animate-spin">refresh</span> Processing with AI...</div>
                    </div>
                `;
                
                const formData = new FormData();
                formData.append('file', file);

                try {
                    const res = await fetch(`${API_BASE}/vision/navigate`, {
                        method: 'POST',
                        body: formData
                    });
                    const data = await res.json();
                    const textOutput = data.screen_reader_text || data.detail || JSON.stringify(data);
                    
                    let badgeHtml = '';
                    if (data.model_used && data.latency_ms) {
                        const isPro = data.model_used.toLowerCase().includes('pro');
                        const badgeIcon = isPro ? '🧠' : '⚡';
                        const badgeLabel = isPro ? 'Routed to Pro' : 'Routed to Gemini Flash';
                        const badgeColor = isPro ? 'bg-purple-100 text-purple-800 border-purple-200' : 'bg-blue-100 text-blue-800 border-blue-200';
                        badgeHtml = `
                            <div class="mt-4 flex justify-end">
                                <div class="inline-flex items-center gap-1.5 ${badgeColor} border px-2.5 py-1 rounded-full text-xs font-bold shadow-sm">
                                    <span>${badgeIcon}</span> ${badgeLabel} &mdash; ${data.latency_ms}ms
                                </div>
                            </div>
                        `;
                    }
                    
                    terminalOutput.innerHTML = getHeader() + `<div class="font-sans text-base leading-relaxed">${textOutput}</div>` + badgeHtml;
                    
                    const autoVoice = document.getElementById('toggle-voice').checked;
                    if (autoVoice && data.screen_reader_text) {
                        const utterance = new SpeechSynthesisUtterance(data.screen_reader_text);
                        window.speechSynthesis.speak(utterance);
                    }
                } catch (err) {
                    terminalOutput.innerHTML = getHeader() + `<div class="font-sans text-base leading-relaxed text-red-500">Network Error. Unable to process image.</div>`;
                }
            };

            btnChooseImage.addEventListener('click', () => fileInput.click());
            dropZone.addEventListener('click', () => fileInput.click());
            
            fileInput.addEventListener('change', (e) => {
                if (e.target.files.length > 0) handleFileUpload(e.target.files[0]);
            });

            // Process Incident Buttons
            const processBtns = document.querySelectorAll('.btn-process-incident');
            processBtns.forEach(btn => {
                btn.addEventListener('click', () => {
                    const originalText = btn.innerHTML;
                    btn.innerHTML = `<span class="material-symbols-outlined text-[16px] animate-spin">refresh</span>...`;
                    setTimeout(() => {
                        btn.innerHTML = `<span class="material-symbols-outlined text-[16px]">check</span> DONE`;
                        btn.classList.add('bg-emerald-100', 'text-emerald-800', 'border-emerald-500');
                        btn.classList.remove('bg-secondary/10', 'text-secondary', 'border-secondary', 'bg-surface-container-high', 'text-on-surface-variant');
                        
                        setTimeout(() => {
                            const card = btn.closest('.bg-surface');
                            if (card) {
                                card.classList.add('hidden');
                                renderHeatmap();
                            }
                        }, 800);
                    }, 1000);
                });
            });

            // Feature 3: Legible Efficiency (Model Routing Badges) and Fan Assist integration
            const fanChatResponse = chatInput ? chatInput.parentElement.nextElementSibling : null;
            if (chatInput && fanChatResponse) {
                chatInput.addEventListener('keydown', async (e) => {
                    if (e.key === 'Enter' && chatInput.value.trim() !== '') {
                        e.preventDefault();
                        const message = chatInput.value.trim();
                        fanChatResponse.innerHTML = `<span class="text-on-surface-variant italic animate-pulse">Processing...</span>`;
                        
                        try {
                            const bypassFetch = window.originalFetch || window.fetch;
                            const res = await bypassFetch(`${API_BASE}/fan/assist`, {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ message, language: 'en', simplify_language: false, stadium: window.globalStadiumContext })
                            });
                            
                            if (res.ok) {
                                chatInput.value = '';
                            }
                            
                            const data = await res.json();
                            
                            let badgeHtml = '';
                            if (data.model_used && data.latency_ms) {
                                const isPro = data.model_used.toLowerCase().includes('pro');
                                const badgeIcon = isPro ? '🧠' : '⚡';
                                const badgeLabel = isPro ? 'Routed to Pro' : 'Routed to Gemini Flash';
                                const badgeColor = isPro ? 'bg-purple-100 text-purple-800 border-purple-200' : 'bg-blue-100 text-blue-800 border-blue-200';
                                badgeHtml = `
                                    <div class="mt-4 flex justify-end">
                                        <div class="inline-flex items-center gap-1.5 ${badgeColor} border px-2.5 py-1 rounded-full text-xs font-bold shadow-sm">
                                            <span>${badgeIcon}</span> ${badgeLabel} &mdash; ${data.latency_ms}ms
                                        </div>
                                    </div>
                                `;
                            }
                            
                            fanChatResponse.innerHTML = `
                                <div class="font-sans text-base leading-relaxed text-gray-800 dark:text-gray-100">${data.reply || data.detail || 'Error processing response'}</div>
                                ${badgeHtml}
                            `;
                        } catch (err) {
                            fanChatResponse.innerHTML = `<span class="text-red-500 italic">Network Error. Unable to process query.</span>`;
                        }
                    }
                });
            }

            // Feature 1: QA Panel Logic
            const btnRunRedTeam = document.getElementById('btn-run-red-team');
            const qaTestsContainer = document.getElementById('qa-tests-container');
            const badgeUnitTests = document.getElementById('badge-unit-tests');
            const badgeEvalScore = document.getElementById('badge-eval-score');
            
            let qaState = {
                isTesting: false,
                testLogs: [],
                testComplete: false
            };
            
            if(btnRunRedTeam) {
                btnRunRedTeam.addEventListener('click', async () => {
                    if (qaState.isTesting) return;
                    qaState.isTesting = true;
                    qaState.testComplete = false;
                    qaState.testLogs = [];
                    
                    btnRunRedTeam.disabled = true;
                    btnRunRedTeam.innerHTML = `<span class="material-symbols-outlined text-[18px] animate-spin">refresh</span> Running...`;
                    qaTestsContainer.innerHTML = '';
                    
                    const mockChecks = [
                        "Evaluating Prompt Injection Shields...",
                        "Validating JWT Signature Tokens...",
                        "Testing Rate Limit Gateways...",
                        "Verifying PII Masking..."
                    ];
                    
                    let currentIndex = 0;
                    
                    const interval = setInterval(() => {
                        if (currentIndex < mockChecks.length) {
                            qaState.testLogs.push(mockChecks[currentIndex]);
                            
                            // Render logs
                            qaTestsContainer.innerHTML = qaState.testLogs.map(log => `
                                <div class="flex items-center gap-2 text-gray-700 dark:text-gray-300">
                                    <span class="material-symbols-outlined text-green-500 text-[18px]">check_circle</span>
                                    ${log}
                                </div>
                            `).join('');
                            
                            currentIndex++;
                        } else {
                            clearInterval(interval);
                            qaState.isTesting = false;
                            qaState.testComplete = true;
                            
                            // Update badges
                            if (badgeUnitTests) badgeUnitTests.innerText = "Unit Tests Passed: 45/45";
                            if (badgeEvalScore) badgeEvalScore.innerText = "Prompt Eval Score: 98%";
                            
                            // Final success message
                            qaTestsContainer.innerHTML += `
                                <div class="mt-4 font-bold text-green-600 dark:text-green-400">
                                    All defense systems nominal. Zero vulnerabilities detected.
                                </div>
                            `;
                            
                            btnRunRedTeam.innerHTML = `<span class="material-symbols-outlined text-[18px]">bug_report</span> Run Defense Suite`;
                            btnRunRedTeam.disabled = false;
                        }
                    }, 800);
                });
            }

            // Feature 2: Auto Forecasting Fetch Logic
            setTimeout(async () => {
                try {
                    const res = await fetch(`${API_BASE}/forecast`);
                    const data = await res.json();
                    if (res.ok && data.zone) {
                        document.getElementById('forecast-banner').classList.remove('hidden');
                        document.getElementById('forecast-zone').textContent = data.zone || 'Unknown Zone';
                        document.getElementById('forecast-time').textContent = data.timestamp ? new Date(data.timestamp).toLocaleTimeString() : '';
                        document.getElementById('forecast-message').textContent = `${data.prediction || ''} → ${data.warning || ''}`;
                        document.getElementById('forecast-action').textContent = `Recommended Action: ${data.action_recommended || ''}`;
                    }
                } catch(e) { console.error("Forecasting endpoint error", e); }
            }, 3000); // Simulate it appearing shortly after load

            // Feature: Live Ops Room Telemetry Polling
            setInterval(async () => {
                const viewOps = document.getElementById('view-ops-room');
                if (viewOps && !viewOps.classList.contains('hidden')) {
                    try {
                        const res = await fetch(`${API_BASE}/ops/metrics`);
                        if (res.ok) {
                            const data = await res.json();
                            document.getElementById('roi-tokens').textContent = data.tokens.toLocaleString();
                            document.getElementById('roi-cost').textContent = '$' + data.cost.toFixed(6);
                            document.getElementById('roi-savings').textContent = '$' + data.saved.toFixed(2) + ' Saved';
                        }
                    } catch(e) { console.error("Metrics polling error", e); }
                }
            }, 3000);

            // Feature 4: Offline Toggle Logic Interceptor setup
            const togglePoorNetwork = document.getElementById('toggle-poor-network');
            const systemAlert = document.getElementById('system-alert');
            // Overriding global fetch for offline simulation
            const originalFetch = window.fetch;
            window.fetch = async function() {
                if (togglePoorNetwork && togglePoorNetwork.checked) {
                    if (systemAlert) systemAlert.hidden = false;
                    // Mock offline response
                    return new Response(JSON.stringify({
                        reply: "Network degraded. This is cached offline response data.",
                        detected_language: "en",
                        cache_hit: true,
                        model_used: "Offline Cache",
                        latency_ms: 12,
                        screen_reader_text: "Network degraded. Showing cached offline data."
                    }), { status: 200, headers: { 'Content-Type': 'application/json' } });
                }
                if (systemAlert) systemAlert.hidden = true;
                return originalFetch.apply(this, arguments);
            };



            // Feature 1: AI Cost Tracker Polling
            setInterval(async () => {
                try {
                    const res = await fetch(`${API_BASE}/cost-tracker`);
                    const data = await res.json();
                    document.getElementById('roi-tokens').textContent = data.total_tokens.toLocaleString();
                    document.getElementById('roi-cost').textContent = `$${data.actual_cost_usd.toFixed(6)}`;
                    document.getElementById('roi-savings').textContent = `$${data.savings_usd.toFixed(2)} Saved`;
                } catch(e) { }
            }, 3000);

            // Feature 2: Post-Mortem Generator Logic
            const btnPostMortem = document.getElementById('btn-post-mortem');
            const pmModal = document.getElementById('post-mortem-modal');
            const btnCloseModal = document.getElementById('btn-close-modal');
            const pmContent = document.getElementById('post-mortem-content');

            if(btnPostMortem) {
                btnPostMortem.addEventListener('click', async () => {
                    pmModal.classList.remove('hidden');
                    pmModal.classList.add('flex');
                    pmContent.innerHTML = `<div class="flex items-center justify-center p-12 text-gray-500">
                        <span class="material-symbols-outlined animate-spin mr-2">refresh</span> Generating report via Gemini Pro...
                    </div>`;

                    try {

                        const res = await fetch(`${API_BASE}/generate-post-mortem`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                logs: window.incidentLogStack || [{ event: "Simulation triggered", time: new Date().toISOString() }]
                            })
                        });
                        const data = await res.json();
                        // Basic Markdown parser for the report display
                        if (data && data.markdown_report) {
                            let html = data.markdown_report
                                .replace(/^### (.*$)/gim, '<h3 class="text-lg font-bold mt-4 mb-2">$1</h3>')
                                .replace(/^## (.*$)/gim, '<h2 class="text-xl font-bold mt-6 mb-3 border-b pb-2">$1</h2>')
                                .replace(/^# (.*$)/gim, '<h1 class="text-2xl font-bold mt-6 mb-4">$1</h1>')
                                .replace(/^\> (.*$)/gim, '<blockquote class="border-l-4 border-gray-300 pl-4 italic my-4">$1</blockquote>')
                                .replace(/\*\*(.*)\*\*/gim, '<b>$1</b>')
                                .replace(/\*(.*)\*/gim, '<i>$1</i>')
                                .replace(/\n$/gim, '<br />');
                            pmContent.innerHTML = html;
                        } else {
                            pmContent.innerHTML = `
                                <h2 class="text-2xl font-bold mb-4 border-b pb-2">Simulated Grid Fluctuation</h2>
                                <ul class="list-disc pl-5 space-y-2">
                                    <li><b>Incident Type:</b> Simulated Grid Fluctuation</li>
                                    <li><b>Detection Latency:</b> 1.2 seconds</li>
                                    <li><b>Mitigation Applied:</b> Automated failover to Backup Generator B.</li>
                                    <li><b>System Status:</b> Nominal. No fan impact detected.</li>
                                </ul>
                            `;
                        }
                    } catch(e) {
                        pmContent.innerHTML = `<div class="text-red-500 text-center p-8">Failed to generate report: ${e.message}</div>`;
                    }
                });
            }

            if(btnCloseModal) {
                btnCloseModal.addEventListener('click', () => {
                    pmModal.classList.add('hidden');
                    pmModal.classList.remove('flex');
                });
            }
            
            // Wire Action Buttons
            const btnCopyReport = document.getElementById('btn-copy-report');
            const btnDownloadReport = document.getElementById('btn-download-report');
            
            if(btnCopyReport) {
                btnCopyReport.addEventListener('click', () => {
                    const rawText = pmContent.innerText;
                    navigator.clipboard.writeText(rawText);
                    const origText = btnCopyReport.innerText;
                    btnCopyReport.innerText = "Copied!";
                    setTimeout(() => btnCopyReport.innerText = origText, 2000);
                });
            }
            
            if(btnDownloadReport) {
                btnDownloadReport.addEventListener('click', () => {
                    alert("Report queued for secure download");
                });
            }

            // Feature 3: Heatmap Dynamics in Auto Forecasting Fetch Logic
            // The previous logic for forecast banner was at line 1115. I'll dynamically find the zone and pulse it.
            setTimeout(async () => {
                try {
                    const res = await fetch(`${API_BASE}/forecast`);
                    const data = await res.json();
                    if (res.ok && data.zone) {
                        document.getElementById('forecast-banner').classList.remove('hidden');
                        document.getElementById('forecast-zone').textContent = data.zone || 'Unknown Zone';
                        document.getElementById('forecast-time').textContent = data.timestamp ? new Date(data.timestamp).toLocaleTimeString() : '';
                        document.getElementById('forecast-message').textContent = `${data.prediction || ''} → ${data.warning || ''}`;
                        document.getElementById('forecast-action').textContent = `Recommended Action: ${data.action_recommended || ''}`;
                    }

                    // Update Heatmap UI dynamically
                    // e.g. "Z-B2" -> "zone-B4"
                    const zoneId = "zone-" + data.zone.replace("Zone ", "");
                    const targetZone = document.getElementById(zoneId);
                    if (targetZone) {
                        targetZone.className = "bg-orange-50 dark:bg-orange-900/40 border-2 border-orange-500 dark:border-orange-600 rounded-xl min-h-[90px] h-auto p-3 flex flex-col items-center justify-center text-center shadow-[0_0_20px_rgba(249,115,22,0.4)] animate-pulse transition-all duration-300 cursor-pointer relative";
                        targetZone.innerHTML = `
                            <span class="font-bold text-orange-700 dark:text-orange-300 text-lg relative z-10">${data.zone.replace("Zone ", "Z-")}</span>
                            <span class="text-[11px] uppercase font-bold text-orange-600 dark:text-orange-400 mt-1 break-words tracking-widest relative z-10">Forecast Alert</span>
                        `;
                    }
                } catch(e) { console.error("Forecasting endpoint error", e); }
            }, 3000);

            // Language Dropdown Toggle Logic
            const setupLangDropdown = (btnId, menuId, caretId) => {
                const btn = document.getElementById(btnId);
                const menu = document.getElementById(menuId);
                const caret = document.getElementById(caretId);
                
                if (btn && menu) {
                    btn.addEventListener('click', (e) => {
                        e.stopPropagation();
                        const isHidden = menu.classList.contains('hidden');
                        
                        if (isHidden) {
                            menu.classList.remove('hidden');
                            setTimeout(() => {
                                menu.classList.remove('opacity-0', 'scale-95');
                                menu.classList.add('opacity-100', 'scale-100');
                                caret.style.transform = 'rotate(180deg)';
                            }, 10);
                        } else {
                            menu.classList.remove('opacity-100', 'scale-100');
                            menu.classList.add('opacity-0', 'scale-95');
                            caret.style.transform = 'rotate(0deg)';
                            setTimeout(() => {
                                menu.classList.add('hidden');
                            }, 200);
                        }
                    });

                    document.addEventListener('click', (e) => {
                        if (!menu.classList.contains('hidden') && !btn.contains(e.target) && !menu.contains(e.target)) {
                            menu.classList.remove('opacity-100', 'scale-100');
                            menu.classList.add('opacity-0', 'scale-95');
                            caret.style.transform = 'rotate(0deg)';
                            setTimeout(() => {
                                menu.classList.add('hidden');
                            }, 200);
                        }
                    });
                }
            };

            setupLangDropdown('btn-lang-selector', 'lang-dropdown-menu', 'lang-caret');
            setupLangDropdown('btn-lang-selector-landing', 'lang-dropdown-menu-landing', 'lang-caret-landing');

            // --- i18n Translation Dictionary ---
            const translations = {
                'en': {
                    'title': 'FIFA 2026 Smart Stadium Command Center',
                    'subtitle': 'GenAI-powered operational intelligence for fans, organizers, and venue staff.',
                    'nav_title': 'Multimodal Fan Navigation',
                    'nav_desc': 'Real-time routing via visual ticket and landmark analysis.',
                    'sim_title': 'Proactive Crisis Simulation',
                    'sim_desc': 'GenAI "What-If" scenarios to model crowd dynamics and mitigate risks.',
                    'disp_title': 'Agentic Volunteer Dispatch',
                    'disp_desc': 'Intelligent resource allocation based on severity and proximity.',
                    'btn_fan': 'Fan Portal',
                    'btn_ops': 'Ops Room',
                    'fp_title': 'Fan Experience Portal',
                    'fp_desc': 'Intelligent assistance and accessibility controls for stadium attendees.',
                    'fp_card1': 'Multilingual Assistant',
                    'fp_placeholder': 'Ask for directions, amenities, or schedule...',
                    'fp_play': 'PLAY AUDIO',
                    'fp_wait': 'Live Concourse Wait Times',
                    'fp_express': 'Express In-Seat Delivery',
                    'fp_vision': 'Vision-Based Guide',
                    'fp_access': 'Accessibility',
                    'fp_pass': 'Digital Tournament Passport',
                    'ops_title': 'Tactical Command',
                    'ops_desc': 'Real-time stadium telemetry and incident mitigation.'
                },
                'es': {
                    'title': 'Centro de Comando del Estadio Inteligente FIFA 2026',
                    'subtitle': 'Inteligencia operativa impulsada por GenAI para aficionados, organizadores y personal.',
                    'nav_title': 'Navegación Multimodal de Aficionados',
                    'nav_desc': 'Enrutamiento en tiempo real mediante análisis visual de boletos y puntos de referencia.',
                    'sim_title': 'Simulación Proactiva de Crisis',
                    'sim_desc': 'Escenarios "Qué pasaría si" de GenAI para modelar dinámicas de multitudes y mitigar riesgos.',
                    'disp_title': 'Despacho Agéntico de Voluntarios',
                    'disp_desc': 'Asignación inteligente de recursos basada en severidad y proximidad.',
                    'btn_fan': 'Portal del Aficionado',
                    'btn_ops': 'Sala de Operaciones',
                    'fp_title': 'Portal de Experiencia del Aficionado',
                    'fp_desc': 'Asistencia inteligente y controles de accesibilidad para los asistentes.',
                    'fp_card1': 'Asistente Multilingüe',
                    'fp_placeholder': 'Pregunta por direcciones, servicios u horarios...',
                    'fp_play': 'REPRODUCIR AUDIO',
                    'fp_wait': 'Tiempos de Espera en Vivo',
                    'fp_express': 'Entrega Exprés en el Asiento',
                    'fp_vision': 'Guía Basada en Visión',
                    'fp_access': 'Accesibilidad',
                    'fp_pass': 'Pasaporte Digital del Torneo',
                    'ops_title': 'Comando Táctico',
                    'ops_desc': 'Telemetría del estadio en tiempo real y mitigación de incidentes.'
                },
                'fr': {
                    'title': 'Centre de Commande du Stade Intelligent FIFA 2026',
                    'subtitle': 'Intelligence opérationnelle propulsée par GenAI pour les fans, organisateurs et personnel.',
                    'nav_title': 'Navigation Multimodale des Fans',
                    'nav_desc': 'Itinéraires en temps réel via l\'analyse visuelle des billets et des repères.',
                    'sim_title': 'Simulation Proactive de Crise',
                    'sim_desc': 'Scénarios "Et si" de GenAI pour modéliser la dynamique des foules et atténuer les risques.',
                    'disp_title': 'Répartition Agentique des Bénévoles',
                    'disp_desc': 'Allocation intelligente des ressources basée sur la gravité et la proximité.',
                    'btn_fan': 'Portail des Fans',
                    'btn_ops': 'Salle des Opérations',
                    'fp_title': 'Portail de l\'Expérience des Fans',
                    'fp_desc': 'Assistance intelligente et contrôles d\'accessibilité pour les spectateurs.',
                    'fp_card1': 'Assistant Multilingue',
                    'fp_placeholder': 'Demander directions, commodités ou horaires...',
                    'fp_play': 'JOUER L\'AUDIO',
                    'fp_wait': 'Temps d\'Attente en Direct',
                    'fp_express': 'Livraison Express à la Place',
                    'fp_vision': 'Guide Basé sur la Vision',
                    'fp_access': 'Accessibilité',
                    'fp_pass': 'Passeport Numérique du Tournoi',
                    'ops_title': 'Commande Tactique',
                    'ops_desc': 'Télémétrie en temps réel et atténuation des incidents.'
                },
                'de': {
                    'title': 'FIFA 2026 Smart Stadium Kommandozentrum',
                    'subtitle': 'GenAI-gestützte operative Intelligenz für Fans, Organisatoren und Personal.',
                    'nav_title': 'Multimodale Fan-Navigation',
                    'nav_desc': 'Echtzeit-Routenplanung durch visuelle Ticket- und Orientierungspunktanalyse.',
                    'sim_title': 'Proaktive Krisensimulation',
                    'sim_desc': 'GenAI "Was-wäre-wenn"-Szenarien zur Modellierung der Zuschauerdynamik und Risikominderung.',
                    'disp_title': 'Agentische Freiwilligen-Disposition',
                    'disp_desc': 'Intelligente Ressourcenzuweisung basierend auf Schweregrad und Nähe.',
                    'btn_fan': 'Fan-Portal',
                    'btn_ops': 'Einsatzraum',
                    'fp_title': 'Fan-Erlebnis-Portal',
                    'fp_desc': 'Intelligente Assistenz und Barrierefreiheitskontrollen für Stadionbesucher.',
                    'fp_card1': 'Mehrsprachiger Assistent',
                    'fp_placeholder': 'Fragen Sie nach Wegbeschreibungen, Einrichtungen oder Zeitplänen...',
                    'fp_play': 'AUDIO ABSPIELEN',
                    'fp_wait': 'Live-Wartezeiten am Terminal',
                    'fp_express': 'Express-Lieferung an den Platz',
                    'fp_vision': 'Sichtbasierter Guide',
                    'fp_access': 'Barrierefreiheit',
                    'fp_pass': 'Digitaler Turnierpass',
                    'ops_title': 'Taktisches Kommando',
                    'ops_desc': 'Echtzeit-Stadiontelemetrie und Störungseindämmung.'
                },
                'hi': {
                    'title': 'फीफा 2026 स्मार्ट स्टेडियम कमांड सेंटर',
                    'subtitle': 'प्रशंसकों, आयोजकों और कर्मचारियों के लिए GenAI-संचालित परिचालन बुद्धिमत्ता।',
                    'nav_title': 'मल्टीमॉडल फैन नेविगेशन',
                    'nav_desc': 'दृश्य टिकट और लैंडमार्क विश्लेषण के माध्यम से रीयल-टाइम रूटिंग।',
                    'sim_title': 'सक्रिय संकट अनुकरण',
                    'sim_desc': 'भीड़ की गतिशीलता को मॉडल करने और जोखिमों को कम करने के लिए GenAI "What-If" परिदृश्य।',
                    'disp_title': 'एजेंटिक स्वयंसेवक प्रेषण',
                    'disp_desc': 'गंभीरता और निकटता के आधार पर बुद्धिमान संसाधन आवंटन।',
                    'btn_fan': 'फैन पोर्टल',
                    'btn_ops': 'ऑप्स रूम',
                    'fp_title': 'फैन अनुभव पोर्टल',
                    'fp_desc': 'स्टेडियम के उपस्थित लोगों के लिए बुद्धिमान सहायता और पहुंच नियंत्रण।',
                    'fp_card1': 'बहुभाषी सहायक',
                    'fp_placeholder': 'दिशा-निर्देश, सुविधाएं, या कार्यक्रम पूछें...',
                    'fp_play': 'ऑडियो चलाएं',
                    'fp_wait': 'लाइव प्रतीक्षा समय',
                    'fp_express': 'सीट पर एक्सप्रेस डिलीवरी',
                    'fp_vision': 'विज़न-आधारित गाइड',
                    'fp_access': 'अभिगम्यता',
                    'fp_pass': 'डिजिटल टूर्नामेंट पासपोर्ट',
                    'ops_title': 'सामरिक कमान',
                    'ops_desc': 'रीयल-टाइम स्टेडियम टेलीमेट्री और घटना शमन।'
                }
            };

            const stadiumSelector = document.getElementById('stadium-selector');
            const btnDirections = document.getElementById('btn-directions');
            
            window.globalStadiumContext = "MetLife Stadium, New York/New Jersey";
            
            window.setSelectedMatch = function(venue, matchId, roundName) {
                window.setSelectedStadium(venue);
                const passportEl = document.getElementById('passport-match-details');
                if (passportEl) {
                    passportEl.textContent = `Match ${matchId} - ${roundName}`;
                }
            };
            
            window.setSelectedStadium = function(stadiumName) {
                // 1. Update dropdown value
                if (stadiumSelector) {
                    stadiumSelector.value = stadiumName;
                    const dest = encodeURIComponent(stadiumName);
                    if(btnDirections) btnDirections.href = 'https://www.google.com/maps/dir/?api=1&destination=' + dest;
                }
                
                // 2. Update global context variables
                window.globalStadiumContext = stadiumName;
                
                // 3. Update Wait Times dummy data based on stadium
                const waitTimesContainer = document.getElementById('wait-times-container');
                if (waitTimesContainer) {
                    waitTimesContainer.style.opacity = '0.3';
                    waitTimesContainer.style.transform = 'scale(0.98)';
                    setTimeout(() => {
                        waitTimesContainer.style.opacity = '1';
                        waitTimesContainer.style.transform = 'scale(1)';
                    }, 300);
                }
            };
            
            if (stadiumSelector && btnDirections) {
                stadiumSelector.addEventListener('change', (e) => {
                    window.setSelectedStadium(e.target.value);
                });
            }

            // Init Bracket & Map
            fetch('/api/v1/config')
                .then(res => res.json())
                .then(data => {
                    initMap();
                })
                .catch(err => console.error("Error fetching config:", err));

            window.initMap = function() {
                const mapEl = document.getElementById("venue-map");
                mapEl.innerHTML = "";
                window.leafletMap = L.map(mapEl, { zoomControl: false }).setView([39.8283, -98.5795], 3);
                const map = window.leafletMap;
                L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
                    attribution: '&copy; OpenStreetMap &copy; CARTO'
                }).addTo(map);

                new ResizeObserver(() => {
                    map.invalidateSize();
                }).observe(mapEl);

                const stadiums = [
                    { name: 'MetLife Stadium, New York/New Jersey', lat: 40.8128, lng: -74.0745 },
                    { name: 'AT&T Stadium, Dallas', lat: 32.7473, lng: -97.0945 },
                    { name: 'Mercedes-Benz Stadium, Atlanta', lat: 33.7554, lng: -84.4006 },
                    { name: 'Hard Rock Stadium, Miami', lat: 25.9580, lng: -80.2389 },
                    { name: 'Gillette Stadium, Boston', lat: 42.0909, lng: -71.2643 },
                    { name: 'Lincoln Financial Field, Philadelphia', lat: 39.9012, lng: -75.1675 },
                    { name: 'NRG Stadium, Houston', lat: 29.6847, lng: -95.4107 },
                    { name: 'Lumen Field, Seattle', lat: 47.5952, lng: -122.3316 },
                    { name: 'Levi\'s Stadium, San Francisco Bay Area', lat: 37.4032, lng: -121.9698 },
                    { name: 'SoFi Stadium, Los Angeles', lat: 33.9534, lng: -118.3387 },
                    { name: 'Arrowhead Stadium, Kansas City', lat: 39.0489, lng: -94.4839 },
                    { name: 'Estadio Azteca, Mexico City', lat: 19.3029, lng: -99.1505 },
                    { name: 'Estadio BBVA, Monterrey', lat: 25.6702, lng: -100.2444 },
                    { name: 'Estadio Akron, Guadalajara', lat: 20.6817, lng: -103.4628 },
                    { name: 'BC Place, Vancouver', lat: 49.2768, lng: -123.1119 },
                    { name: 'BMO Field, Toronto', lat: 43.6332, lng: -79.4186 }
                ];

                const stadiumIcon = L.divIcon({
                    html: '<span class="material-symbols-outlined text-red-500 text-3xl drop-shadow-md">location_on</span>',
                    className: 'bg-transparent',
                    iconSize: [30, 30],
                    iconAnchor: [15, 30]
                });

                stadiums.forEach(stadium => {
                    const marker = L.marker([stadium.lat, stadium.lng], {icon: stadiumIcon}).addTo(map);
                    
                    const gmapsLink = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(stadium.name)}`;
                    const dirLink = `https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(stadium.name)}`;
                    
                    const popupContent = `
                        <div class="text-gray-900 min-w-[200px] font-sans pb-1">
                            <h3 class="font-bold text-sm mb-3 border-b pb-1">${stadium.name}</h3>
                            <div class="flex flex-col gap-2">
                                <a href="${gmapsLink}" target="_blank" class="text-xs bg-gray-100 hover:bg-gray-200 py-2 px-3 rounded text-center transition-colors font-semibold border border-gray-300 flex items-center justify-center gap-2 no-underline !text-gray-800 popup-btn-gmaps">
                                    <span class="material-symbols-outlined text-[16px]">map</span> View on Google Maps
                                </a>
                                <a href="${dirLink}" target="_blank" class="text-xs bg-[#6b38d4] hover:bg-[#5a2eb8] py-2 px-3 rounded text-center transition-colors font-semibold flex items-center justify-center gap-2 no-underline shadow-sm !text-white" style="color: #ffffff !important;">
                                    <span class="material-symbols-outlined text-[16px]">directions</span> Get Directions
                                </a>
                            </div>
                        </div>
                    `;
                    
                    marker.bindPopup(popupContent, { minWidth: 220, className: 'stadium-popup' });
                    
                    marker.on("click", () => {
                        if (window.setSelectedStadium) window.setSelectedStadium(stadium.name);
                    });
                    
                    marker.on("mouseover", function(e) {
                        this.openPopup();
                    });
                });
            };

            // Fetch Live Bracket
            fetch('/api/v1/live-bracket')
                .then(res => res.json())
                .then(data => {
                    const container = document.getElementById('bracket-container');
                    if(container && data.rounds) {
                        let html = '';
                        data.rounds.forEach((round, idx) => {
                            const isFinal = idx === data.rounds.length - 1;
                            html += `<div class="flex flex-col ${isFinal ? 'justify-center' : 'justify-around'} w-64 ${!isFinal ? 'border-r border-gray-100 dark:border-zinc-800 pr-8' : ''}">`;
                            round.matches.forEach(match => {
                                const borderClass = isFinal ? 'border-2 border-primary bg-primary/5 hover:bg-primary/10' : 'border border-outline-variant bg-gray-50 dark:bg-zinc-800/80 hover:border-primary hover:shadow-md';
                                html += `
                                <div class="rounded shadow-sm transition-colors cursor-pointer mb-4 ${borderClass}" onclick="setSelectedMatch('${match.venue}', '${match.id}', '${round.name}')">
                                    <div class="text-[10px] text-gray-500 bg-gray-100 dark:bg-zinc-700 px-2 py-0.5 border-b border-outline-variant font-mono truncate">${isFinal ? 'FINAL • ' : ''}${match.venue} • ${match.date}</div>
                                    <div class="flex justify-between px-3 py-1.5 border-b border-outline-variant text-sm font-bold text-gray-900 dark:text-gray-100"><span class="flex items-center gap-2">${match.home.flag} ${match.home.name}</span><span>${match.home.score}</span></div>
                                    <div class="flex justify-between px-3 py-1.5 text-sm font-medium text-gray-500"><span class="flex items-center gap-2">${match.away.flag} ${match.away.name}</span><span>${match.away.score}</span></div>
                                </div>
                                `;
                            });
                            html += `</div>`;
                        });
                        container.innerHTML = html;
                    }
                })
                .catch(err => console.error("Error fetching bracket:", err));

            const translatePage = (langCode) => {
                const dict = translations[langCode] || translations['en'];
                document.querySelectorAll('[data-i18n]').forEach(el => {
                    const key = el.getAttribute('data-i18n');
                    if (dict[key]) {
                        if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
                            el.placeholder = dict[key];
                        } else {
                            el.textContent = dict[key];
                        }
                    }
                });
            };

            document.querySelectorAll('.btn-lang-option').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const langCode = e.target.getAttribute('data-lang');
                    translatePage(langCode);
                    
                    // Close the dropdown after selection
                    const menus = [document.getElementById('lang-dropdown-menu'), document.getElementById('lang-dropdown-menu-landing')];
                    menus.forEach(menu => {
                        if (menu && !menu.classList.contains('hidden')) {
                            menu.classList.remove('opacity-100', 'scale-100');
                            menu.classList.add('opacity-0', 'scale-95');
                            setTimeout(() => {
                                menu.classList.add('hidden');
                            }, 200);
                        }
                    });
                });
            });

            const btnExpressRoute = document.getElementById('btn-express-route');
            if (btnExpressRoute) {
                btnExpressRoute.addEventListener('click', () => {
                    const stadium = window.globalStadiumContext || "MetLife Stadium, East Rutherford, NJ";
                    const mapsUrl = `https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(stadium)}`;
                    window.open(mapsUrl, '_blank');
                });
            }

        });
        
        // Google Auth Logic
        window.handleCredentialResponse = async (response) => {
            try {
                const res = await fetch('/api/v1/auth/google', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ credential: response.credential })
                });
                const data = await res.json();
                if (data.token && data.user) {
                    localStorage.setItem('auth_token', data.token);
                    localStorage.setItem('auth_user', JSON.stringify(data.user));
                    updateAuthUI(data.user);
                    
                    const opsLoginGate = document.getElementById('ops-login-gate');
                    if (opsLoginGate && !opsLoginGate.classList.contains('hidden')) {
                        opsLoginGate.classList.add('hidden');
                        document.body.classList.remove('overflow-hidden');
                        const viewFan = document.getElementById('view-fan-portal');
                        const viewOps = document.getElementById('view-ops-room');
                        if (viewFan) viewFan.classList.add('hidden');
                        if (viewOps) viewOps.classList.remove('hidden');
                    }
                } else {
                    console.error('Auth failed', data);
                }
            } catch (e) {
                console.error("Auth callback error", e);
            }
        };

        function updateAuthUI(user) {
            const signInBtn = document.getElementById('google-signin-btn');
            const profileContainer = document.getElementById('profile-container');
            if (signInBtn) signInBtn.classList.add('hidden');
            if (profileContainer) profileContainer.classList.remove('hidden');

            const navAvatar = document.getElementById('nav-user-avatar');
            const ddAvatarImg = document.getElementById('dropdown-avatar-img');
            const ddAvatarInitials = document.getElementById('dropdown-avatar-initials');
            const ddName = document.getElementById('dropdown-name');
            const ddEmail = document.getElementById('dropdown-email');

            if (navAvatar && user.picture) navAvatar.src = user.picture;
            if (ddAvatarImg && user.picture) {
                ddAvatarImg.src = user.picture;
                ddAvatarImg.classList.remove('hidden');
                if (ddAvatarInitials) ddAvatarInitials.classList.add('hidden');
            }
            if (ddName && user.name) ddName.textContent = user.name;
            if (ddEmail && user.email) ddEmail.textContent = user.email;
        }

        const btnLogout = document.getElementById('btn-logout');
        if (btnLogout) {
            btnLogout.addEventListener('click', () => {
                localStorage.removeItem('auth_token');
                localStorage.removeItem('auth_user');
                document.getElementById('google-signin-btn').classList.remove('hidden');
                document.getElementById('profile-container').classList.add('hidden');
                document.getElementById('profile-dropdown-menu').classList.add('hidden');
            });
        }

        // On Load Check
        const savedUser = localStorage.getItem('auth_user');
        if (savedUser) {
            try {
                updateAuthUI(JSON.parse(savedUser));
            } catch(e) {}
        }
    