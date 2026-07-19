import re

with open('static/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add ID to the UL list
old_ul = '<ul class="space-y-4 font-mono-data text-mono-data text-[13px]">'
new_ul = '<ul id="inbound-prompt-log" class="space-y-4 font-mono-data text-mono-data text-[13px]">'
if old_ul in html:
    html = html.replace(old_ul, new_ul)
else:
    print("Could not find old_ul")
    exit(1)

# 2. Inject JS logic
js_code = """
            // Inbound Prompt Log Live Stream
            const promptLogList = document.getElementById('inbound-prompt-log');
            if (promptLogList) {
                let activeLogs = [
                    { type: 'success', text: "SELECT * FROM crowd_density WHERE zone='B4'" },
                    { type: 'success', text: "Translate: 'Where is the nearest bathroom?' to ES" },
                    { type: 'success', text: "Verify_Ticket_Img: src_hash_8f92a..." },
                    { type: 'warning', text: "Rate limit warning on Vision API" },
                    { type: 'success', text: "Concourse routing matrix calculation: OK" }
                ];

                const mockLogPool = [
                    { type: 'success', text: "SELECT * FROM crowd_density WHERE zone='B4'" },
                    { type: 'success', text: "Translate: 'Where is the nearest bathroom?' to ES" },
                    { type: 'success', text: "Verify_Ticket_Img: src_hash_8f92a..." },
                    { type: 'warning', text: "Rate limit warning on Vision API" },
                    { type: 'success', text: "Concourse routing matrix calculation: OK" },
                    { type: 'error', text: "DB Timeout: Ops_Logistics schema not responding" },
                    { type: 'success', text: "Gemini Prompt Injection: Analyzing vendor stocks" },
                    { type: 'success', text: "OCR Vision Processing: Ticket #99482 verified" },
                    { type: 'success', text: "UPDATE zone_status SET alert=false WHERE id='Z-A1'" },
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
"""

injection_target = "document.addEventListener('DOMContentLoaded', () => {"
if injection_target in html:
    html = html.replace(injection_target, injection_target + "\n" + js_code)
else:
    print("Could not find injection target")
    exit(1)

with open('static/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Success")
