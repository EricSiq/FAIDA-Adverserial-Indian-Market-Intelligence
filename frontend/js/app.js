document.addEventListener("DOMContentLoaded", () => {
  const toneSlider = document.getElementById("tone-slider");
  const toneBadge = document.getElementById("tone-badge");
  const thesisForm = document.getElementById("thesis-form");
  const userInput = document.getElementById("user-input");
  const submitBtn = document.getElementById("submit-btn");
  const btnText = document.getElementById("btn-text");
  const btnSpinner = document.getElementById("btn-spinner");
  const chatStream = document.getElementById("chat-stream");
  const welcomeCard = document.getElementById("welcome-card");

  const lkbSymbolBadge = document.getElementById("lkb-symbol-badge");
  const frictionScoreVal = document.getElementById("friction-score-val");
  const frictionProgress = document.getElementById("friction-progress");
  const frictionDesc = document.getElementById("friction-desc");
  const lkbTbody = document.getElementById("lkb-tbody");
  const evidenceBox = document.getElementById("evidence-box");
  const evidenceId = document.getElementById("evidence-id");
  const evidenceSource = document.getElementById("evidence-source");
  const evidenceContext = document.getElementById("evidence-context");

  // Settings Modal
  const providerBtn = document.getElementById("provider-btn");
  const providerLabel = document.getElementById("provider-label");
  const settingsModal = document.getElementById("settings-modal");
  const closeSettingsBtn = document.getElementById("close-settings-btn");
  const saveSettingsBtn = document.getElementById("save-settings-btn");
  const settingProviderSelect = document.getElementById("setting-provider-select");
  const settingOllamaModel = document.getElementById("setting-ollama-model");
  const settingGroqKey = document.getElementById("setting-groq-key");

  // History Modal Elements
  const historyBtn = document.getElementById("history-btn");
  const historyModal = document.getElementById("history-modal");
  const closeHistoryBtn = document.getElementById("close-history-btn");
  const historyList = document.getElementById("history-list");

  let currentLKBFacts = [];

  const TONE_NAMES = {
    1: "Level 1: Socratic Educator (Gentle & Beginner Analogies)",
    2: "Level 2: Mindful Mentor (Balanced Caution & Insights)",
    3: "Level 3: Pragmatic Risk Officer (Default)",
    4: "Level 4: Cynical Contrarian (Narrative Skeptic)",
    5: "Level 5: Hardcore Short-Seller (Forensic Roaster)",
    6: "Level 6: Quant Forensic (Zero Fluff, Pure Stats & Ratios)"
  };

  // Tone Slider Event
  toneSlider.addEventListener("input", (e) => {
    const val = parseInt(e.target.value, 10);
    toneBadge.textContent = TONE_NAMES[val] || `Level ${val}`;
  });

  // Suggestion chips
  document.querySelectorAll(".chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      userInput.value = chip.dataset.query;
      thesisForm.dispatchEvent(new Event("submit"));
    });
  });

  // Settings Modal Open/Close
  providerBtn.addEventListener("click", () => {
    settingsModal.classList.remove("hidden");
  });
  closeSettingsBtn.addEventListener("click", () => {
    settingsModal.classList.add("hidden");
  });

  // History Modal Open/Close & Fetch
  historyBtn.addEventListener("click", async () => {
    historyModal.classList.remove("hidden");
    historyList.innerHTML = '<p class="empty-table-msg">Loading saved theses...</p>';
    try {
      const res = await fetch("/api/history");
      const items = await res.json();
      if (!items || items.length === 0) {
        historyList.innerHTML = '<p class="empty-table-msg">No investment decisions recorded yet.</p>';
        return;
      }
      historyList.innerHTML = "";
      items.forEach((item) => {
        const card = document.createElement("div");
        card.className = "history-card";
        const dateStr = item.created_at ? new Date(item.created_at).toLocaleDateString() : "";
        card.innerHTML = `
          <div class="history-card-left">
            <div class="history-title">
              <span>${escapeHtml(item.symbol)} (${escapeHtml(item.exchange)})</span>
              <span class="history-action-badge ${escapeHtml(item.action)}">${escapeHtml(item.action)}</span>
              ${item.target_price ? `<span style="font-size:12px; color:var(--text-muted);">@ ₹${item.target_price}</span>` : ""}
            </div>
            <div class="history-verdict">${escapeHtml(item.headline_verdict || "")}</div>
          </div>
          <div class="history-card-right">
            <div class="history-score">${item.friction_score}/100</div>
            <div class="history-date">${dateStr}</div>
          </div>
        `;
        card.addEventListener("click", async () => {
          try {
            const detailRes = await fetch(`/api/history/${item.id}`);
            const detail = await detailRes.json();
            historyModal.classList.add("hidden");
            if (welcomeCard) welcomeCard.style.display = "none";
            renderAnalysisResponse({
              adversarial_counter_thesis: detail.pre_mortem.headline_verdict + "\n\n" + (detail.pre_mortem.bearish_risks.map(r => `### ${r.risk_title}\n${r.argument}`).join("\n\n")),
              elapsed_seconds: 0.0,
              pre_mortem: detail.pre_mortem,
              lkb_packet: detail.lkb_packet
            });
            updateLKBPanel(detail.lkb_packet, detail.pre_mortem);
          } catch (err) {
            alert("Error loading past decision: " + err);
          }
        });
        historyList.appendChild(card);
      });
    } catch (err) {
      historyList.innerHTML = `<p class="empty-table-msg" style="color:var(--accent-red)">Error loading history: ${err.message}</p>`;
    }
  });

  closeHistoryBtn.addEventListener("click", () => {
    historyModal.classList.add("hidden");
  });

  // Load Initial Config
  fetch("/api/config")
    .then((r) => r.json())
    .then((cfg) => {
      if (cfg.active_provider === "groq") {
        providerLabel.textContent = "Groq: " + cfg.groq_model;
      } else {
        providerLabel.textContent = "Ollama: " + cfg.default_local_model;
      }
      settingProviderSelect.value = cfg.active_provider || "ollama";
      settingOllamaModel.value = cfg.default_local_model || "gemma4:e4b";
    })
    .catch((err) => console.log("Config load error:", err));

  // Load India VIX Weather Indicator
  function loadVixGauge() {
    fetch("/api/macro/vix")
      .then((r) => r.json())
      .then((vix) => {
        const dot = document.getElementById("vix-dot");
        const label = document.getElementById("vix-label");
        const pill = document.getElementById("vix-pill");
        if (dot && label && pill) {
          dot.style.backgroundColor = vix.color;
          dot.style.boxShadow = `0 0 6px ${vix.color}`;
          label.textContent = `India VIX: ${vix.vix_value}`;
          pill.title = `${vix.regime_label}: ${vix.description}`;
        }
      })
      .catch((err) => console.log("VIX load error:", err));
  }
  loadVixGauge();

  saveSettingsBtn.addEventListener("click", async () => {
    const active_provider = settingProviderSelect.value;
    const default_local_model = settingOllamaModel.value.trim();
    const groq_api_key = settingGroqKey.value.trim();

    try {
      const res = await fetch("/api/config", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          active_provider,
          default_local_model,
          groq_api_key: groq_api_key || undefined
        })
      });
      const data = await res.json();
      if (data.status === "ok") {
        providerLabel.textContent =
          active_provider === "groq"
            ? "Groq: llama-3.3-70b"
            : "Ollama: " + default_local_model;
        settingsModal.classList.add("hidden");
      }
    } catch (err) {
      alert("Failed to save settings: " + err);
    }
  });

  // Submit Thesis Form
  thesisForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const query = userInput.value.trim();
    if (!query) return;

    if (welcomeCard) welcomeCard.style.display = "none";

    // 1. Render User Bubble
    appendUserBubble(query);
    userInput.value = "";

    // 2. Set Loading UI
    setLoading(true);

    try {
      const tone = parseInt(toneSlider.value, 10);
      const resp = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, tone_level: tone })
      });

      if (!resp.ok) {
        throw new Error(`Server returned status ${resp.status}`);
      }

      const data = await resp.json();
      renderAnalysisResponse(data);
      updateLKBPanel(data.lkb_packet, data.pre_mortem);
    } catch (err) {
      appendErrorBubble("Error stress-testing thesis: " + err.message);
    } finally {
      setLoading(false);
    }
  });

  function setLoading(loading) {
    if (loading) {
      submitBtn.disabled = true;
      btnText.textContent = "Scraping & Red-Teaming...";
      btnSpinner.classList.remove("hidden");
    } else {
      submitBtn.disabled = false;
      btnText.textContent = "Stress Test Thesis";
      btnSpinner.classList.add("hidden");
    }
  }

  function appendUserBubble(text) {
    const div = document.createElement("div");
    div.className = "user-thesis-bubble";
    div.innerHTML = `<strong>Your Proposed Thesis:</strong> ${escapeHtml(text)}`;
    chatStream.appendChild(div);
    chatStream.scrollTop = chatStream.scrollHeight;
  }

  function appendErrorBubble(text) {
    const div = document.createElement("div");
    div.className = "adversarial-card";
    div.style.borderLeftColor = "#ef4444";
    div.innerHTML = `<p style="color: #ef4444;">${escapeHtml(text)}</p>`;
    chatStream.appendChild(div);
    chatStream.scrollTop = chatStream.scrollHeight;
  }

  function renderAnalysisResponse(data) {
    const pm = data.pre_mortem;
    const lkb = data.lkb_packet;
    const container = document.createElement("div");
    container.className = "analysis-turn";

    // Format LLM text with clickable [LKB-XX] badges
    let formattedDebate = escapeHtml(data.adversarial_counter_thesis);
    formattedDebate = formattedDebate.replace(/\[(LKB-\d{2})\]/g, (match, id) => {
      return `<span class="citation-badge" data-fact-id="${id}">[${id}]</span>`;
    });

    // Cognitive Biases HTML
    let biasesHtml = "";
    if (pm.detected_biases && pm.detected_biases.length > 0) {
      biasesHtml = `
        <div class="bias-section">
          <h4>⚠️ Cognitive Biases & Behavioral Traps Detected in Your Rationale:</h4>
          ${pm.detected_biases.map(b => `
            <div class="bias-card">
              <div class="bias-title">${escapeHtml(b.bias_name)} (${escapeHtml(b.severity)} Severity)</div>
              <p class="bias-trap"><strong>The Trap:</strong> ${escapeHtml(b.psychological_trap)}</p>
              <p class="bias-reframing"><strong>💡 Reframing Check:</strong> ${escapeHtml(b.reframing_advice)}</p>
            </div>
          `).join("")}
        </div>
      `;
    }

    // Macro Shock Simulator HTML
    const simulatorHtml = `
      <div class="simulator-card" id="sim-card-${data.session_id}">
        <div class="simulator-header">
          <span>⚡ Interactive Macro Shock Simulator ("What-If?" Stress Tester)</span>
        </div>
        <div class="sim-buttons">
          <button class="sim-btn" data-scenario="CRUDE_SURGE" data-sym="${escapeHtml(data.thesis.symbol)}">🛢️ Crude Spikes $95+</button>
          <button class="sim-btn" data-scenario="RBI_RATE_HIKE" data-sym="${escapeHtml(data.thesis.symbol)}">🏦 RBI Hikes Repo +25bps</button>
          <button class="sim-btn" data-scenario="INR_DEPRECIATION" data-sym="${escapeHtml(data.thesis.symbol)}">💵 USD/INR Weakens ₹86.50</button>
          <button class="sim-btn" data-scenario="MARGIN_COMPRESSION" data-sym="${escapeHtml(data.thesis.symbol)}">📉 Margins Drop -250bps</button>
        </div>
        <div class="sim-result-panel hidden" id="sim-result-${data.session_id}">
          <div class="sim-impact-tag" id="sim-impact-${data.session_id}"></div>
          <div id="sim-mech-${data.session_id}" style="color:var(--text-secondary);"></div>
          <div id="sim-warning-${data.session_id}" style="color:var(--accent-orange); font-size:11.5px;"></div>
        </div>
      </div>
    `;

    const cardHtml = `
      <div class="adversarial-card">
        <div class="verdict-header">
          <span class="verdict-badge">ADVERSARIAL RED-TEAM VERDICT</span>
          <span style="font-size: 11px; color: var(--text-muted);">Latency: ${data.elapsed_seconds}s</span>
        </div>

        <h3 style="font-size: 15px; color: ${pm.friction_score >= 70 ? 'var(--accent-red)' : 'var(--accent-orange)'};">
          ${escapeHtml(pm.headline_verdict)}
        </h3>

        <div class="adversarial-body">${formattedDebate}</div>

        ${biasesHtml}

        ${simulatorHtml}

        <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid var(--border-subtle);">
          <strong style="font-size: 12px; color: var(--text-primary);">💡 Retail Investor Pre-Mortem Takeaways:</strong>
          <ul style="margin: 6px 0 0 18px; font-size: 12px; color: var(--text-secondary); line-height: 1.5;">
            ${pm.educational_takeaways.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
          </ul>
        </div>

        <div class="action-buttons-row">
          <button class="export-btn" onclick="window.open('/api/export/${data.session_id}', '_blank')">
            <span>📄 Export Pre-Mortem One-Pager (Print/PDF)</span>
          </button>
        </div>
      </div>
    `;

    container.innerHTML = cardHtml;
    chatStream.appendChild(container);
    chatStream.scrollTop = chatStream.scrollHeight;

    // Attach click handlers to citation badges
    container.querySelectorAll(".citation-badge").forEach((badge) => {
      badge.addEventListener("click", () => {
        const factId = badge.dataset.factId;
        highlightFactRow(factId);
      });
    });

    // Attach click handlers to simulator scenario buttons
    container.querySelectorAll(".sim-btn").forEach((btn) => {
      btn.addEventListener("click", async () => {
        container.querySelectorAll(".sim-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        const scenario = btn.dataset.scenario;
        const sym = btn.dataset.sym;
        const resPanel = document.getElementById(`sim-result-${data.session_id}`);
        const impactTag = document.getElementById(`sim-impact-${data.session_id}`);
        const mechText = document.getElementById(`sim-mech-${data.session_id}`);
        const warnText = document.getElementById(`sim-warning-${data.session_id}`);

        resPanel.classList.remove("hidden");
        impactTag.textContent = "Calculating macroeconomic shock impact...";
        mechText.textContent = "";
        warnText.textContent = "";

        try {
          const sRes = await fetch("/api/simulate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ symbol: sym, scenario_type: scenario })
          });
          const sData = await sRes.json();
          impactTag.textContent = `${sData.scenario_title} → ${sData.estimated_impact}`;
          mechText.textContent = sData.mechanism;
          warnText.textContent = `⚠️ Red-Team Warning: ${sData.red_team_warning}`;
        } catch (sErr) {
          impactTag.textContent = "Simulation error: " + sErr.message;
        }
      });
    });
  }

  function updateLKBPanel(lkbPacket, preMortem) {
    if (!lkbPacket) return;

    currentLKBFacts = lkbPacket.facts || [];
    lkbSymbolBadge.textContent = `${lkbPacket.symbol} (${lkbPacket.exchange})`;

    // Update Friction Gauge
    const score = preMortem.friction_score || 50;
    frictionScoreVal.textContent = `${score} / 100`;
    frictionProgress.style.width = `${score}%`;

    if (score >= 70) {
      frictionScoreVal.style.color = "var(--accent-red)";
      frictionDesc.textContent = "High Risk: Substantial headwind signals and valuation stretch against thesis.";
    } else if (score >= 45) {
      frictionScoreVal.style.color = "var(--accent-orange)";
      frictionDesc.textContent = "Moderate Friction: Mixed technical and fundamental balance.";
    } else {
      frictionScoreVal.style.color = "var(--accent-green)";
      frictionDesc.textContent = "Low Adversarial Friction: Thesis has reasonable statistical alignment.";
    }

    // Populate LKB Table
    lkbTbody.innerHTML = "";
    currentLKBFacts.forEach((fact) => {
      const tr = document.createElement("tr");
      tr.id = `row-${fact.id}`;
      tr.innerHTML = `
        <td class="fact-id">${fact.id}</td>
        <td><span class="category-tag">${fact.category}</span></td>
        <td><strong>${escapeHtml(fact.metric)}</strong></td>
        <td>${escapeHtml(String(fact.value))} ${escapeHtml(fact.unit)}</td>
        <td><span class="src-tag">${escapeHtml(fact.source)}</span></td>
      `;

      tr.addEventListener("click", () => {
        highlightFactRow(fact.id);
      });

      lkbTbody.appendChild(tr);
    });
  }

  function highlightFactRow(factId) {
    // Clear previous highlight
    document.querySelectorAll(".lkb-table tr").forEach((r) => r.classList.remove("highlighted"));

    const row = document.getElementById(`row-${factId}`);
    if (row) {
      row.classList.add("highlighted");
      row.scrollIntoView({ behavior: "smooth", block: "center" });
    }

    const fact = currentLKBFacts.find((f) => f.id === factId);
    if (fact) {
      evidenceId.textContent = `CITATION: [${fact.id}] ${fact.metric}`;
      evidenceSource.textContent = `${fact.source} (${fact.category})`;
      evidenceContext.textContent = fact.context || `Value: ${fact.value} ${fact.unit}`;
    }
  }

  function escapeHtml(str) {
    if (!str) return "";
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }
});
