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
  const newThesisBtn = document.getElementById("new-thesis-btn");

  const lkbSymbolBadge = document.getElementById("lkb-symbol-badge");
  const frictionScoreVal = document.getElementById("friction-score-val");
  const frictionProgress = document.getElementById("friction-progress");
  const frictionDesc = document.getElementById("friction-desc");
  const lkbTbody = document.getElementById("lkb-tbody");
  const countAll = document.getElementById("count-all");
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
  let activeCategory = "ALL";
  let activeStepperTimers = [];

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
              session_id: detail.session_id,
              adversarial_counter_thesis: detail.pre_mortem.headline_verdict + "\n\n" + (detail.pre_mortem.bearish_risks.map(r => `### ${r.risk_title}\n${r.argument}`).join("\n\n")),
              elapsed_seconds: 0.0,
              pre_mortem: detail.pre_mortem,
              lkb_packet: detail.lkb_packet,
              thesis: {
                symbol: detail.symbol,
                exchange: detail.exchange,
                action: detail.action
              }
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

  // Load Global Macro Telemetry & India VIX
  async function loadMacroTelemetry() {
    try {
      const [vixRes, macroRes] = await Promise.all([
        fetch("/api/macro/vix").then(r => r.json()).catch(() => null),
        fetch("/api/macro/global").then(r => r.json()).catch(() => null)
      ]);

      if (vixRes) {
        const dot = document.getElementById("vix-dot");
        const label = document.getElementById("vix-label");
        const pill = document.getElementById("vix-pill");
        if (dot && label && pill) {
          dot.style.backgroundColor = vixRes.color || "var(--accent-green)";
          dot.style.boxShadow = `0 0 6px ${vixRes.color || "var(--accent-green)"}`;
          label.textContent = `India VIX: ${vixRes.vix_value}`;
          pill.title = `${vixRes.regime_label}: ${vixRes.description}`;
        }
        document.querySelectorAll(".macro-vix-val").forEach((el) => {
          el.textContent = `${vixRes.vix_value} (${vixRes.regime_label || "Normal"})`;
        });
      }

      if (macroRes) {
        if (macroRes.brent_crude_usd) {
          const valStr = `$${macroRes.brent_crude_usd.toFixed(2)}`;
          document.querySelectorAll(".macro-brent-val").forEach((el) => {
            el.textContent = valStr;
          });
        }
        if (macroRes.us_10y_yield_pct) {
          const valStr = `${macroRes.us_10y_yield_pct.toFixed(2)}%`;
          document.querySelectorAll(".macro-us10y-val").forEach((el) => {
            el.textContent = valStr;
          });
        }
        if (macroRes.us_dollar_index) {
          const valStr = `${macroRes.us_dollar_index.toFixed(1)}`;
          document.querySelectorAll(".macro-dxy-val").forEach((el) => {
            el.textContent = valStr;
          });
        }
      }
    } catch (err) {
      console.log("Macro telemetry load error:", err);
    }
  }
  loadMacroTelemetry();

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

  // LKB Category Filter Chips
  document.querySelectorAll(".filter-chip").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".filter-chip").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      activeCategory = (btn.dataset.category || "ALL").toUpperCase();
      renderLKBTable();
    });
  });

  // Reset / New Thesis Function
  function resetWorkspace() {
    chatStream.innerHTML = "";
    if (welcomeCard) {
      welcomeCard.style.display = "block";
      chatStream.appendChild(welcomeCard);
    }
    currentLKBFacts = [];
    lkbSymbolBadge.textContent = "NO ASSET SELECTED";
    frictionScoreVal.textContent = "-- / 100";
    frictionScoreVal.style.color = "var(--text-primary)";
    frictionProgress.style.width = "0%";
    frictionDesc.textContent = "Awaiting investment hypothesis to measure market headwinds...";
    if (countAll) countAll.textContent = "0";
    lkbTbody.innerHTML = `
      <tr>
        <td colspan="5" class="empty-table-msg">
          Submit an investment thesis to inspect real-time NSE & Screener facts.
        </td>
      </tr>
    `;
    evidenceId.textContent = "CITATION INSPECTOR";
    evidenceSource.textContent = "--";
    evidenceContext.textContent = "Click any [LKB-XX] citation badge in the debate to verify the mathematical ground-truth.";
    userInput.value = "";
    userInput.focus();
  }

  if (newThesisBtn) {
    newThesisBtn.addEventListener("click", resetWorkspace);
  }

  // Keyboard Shortcuts
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      settingsModal.classList.add("hidden");
      historyModal.classList.add("hidden");
    }
    if (e.ctrlKey && e.key.toLowerCase() === "n") {
      e.preventDefault();
      resetWorkspace();
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

    // 2. Render Swarm Progress Stepper
    const stepperCard = createSwarmStepper();
    chatStream.appendChild(stepperCard);
    chatStream.scrollTop = chatStream.scrollHeight;
    startStepperAnimation();

    // 3. Set Loading UI
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
      clearStepperTimers();
      stepperCard.remove();

      renderAnalysisResponse(data);
      updateLKBPanel(data.lkb_packet, data.pre_mortem);
    } catch (err) {
      clearStepperTimers();
      stepperCard.remove();
      appendErrorBubble("Error stress-testing thesis: " + err.message);
    } finally {
      setLoading(false);
    }
  });

  function createSwarmStepper() {
    const card = document.createElement("div");
    card.className = "swarm-stepper";
    card.id = "active-stepper";
    card.innerHTML = `
      <div class="stepper-header">
        <span>ADVERSARIAL SWARM TELEMETRY</span>
        <span style="font-size: 11px; color: var(--accent-blue);">Live Market Ingestion Active</span>
      </div>
      <div class="stepper-steps-list">
        <div class="stepper-step active" id="step-1">
          <div class="step-icon">1</div>
          <div class="step-label">Ingesting Live NSE Quotes & 52-Week Percentiles...</div>
        </div>
        <div class="stepper-step" id="step-2">
          <div class="step-icon">2</div>
          <div class="step-label">Auditing Screener.in 3-Year CFO/PAT Accrual Forensics...</div>
        </div>
        <div class="stepper-step" id="step-3">
          <div class="step-icon">3</div>
          <div class="step-label">Cross-referencing BSE Filings & Global Macro Drivers...</div>
        </div>
        <div class="stepper-step" id="step-4">
          <div class="step-icon">4</div>
          <div class="step-label">Activating Red-Team Adversarial Swarm...</div>
        </div>
      </div>
    `;
    return card;
  }

  function startStepperAnimation() {
    clearStepperTimers();
    const t1 = setTimeout(() => {
      const s1 = document.getElementById("step-1");
      const s2 = document.getElementById("step-2");
      if (s1 && s2) {
        s1.className = "stepper-step done";
        s1.querySelector(".step-icon").textContent = "✓";
        s2.className = "stepper-step active";
      }
    }, 450);

    const t2 = setTimeout(() => {
      const s2 = document.getElementById("step-2");
      const s3 = document.getElementById("step-3");
      if (s2 && s3) {
        s2.className = "stepper-step done";
        s2.querySelector(".step-icon").textContent = "✓";
        s3.className = "stepper-step active";
      }
    }, 1100);

    const t3 = setTimeout(() => {
      const s3 = document.getElementById("step-3");
      const s4 = document.getElementById("step-4");
      if (s3 && s4) {
        s3.className = "stepper-step done";
        s3.querySelector(".step-icon").textContent = "✓";
        s4.className = "stepper-step active";
      }
    }, 1900);

    activeStepperTimers = [t1, t2, t3];
  }

  function clearStepperTimers() {
    activeStepperTimers.forEach(t => clearTimeout(t));
    activeStepperTimers = [];
  }

  function setLoading(loading) {
    if (loading) {
      submitBtn.disabled = true;
      btnText.textContent = "Swarm Ingesting...";
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
    div.innerHTML = `<strong>Your Proposed Thesis:</strong> ${escapeHtml(stripEmojis(text))}`;
    chatStream.appendChild(div);
    requestAnimationFrame(() => {
      chatStream.scrollTop = chatStream.scrollHeight;
    });
  }

  function appendErrorBubble(text) {
    const div = document.createElement("div");
    div.className = "adversarial-card";
    div.style.borderLeftColor = "#ef4444";
    div.innerHTML = `<p style="color: #ef4444;">${escapeHtml(stripEmojis(text))}</p>`;
    chatStream.appendChild(div);
    requestAnimationFrame(() => {
      chatStream.scrollTop = chatStream.scrollHeight;
    });
  }

  function renderAnalysisResponse(data) {
    const pm = data.pre_mortem;
    const container = document.createElement("div");
    container.className = "analysis-turn";

    // Format LLM text with Markdown rendering, citation badges, and clean corporate styling
    const formattedDebate = formatMarkdown(data.adversarial_counter_thesis);

    // Cognitive Biases HTML (Zero Emojis, Minimalist Corporate)
    let biasesHtml = "";
    if (pm.detected_biases && pm.detected_biases.length > 0) {
      biasesHtml = `
        <div class="bias-section">
          <h4>Cognitive Biases & Behavioral Traps Detected in Your Rationale:</h4>
          ${pm.detected_biases.map(b => `
            <div class="bias-card">
              <div class="bias-title">${escapeHtml(stripEmojis(b.bias_name))} (${escapeHtml(b.severity)} Severity)</div>
              <p class="bias-trap"><strong>The Trap:</strong> ${escapeHtml(stripEmojis(b.psychological_trap))}</p>
              <p class="bias-reframing"><strong>Reframing Check:</strong> ${escapeHtml(stripEmojis(b.reframing_advice))}</p>
            </div>
          `).join("")}
        </div>
      `;
    }

    // Macro Shock Simulator HTML (Zero Emojis, Corporate Labels)
    const sym = data.thesis ? data.thesis.symbol : "EQUITY";
    const simulatorHtml = `
      <div class="simulator-card" id="sim-card-${data.session_id}">
        <div class="simulator-header">
          <span>Interactive Macro Shock Simulator (Stress Tester)</span>
        </div>
        <div class="sim-buttons">
          <button class="sim-btn" data-scenario="CRUDE_SURGE" data-sym="${escapeHtml(sym)}">Crude Spikes $95+</button>
          <button class="sim-btn" data-scenario="RBI_RATE_HIKE" data-sym="${escapeHtml(sym)}">RBI Hikes Repo +25bps</button>
          <button class="sim-btn" data-scenario="INR_DEPRECIATION" data-sym="${escapeHtml(sym)}">USD/INR Weakens ₹86.50</button>
          <button class="sim-btn" data-scenario="MARGIN_COMPRESSION" data-sym="${escapeHtml(sym)}">Margins Drop -250bps</button>
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
          ${escapeHtml(stripEmojis(pm.headline_verdict))}
        </h3>

        <div class="adversarial-body">${formattedDebate}</div>

        ${biasesHtml}

        ${simulatorHtml}

        <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid var(--border-subtle);">
          <strong style="font-size: 12px; color: var(--text-primary);">Key Institutional Pre-Mortem Takeaways:</strong>
          <ul style="margin: 6px 0 0 18px; font-size: 12px; color: var(--text-secondary); line-height: 1.5;">
            ${(pm.educational_takeaways || []).map((item) => `<li>${escapeHtml(stripEmojis(item))}</li>`).join("")}
          </ul>
        </div>

        <div class="action-buttons-row">
          <button class="rebuttal-btn" data-sym="${escapeHtml(sym)}">
            <span>Spar / Rebut</span>
          </button>
          <button class="export-btn" onclick="window.open('/api/export/${data.session_id}?format=pdf', '_blank')">
            <span>Download Pre-Mortem One-Pager (PDF)</span>
          </button>
          <button class="export-btn secondary-btn" style="background:transparent; border:1px solid var(--border-subtle); color:var(--text-secondary); margin-left:8px;" onclick="window.open('/api/export/${data.session_id}?format=html', '_blank')">
            <span>View Web Layout</span>
          </button>
        </div>
      </div>
    `;

    container.innerHTML = cardHtml;
    chatStream.appendChild(container);
    requestAnimationFrame(() => {
      chatStream.scrollTop = chatStream.scrollHeight;
    });

    // Attach click handlers to citation badges
    container.querySelectorAll(".citation-badge").forEach((badge) => {
      badge.addEventListener("click", () => {
        const factId = badge.dataset.factId;
        highlightFactRow(factId);
      });
    });

    // Attach click handler to Rebuttal Spar button
    const rebutBtn = container.querySelector(".rebuttal-btn");
    if (rebutBtn) {
      rebutBtn.addEventListener("click", () => {
        userInput.value = `Regarding ${sym}: I challenge your argument on `;
        userInput.focus();
        userInput.setSelectionRange(userInput.value.length, userInput.value.length);
      });
    }

    // Attach click handlers to simulator scenario buttons
    container.querySelectorAll(".sim-btn").forEach((btn) => {
      btn.addEventListener("click", async () => {
        container.querySelectorAll(".sim-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        const scenario = btn.dataset.scenario;
        const targetSym = btn.dataset.sym;
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
            body: JSON.stringify({ symbol: targetSym, scenario_type: scenario })
          });
          const sData = await sRes.json();
          impactTag.textContent = `${sData.scenario_title} → ${sData.estimated_impact}`;
          mechText.textContent = sData.mechanism;
          warnText.textContent = `Red-Team Warning: ${stripEmojis(sData.red_team_warning)}`;
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

    // Update count badge
    if (countAll) countAll.textContent = String(currentLKBFacts.length);

    // Update Friction Gauge
    const score = preMortem ? (preMortem.friction_score || 50) : 50;
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

    renderLKBTable();
  }

  function renderLKBTable() {
    lkbTbody.innerHTML = "";
    const filtered = activeCategory === "ALL"
      ? currentLKBFacts
      : currentLKBFacts.filter(f => (f.category || "").toUpperCase() === activeCategory);

    if (filtered.length === 0) {
      lkbTbody.innerHTML = `<tr><td colspan="5" class="empty-table-msg">No facts found in category '${activeCategory}'.</td></tr>`;
      return;
    }

    filtered.forEach((fact) => {
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
    // Switch to ALL tab if row is hidden under another category
    const fact = currentLKBFacts.find((f) => f.id === factId);
    if (fact && activeCategory !== "ALL" && (fact.category || "").toUpperCase() !== activeCategory) {
      activeCategory = "ALL";
      document.querySelectorAll(".filter-chip").forEach(b => {
        b.classList.toggle("active", b.dataset.category === "ALL");
      });
      renderLKBTable();
    }

    // Clear previous highlight
    document.querySelectorAll(".lkb-table tr").forEach((r) => r.classList.remove("highlighted"));

    const row = document.getElementById(`row-${factId}`);
    if (row) {
      row.classList.add("highlighted");
      row.scrollIntoView({ behavior: "smooth", block: "center" });
    }

    if (fact) {
      evidenceId.textContent = `CITATION: [${fact.id}] ${fact.metric}`;
      evidenceSource.textContent = `${fact.source} (${fact.category})`;
      evidenceContext.textContent = fact.context || `Value: ${fact.value} ${fact.unit}`;
    }
  }

  function stripEmojis(str) {
    if (!str) return "";
    return str.replace(/[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}\u{1F1E6}-\u{1F1FF}\u{1F600}-\u{1F64F}\u{1F680}-\u{1F6FF}\u{1F900}-\u{1F9FF}\u{1FA70}-\u{1FAFF}\u{200D}\u{FE0F}]/gu, "").trim();
  }

  function inlineFormat(str) {
    let res = escapeHtml(str);
    // Bold + Italic: ***text***
    res = res.replace(/\*\*\*(.*?)\*\*\*/g, '<strong><em>$1</em></strong>');
    // Bold: **text**
    res = res.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    // Italic: *text*
    res = res.replace(/\*(.*?)\*/g, '<em>$1</em>');
    // Inline Code: `text`
    res = res.replace(/`([^`]+)`/g, '<code>$1</code>');
    // Citations: [LKB-XX]
    res = res.replace(/\[(LKB-\d{2})\]/g, (match, id) => {
      return `<span class="citation-badge" data-fact-id="${id}">[${id}]</span>`;
    });
    return res;
  }

  function formatMarkdown(rawText) {
    if (!rawText) return "";
    const cleaned = stripEmojis(rawText);
    let html = "";

    if (typeof marked !== "undefined" && typeof marked.parse === "function") {
      try {
        marked.setOptions({
          gfm: true,
          breaks: true
        });
        html = marked.parse(cleaned);
      } catch (err) {
        console.warn("marked.parse error, using fallback:", err);
        html = fallbackMarkdown(cleaned);
      }
    } else {
      html = fallbackMarkdown(cleaned);
    }

    // Transform [LKB-XX] citation badges into interactive pill badges
    html = html.replace(/\[(LKB-\d{2})\]/g, (match, id) => {
      return `<span class="citation-badge" data-fact-id="${id}">[${id}]</span>`;
    });

    return html;
  }

  function fallbackMarkdown(cleaned) {
    const lines = cleaned.split(/\r?\n/);
    const out = [];
    let inList = false;
    let listType = "";

    function closeList() {
      if (inList) {
        out.push(listType === "ul" ? "</ul>" : "</ol>");
        inList = false;
        listType = "";
      }
    }

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      if (!line) {
        closeList();
        continue;
      }
      if (line.startsWith("### ")) {
        closeList();
        out.push(`<h4>${inlineFormat(line.slice(4))}</h4>`);
        continue;
      }
      if (line.startsWith("## ")) {
        closeList();
        out.push(`<h3>${inlineFormat(line.slice(3))}</h3>`);
        continue;
      }
      if (line.startsWith("# ")) {
        closeList();
        out.push(`<h3>${inlineFormat(line.slice(2))}</h3>`);
        continue;
      }
      const ulMatch = line.match(/^[-*]\s+(.*)$/);
      if (ulMatch) {
        if (!inList || listType !== "ul") {
          closeList();
          out.push("<ul>");
          inList = true;
          listType = "ul";
        }
        out.push(`<li>${inlineFormat(ulMatch[1])}</li>`);
        continue;
      }
      const olMatch = line.match(/^(\d+)\.\s+(.*)$/);
      if (olMatch) {
        if (!inList || listType !== "ol") {
          closeList();
          out.push("<ol>");
          inList = true;
          listType = "ol";
        }
        out.push(`<li>${inlineFormat(olMatch[2])}</li>`);
        continue;
      }
      closeList();
      out.push(`<p>${inlineFormat(line)}</p>`);
    }
    closeList();
    return out.join("\n");
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
