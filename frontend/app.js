/**
 * app.js — Vanilla JS client for Smart Stadium Ops.
 *
 * Zero dependencies. Features:
 *   - Tab-based dashboard navigation with ARIA state management
 *   - Network offline/online detection with accessible system alert
 *   - Phase 2 GenAI-backed incident processing & fan assistance
 *   - Real-time incident log with severity-colored entries
 *   - Character counters, loading states, error handling
 */

(() => {
  "use strict";

  const API_BASE = "https://fifa-backend-api.onrender.com/api/v1";

  // ══════════════════════════════════════════════════════════════════════
  //  DOM REFERENCES
  // ══════════════════════════════════════════════════════════════════════

  const $id = (id) => document.getElementById(id);

  const DOM = {
    // System
    systemAlert: $id("system-alert"),
    alertTitle: $id("system-alert-title"),
    alertMessage: $id("system-alert-message"),
    alertDismiss: $id("system-alert-dismiss"),
    healthBadge: $id("health-badge"),
    connectionDot: $id("connection-indicator"),

    // Tabs
    tabIncidents: $id("tab-incidents"),
    tabFan: $id("tab-fan"),
    tabLogs: $id("tab-logs"),
    panelIncidents: $id("panel-incidents"),
    panelFan: $id("panel-fan"),
    panelLogs: $id("panel-logs"),

    // Incident form
    incidentForm: $id("incident-form"),
    incZone: $id("inc-zone"),
    incSeverity: $id("inc-severity"),
    incDesc: $id("inc-desc"),
    incDescCount: $id("inc-desc-count"),
    incReporter: $id("inc-reporter"),
    incSubmit: $id("inc-submit"),
    incidentResult: $id("incident-result"),

    // Fan form
    fanForm: $id("fan-form"),
    fanLang: $id("fan-lang"),
    fanMatch: $id("fan-match"),
    fanMsg: $id("fan-msg"),
    fanMsgCount: $id("fan-msg-count"),
    fanSubmit: $id("fan-submit"),
    fanResult: $id("fan-result"),

    // Log
    incidentLog: $id("incident-log"),
    logCount: $id("log-count"),
  };

  // ══════════════════════════════════════════════════════════════════════
  //  STATE
  // ══════════════════════════════════════════════════════════════════════

  const state = {
    isOnline: navigator.onLine,
    incidents: [],
    alertDismissed: false,
  };

  // ══════════════════════════════════════════════════════════════════════
  //  NETWORK & API
  // ══════════════════════════════════════════════════════════════════════

  /**
   * Fetch wrapper with JSON handling and structured error extraction.
   * @param {string} endpoint - API path (e.g., "/incidents/process")
   * @param {RequestInit} options - fetch options
   * @returns {Promise<any>} parsed JSON response
   */
  async function apiFetch(endpoint, options = {}) {
    // Implement a client-side timeout as a fallback
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 8000);

    try {
      const res = await fetch(`${API_BASE}${endpoint}`, {
        headers: { "Content-Type": "application/json" },
        signal: controller.signal,
        ...options,
      });
      clearTimeout(timeoutId);

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));

        // Intercept degraded performance or 503/504 errors
        if (
          res.status === 503 ||
          res.status === 504 ||
          (err.detail && err.detail.status === "degraded_performance")
        ) {
          handleOffline();
          throw new Error(
            "Network congestion detected. Switched to Offline Mode.",
          );
        }

        const detail = err.detail;
        if (typeof detail === "object" && detail.message) {
          throw new Error(detail.message);
        }
        throw new Error(
          typeof detail === "string" ? detail : `HTTP ${res.status}`,
        );
      }

      const data = await res.json();
      // If the payload contains a degraded_performance flag (200 OK fallback)
      if (data.status === "degraded_performance") {
        handleOffline();
      }
      return data;
    } catch (error) {
      clearTimeout(timeoutId);
      if (
        error.name === "AbortError" ||
        error.message.includes("Failed to fetch")
      ) {
        handleOffline();
        throw new Error(
          "Network connection dropped. Operating in Offline Mode.",
        );
      }
      throw error;
    }
  }

  // ══════════════════════════════════════════════════════════════════════
  //  OFFLINE DETECTION
  // ══════════════════════════════════════════════════════════════════════

  function showSystemAlert(title, message) {
    DOM.alertTitle.textContent = title;
    DOM.alertMessage.textContent = message;
    DOM.systemAlert.hidden = false;
    state.alertDismissed = false;
  }

  function hideSystemAlert() {
    DOM.systemAlert.hidden = true;
  }

  function handleOnline() {
    state.isOnline = true;
    DOM.connectionDot.className = "connection-dot connection-dot--online";
    DOM.connectionDot.setAttribute("aria-label", "Network status: online");
    DOM.connectionDot.title = "Network: Online";
    hideSystemAlert();
    checkHealth();
  }

  function handleOffline() {
    state.isOnline = false;
    DOM.connectionDot.className = "connection-dot connection-dot--offline";
    DOM.connectionDot.setAttribute("aria-label", "Network status: offline");
    DOM.connectionDot.title = "Network: Offline";
    DOM.healthBadge.textContent = "Offline";
    DOM.healthBadge.className = "badge badge--error";
    DOM.healthBadge.setAttribute("aria-label", "System status: offline");

    if (!state.alertDismissed) {
      showSystemAlert(
        "Network Connection Lost",
        "Stadium network is unavailable. Incident reporting and fan " +
          "assistant services are operating in degraded mode. Reports " +
          "will be queued and submitted when connectivity is restored.",
      );
    }
  }

  window.addEventListener("online", handleOnline);
  window.addEventListener("offline", handleOffline);

  DOM.alertDismiss.addEventListener("click", () => {
    hideSystemAlert();
    state.alertDismissed = true;
  });

  // ══════════════════════════════════════════════════════════════════════
  //  TAB NAVIGATION
  // ══════════════════════════════════════════════════════════════════════

  const TABS = [
    { btn: DOM.tabIncidents, panel: DOM.panelIncidents },
    { btn: DOM.tabFan, panel: DOM.panelFan },
    { btn: DOM.tabLogs, panel: DOM.panelLogs },
  ];

  function activateTab(activeBtn) {
    TABS.forEach(({ btn, panel }) => {
      const isActive = btn === activeBtn;
      btn.classList.toggle("tab-btn--active", isActive);
      btn.setAttribute("aria-selected", String(isActive));
      panel.hidden = !isActive;
      panel.classList.toggle("panel--active", isActive);
    });
  }

  TABS.forEach(({ btn }) => {
    btn.addEventListener("click", () => activateTab(btn));
  });

  // Keyboard navigation (arrow keys between tabs)
  document.querySelector(".tab-bar").addEventListener("keydown", (e) => {
    const btns = TABS.map((t) => t.btn);
    const idx = btns.indexOf(document.activeElement);
    if (idx < 0) return;

    let next = idx;
    if (e.key === "ArrowRight" || e.key === "ArrowDown") {
      next = (idx + 1) % btns.length;
    } else if (e.key === "ArrowLeft" || e.key === "ArrowUp") {
      next = (idx - 1 + btns.length) % btns.length;
    } else {
      return;
    }

    e.preventDefault();
    btns[next].focus();
    activateTab(btns[next]);
  });

  // ══════════════════════════════════════════════════════════════════════
  //  CHARACTER COUNTERS
  // ══════════════════════════════════════════════════════════════════════

  function attachCounter(textarea, countEl, max) {
    const update = () => {
      const len = textarea.value.length;
      countEl.textContent = `${len} / ${max}`;
    };
    textarea.addEventListener("input", update);
    update();
  }

  attachCounter(DOM.incDesc, DOM.incDescCount, 4000);
  attachCounter(DOM.fanMsg, DOM.fanMsgCount, 1000);

  // ══════════════════════════════════════════════════════════════════════
  //  BUTTON LOADING STATE
  // ══════════════════════════════════════════════════════════════════════

  function setLoading(btn, busy) {
    const textSpan = btn.querySelector(".btn__text");
    const spinnerSpan = btn.querySelector(".btn__spinner");
    btn.disabled = busy;
    btn.setAttribute("aria-busy", String(busy));
    if (textSpan)
      textSpan.textContent = busy
        ? "Processing…"
        : btn.dataset.label || "Submit";
    if (spinnerSpan) spinnerSpan.hidden = !busy;
  }

  // Store original labels
  document.querySelectorAll(".btn").forEach((btn) => {
    const textSpan = btn.querySelector(".btn__text");
    if (textSpan) btn.dataset.label = textSpan.textContent;
  });

  // ══════════════════════════════════════════════════════════════════════
  //  SEVERITY HELPERS
  // ══════════════════════════════════════════════════════════════════════

  function severityTag(level) {
    return `<span class="severity-tag severity-tag--${level}" role="img" aria-label="Severity: ${level}">${level}</span>`;
  }

  function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
  }

  // ══════════════════════════════════════════════════════════════════════
  //  HEALTH CHECK
  // ══════════════════════════════════════════════════════════════════════

  async function checkHealth() {
    try {
      const data = await apiFetch("/health");
      DOM.healthBadge.textContent = `v${data.version} · ${data.prompts_loaded} prompts`;
      DOM.healthBadge.className = "badge badge--ok";
      DOM.healthBadge.setAttribute(
        "aria-label",
        `System status: operational, version ${data.version}`,
      );

      if (state.isOnline) {
        DOM.connectionDot.className = "connection-dot connection-dot--online";
        DOM.connectionDot.setAttribute("aria-label", "Network status: online");
      }
    } catch {
      DOM.healthBadge.textContent = "Unreachable";
      DOM.healthBadge.className = "badge badge--error";
      DOM.healthBadge.setAttribute("aria-label", "System status: unreachable");
    }
  }

  // ══════════════════════════════════════════════════════════════════════
  //  INCIDENT LOG
  // ══════════════════════════════════════════════════════════════════════

  function addToIncidentLog(incident) {
    state.incidents.unshift(incident);

    // Clear empty state on first entry
    if (state.incidents.length === 1) {
      DOM.incidentLog.innerHTML = "";
    }

    const time = new Date(
      incident.acknowledged_at || Date.now(),
    ).toLocaleTimeString();
    const entry = document.createElement("div");
    entry.className = `log-entry log-entry--${escapeHtml(incident.severity)}`;
    entry.setAttribute("role", "article");
    entry.setAttribute(
      "aria-label",
      `Incident ${incident.incident_id}, severity ${incident.severity}, zone ${incident.zone}`,
    );
    entry.innerHTML = `
            <span class="log-entry__id">${escapeHtml(incident.incident_id)}</span>
            <span class="log-entry__desc">
                ${severityTag(incident.severity)}
                ${escapeHtml(incident.zone)}
            </span>
            <span class="log-entry__time">${escapeHtml(time)}</span>
        `;

    DOM.incidentLog.prepend(entry);
    DOM.logCount.textContent = `${state.incidents.length} event${state.incidents.length !== 1 ? "s" : ""}`;
  }

  // ══════════════════════════════════════════════════════════════════════
  //  RENDER: Incident AI Response
  // ══════════════════════════════════════════════════════════════════════

  function renderIncidentResponse(data) {
    const ta = data.task_assignment || {};
    const units = (ta.response_units || [])
      .map((u) => `<li>${escapeHtml(u)}</li>`)
      .join("");
    const steps = (ta.action_steps || [])
      .map((s) => `<li>${escapeHtml(s)}</li>`)
      .join("");

    let escalationHtml = "";
    if (ta.escalation_required) {
      escalationHtml = `
                <div class="escalation-banner" role="alert">
                    <span aria-hidden="true">🚨</span>
                    ESCALATION REQUIRED — Route to venue command immediately
                </div>
            `;
    }

    DOM.incidentResult.innerHTML = `
            <div class="result-card" role="region" aria-label="Incident triage result">
                <div class="result-card__title">
                    ${severityTag(data.severity)}
                    <span>Task Assignment — ${escapeHtml(data.incident_id)}</span>
                </div>

                <div class="result-field">
                    <span class="result-field__label">Zone</span>
                    <span class="result-field__value">${escapeHtml(data.zone)}</span>
                </div>
                <div class="result-field">
                    <span class="result-field__label">Crowd Impact</span>
                    <span class="result-field__value">${escapeHtml(data.crowd_impact)}</span>
                </div>
                <div class="result-field">
                    <span class="result-field__label">Est. Resolution</span>
                    <span class="result-field__value">${ta.estimated_resolution_minutes ?? "—"} min</span>
                </div>

                ${
                  units
                    ? `
                <div class="result-section">
                    <div class="result-section__title">Response Units</div>
                    <ul class="result-list">${units}</ul>
                </div>`
                    : ""
                }

                ${
                  steps
                    ? `
                <div class="result-section">
                    <div class="result-section__title">Action Steps</div>
                    <ol class="result-list">${steps}</ol>
                </div>`
                    : ""
                }

                ${
                  ta.commander_notes
                    ? `
                <div class="result-section">
                    <div class="result-section__title">Commander Notes</div>
                    <p style="font-size:let(--fs-sm);line-height:1.6;">${escapeHtml(ta.commander_notes)}</p>
                </div>`
                    : ""
                }

                ${escalationHtml}
            </div>
        `;

    // Also add to the live log
    addToIncidentLog(data);
  }

  function renderIncidentError(message) {
    DOM.incidentResult.innerHTML = `
            <div class="result-card result-card--error" role="alert">
                <div class="result-card__title" style="color:let(--danger);">
                    <span aria-hidden="true">❌</span> Error
                </div>
                <p style="font-size:let(--fs-sm);">${escapeHtml(message)}</p>
            </div>
        `;
  }

  // ══════════════════════════════════════════════════════════════════════
  //  RENDER: Fan AI Response
  // ══════════════════════════════════════════════════════════════════════

  function renderFanResponse(data) {
    let cacheHtml = "";
    if (data.cache_hit) {
      cacheHtml = `<span class="cache-badge">⚡ Cache Hit</span>`;
    }

    let escalationHtml = "";
    if (data.escalated) {
      escalationHtml = `
                <div class="escalation-banner" role="alert">
                    <span aria-hidden="true">🚨</span>
                    SAFETY CONCERN — Escalated to Incident Commander
                </div>
            `;
    }

    DOM.fanResult.innerHTML = `
            <div class="result-card" role="region" aria-label="Fan assistant response">
                <div class="result-card__title">
                    <span aria-hidden="true">💬</span>
                    Assistant Response
                    ${cacheHtml}
                </div>

                <div class="result-field">
                    <span class="result-field__label">Language</span>
                    <span class="result-field__value">${escapeHtml(data.detected_language)}</span>
                </div>

                <div class="result-section">
                    <p style="font-size:let(--fs-base);line-height:1.7;white-space:pre-wrap;">${escapeHtml(data.reply)}</p>
                </div>

                ${escalationHtml}
            </div>
        `;
  }

  function renderFanError(message) {
    DOM.fanResult.innerHTML = `
            <div class="result-card result-card--error" role="alert">
                <div class="result-card__title" style="color:let(--danger);">
                    <span aria-hidden="true">❌</span> Error
                </div>
                <p style="font-size:let(--fs-sm);">${escapeHtml(message)}</p>
            </div>
        `;
  }

  // ══════════════════════════════════════════════════════════════════════
  //  FORM HANDLERS
  // ══════════════════════════════════════════════════════════════════════

  // ── Incident Form → POST /incidents/process ─────────────────────────
  DOM.incidentForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!state.isOnline) {
      renderIncidentError(
        "Network offline — cannot submit incident. Please try again when connection is restored.",
      );
      return;
    }

    setLoading(DOM.incSubmit, true);

    try {
      const payload = {
        zone: DOM.incZone.value.trim(),
        description: DOM.incDesc.value.trim(),
        reporter: DOM.incReporter.value.trim() || null,
      };

      // Client-side validation
      if (!payload.zone || !payload.description) {
        renderIncidentError("Zone and description are required.");
        return;
      }

      const data = await apiFetch("/incidents/process", {
        method: "POST",
        body: JSON.stringify(payload),
      });

      renderIncidentResponse(data);
      DOM.incidentForm.reset();
      DOM.incDescCount.textContent = "0 / 4000";
    } catch (err) {
      renderIncidentError(err.message || "An unexpected error occurred.");
    } finally {
      setLoading(DOM.incSubmit, false);
    }
  });

  // ── Fan Form → POST /fan/assist ─────────────────────────────────────
  DOM.fanForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!state.isOnline) {
      renderFanError(
        "Network offline — cannot reach assistant. Please visit the nearest Info Desk.",
      );
      return;
    }

    setLoading(DOM.fanSubmit, true);

    try {
      const payload = {
        message: DOM.fanMsg.value.trim(),
        language: DOM.fanLang.value,
        match_id: DOM.fanMatch.value.trim() || null,
      };

      if (!payload.message) {
        renderFanError("Please enter a question.");
        return;
      }

      const data = await apiFetch("/fan/assist", {
        method: "POST",
        body: JSON.stringify(payload),
      });

      renderFanResponse(data);
      DOM.fanForm.reset();
      DOM.fanMsgCount.textContent = "0 / 1000";
    } catch (err) {
      renderFanError(err.message || "An unexpected error occurred.");
    } finally {
      setLoading(DOM.fanSubmit, false);
    }
  });

  // ══════════════════════════════════════════════════════════════════════
  //  INIT & SERVICE WORKER
  // ══════════════════════════════════════════════════════════════════════

  // Register Service Worker and aggressively pre-fetch static data
  if ("serviceWorker" in navigator) {
    window.addEventListener("load", () => {
      navigator.serviceWorker
        .register("/sw.js")
        .then((registration) => {
          console.log(
            "[App] ServiceWorker registration successful:",
            registration.scope,
          );

          // Pre-fetch critical static JSON data during low load
          const staticDataUrls = [
            "/api/v1/health",
            // Add other static JSON paths to aggressively hydrate the cache
          ];
          staticDataUrls.forEach((url) => fetch(url).catch(() => {}));
        })
        .catch((err) => {});
    });
  }

  // Set initial network state
  if (navigator.onLine) {
    DOM.connectionDot.className = "connection-dot connection-dot--online";
    DOM.connectionDot.setAttribute("aria-label", "Network status: online");
  } else {
    handleOffline();
  }

  // Initial health check + polling
  checkHealth();
  setInterval(checkHealth, 30_000);
})();
