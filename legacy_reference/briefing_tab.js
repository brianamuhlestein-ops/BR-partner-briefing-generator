let currentMode = "Master";
let schemaData = {};

async function loadSchemas() {
  console.log("[DEBUG] Attempting to fetch schema...");
  const res = await fetch("/briefing_tab/briefing_schemas.json");
  console.log("[DEBUG] Schema fetch status:", res.status);
  schemaData = await res.json();
  console.log("[DEBUG] Schema data loaded:", schemaData);
  buildSectionBoxes(currentMode);
}

function selectMode(mode) {
  window.currentMode = mode;

  // === Toggle active button ===
  document.querySelectorAll(".mode-btn").forEach(b => b.classList.remove("active"));
  const target = document.querySelector(".mode-btn." + String(mode).toLowerCase());
  if (target) target.classList.add("active");

  // === Update title dynamically ===
  document.getElementById("briefingTypeTitle").innerText =
    (mode === "Partner")
      ? "Space Weather Impacts and IDSS"
      : `${mode} Briefing`;

  // === Only rebuild input boxes for non-Partner modes ===
  if (mode !== "Partner") {
    buildSectionBoxes(mode);
    setTimeout(loadDraft, 100);
  }

  const idssWrapper = document.getElementById("partnerIDSSWrapper");
  const socialWrapper = document.getElementById("socialBuilderWrapper");
  const controls = document.getElementById("controlButtons");
  const rightPanel = document.querySelector(".right-panel");

  // === Partner tab ===
  if (mode === "Partner") {
    idssWrapper.style.display = "block";
    socialWrapper.style.display = "none";
    controls.style.display = "none";
    if (rightPanel) rightPanel.style.display = "none";
    console.log("[DEBUG] Partner mode selected, loading IDSS content...");
    loadPartnerIDSS();
  }

  // === Social Graphic Builder tab ===
  else if (mode === "Social") {
    idssWrapper.style.display = "none";
    socialWrapper.style.display = "block";
    controls.style.display = "none";
    if (rightPanel) rightPanel.style.display = "none";
    // document.getElementById("briefingTypeTitle").innerText = "Social Graphic Builder";
    document.getElementById("slideDate").value = new Date().toUTCString().replace("GMT", "UTC");
  }

  // === All other briefings ===
  else {
    idssWrapper.style.display = "none";
    socialWrapper.style.display = "none";
    controls.style.display = "block";
    if (rightPanel) rightPanel.style.display = "block";
  }


    // === Hide or show text boxes for Partner ===
    const sectionContainer = document.getElementById("sectionContainer");
    if (sectionContainer) {
      sectionContainer.style.display = (mode === "Partner") ? "none" : "block";
    }

    // === Load SWPC products dynamically ===
    try {
      const icaoBox = document.getElementById("icaoProducts");
      const alertBox = document.getElementById("activeProducts");

      // Always load active alerts (all tabs)
      if (alertBox) {
        alertBox.style.display = "block";
        loadActiveAlerts();
      }

      // Only load ICAO advisories when ICAO tab is active
      if (icaoBox) {
        if (mode === "ICAO") {
          icaoBox.style.display = "block";
          loadICAOAdvisories();
        } else {
          icaoBox.style.display = "none";
        }
      }
    } catch (err) {
      console.error("[ERROR] Failed to load SWPC products:", err);
    }
  }



window.onload = loadSchemas;


function buildSectionBoxes(mode) {
  const container = document.getElementById("sectionContainer");
  container.innerHTML = "";

  const sections = schemaData[mode] || [];

  // === Load any saved data for this mode (from drafts or pushDownstream) ===
  let savedData = {};
  const saved = localStorage.getItem(`briefing_${mode}`);
  if (saved) {
    try {
      savedData = JSON.parse(saved);
      console.log(`[DEBUG] Loaded saved data for ${mode}:`, savedData);
    } catch (err) {
      console.warn(`[WARN] Could not parse saved ${mode} data:`, err);
    }
  }

  sections.forEach((title, idx) => {
    const sectionDiv = document.createElement("div");
    sectionDiv.className = "section-block";

    const label = document.createElement("label");
    label.textContent = title;
    sectionDiv.appendChild(label);

    // === Probability Table logic ===
    if (title.toLowerCase().includes("probability table")) {
      const table = document.createElement("table");
      table.className = "prob-table";

      // pick correct categories by section name
      let categories = [];
      if (title.toLowerCase().includes("solar activity")) {
        categories = ["R1–R2", "R3+"];
      } else if (title.toLowerCase().includes("energetic")) {
        categories = ["S1–S2", "S3+"];
      } else if (
        title.toLowerCase().includes("solar wind") ||
        title.toLowerCase().includes("geospace")
      ) {
        categories = ["G1–G2", "G3+"];
      } else {
        categories = ["R1–R2", "R3+"];
      }

      const days = ["Day 1", "Day 2", "Day 3"];

      // header
      const thead = document.createElement("thead");
      const hrow = document.createElement("tr");
      hrow.appendChild(document.createElement("th")); // blank corner
      days.forEach((d) => {
        const th = document.createElement("th");
        th.textContent = d;
        hrow.appendChild(th);
      });
      thead.appendChild(hrow);
      table.appendChild(thead);

      // body
      const tbody = document.createElement("tbody");
      categories.forEach((cat) => {
        const row = document.createElement("tr");
        const th = document.createElement("th");
        th.textContent = cat;
        row.appendChild(th);

        days.forEach((_, dIdx) => {
          const cell = document.createElement("td");
          const input = document.createElement("input");
          input.type = "text";
          input.className = "prob-input";
          input.id = `table_${idx}_${cat}_${dIdx}`;
          cell.appendChild(input);

          // === Restore saved table values if present ===
          const savedKey = `${title}_${cat}_day${dIdx + 1}`;
          if (savedData[savedKey]) {
            input.value = savedData[savedKey];
          }

          row.appendChild(cell);
        });

        tbody.appendChild(row);
      });

      table.appendChild(tbody);
      sectionDiv.appendChild(table);
    } else {
      // === Normal text section ===
      const textarea = document.createElement("textarea");
      textarea.id = `section_${idx}`;
      textarea.rows = 4;

      // === Restore saved text if present ===
      if (savedData[title]) {
        textarea.value = savedData[title];
      }

      sectionDiv.appendChild(textarea);
    }

    container.appendChild(sectionDiv);
  });
}




async function loadActiveAlerts() {
  try {
    const resp = await fetch(`${baseUrl}/get_active_alerts`);
    const data = await resp.json();
    if (!Array.isArray(data)) return;
    const container = document.getElementById("activeProducts");
    container.innerHTML = "";

    data.slice(1).forEach(row => {   // skip header row
      const [issueTime, messageCode, msgType, region, phenomenon, category, threshold, issueText] = row;
      const div = document.createElement("div");
      div.className = "alert-entry";
      div.innerHTML = `
        <strong>${messageCode}</strong> – ${phenomenon} ${category} (${threshold})<br>
        <small>${issueTime}</small>
      `;
      container.appendChild(div);
    });
  } catch (err) {
    console.error("Alert fetch failed", err);
  }
}

async function loadICAOAdvisories() {
  try {
    const resp = await fetch(`${baseUrl}/get_icao_advisories`);
    const data = await resp.json();
    const container = document.getElementById("icaoProducts");
    container.innerHTML = "";

    data.forEach(ad => {
      const div = document.createElement("div");
      div.className = "icao-entry";
      div.innerHTML = `
        <strong>${ad.advisory_number}</strong> – ${ad.event_begin} (${ad.event_end})<br>
        ${ad.advisory_text.slice(0, 300)}...
      `;
      container.appendChild(div);
    });
  } catch (err) {
    console.error("ICAO advisory fetch failed", err);
  }
}














async function generateBriefing() {
  const sections = schemaData[currentMode] || [];
  const inputs = {};

  // === Collect all inputs and probability tables ===
  sections.forEach((title, idx) => {
    if (title.toLowerCase().includes("probability table")) {
      const categories = ["R1–R2", "R3+", "S1–S2", "S3+", "G1–G2", "G3+"];
      const days = ["Day 1", "Day 2", "Day 3"];
      const tableData = {};

      categories.forEach(cat => {
        tableData[cat] = {};
        days.forEach((_, dIdx) => {
          const el = document.getElementById(`table_${idx}_${cat}_${dIdx}`);
          tableData[cat][`Day${dIdx + 1}`] = el ? el.value : "";
        });
      });
      inputs[title] = tableData;
    } else {
      const el = document.getElementById(`section_${idx}`);
      inputs[title] = el ? el.value : "";
    }
  });

  const payload = { type: currentMode, inputs: inputs };

  // === Route mapping for each briefing type ===
  const routeMap = {
    "Master": "/generate_master_text",
    "Discussion": "/generate_discussion_pdf",
    "ICAO": "/generate_icao_pdf",
    "Staff": "/generate_staff_pdf"
  };
  const url = routeMap[currentMode] || "/generate_briefing";

  console.log(`[DEBUG] Sending ${currentMode} briefing to ${url}`);

  try {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await res.json();

    // === Show the PDF preview if one was created ===
    if (data.pdf_path) {
      document.getElementById("previewFrame").src = data.pdf_path;
      alert(`${currentMode} PDF created successfully!`);
    } else {
      document.getElementById("previewFrame").srcdoc = data.html || "";
      alert(`${currentMode} text generated (no PDF found).`);
    }

  } catch (err) {
    console.error(`[ERROR] generateBriefing() failed for ${currentMode}:`, err);
    alert(`Failed to generate ${currentMode} briefing.`);
  }
}

async function loadPartnerIDSS() {
  try {
    console.log("[DEBUG] Loading IDSS sectors...");
    const res = await fetch("/get_idss_sectors");
    const data = await res.json();
    const sectors = data.sectors || data.Sectors || [];

    // === Build sector buttons ===
    const btnRow = document.getElementById("sectorButtons");
    btnRow.innerHTML = "";
    sectors.forEach((s, i) => {
      const btn = document.createElement("button");
      btn.textContent = s.name;
      btn.className = "sector-btn";
      btn.onclick = () => renderSectorTable(s);
      if (i === 0) btn.classList.add("active");
      btnRow.appendChild(btn);
    });

    // === Render first sector by default ===
    if (sectors.length > 0) renderSectorTable(sectors[0]);

    // === Also draw matrix (unchanged) ===
    drawRiskMatrix();
  } catch (err) {
    console.error("Failed to load IDSS data:", err);
  }
}

// === Partner Risk table ===
function renderSectorTable(sector) {
  const tableContainer = document.getElementById("idssTableContainer");
  tableContainer.innerHTML = "";

  // Reset button highlighting
  document.querySelectorAll(".sector-btn").forEach((b) => b.classList.remove("active"));
  const activeBtn = [...document.querySelectorAll(".sector-btn")].find((b) => b.textContent === sector.name);
  if (activeBtn) activeBtn.classList.add("active");

  const table = document.createElement("table");
  table.className = "idss-table";

  // Table head
  const thead = document.createElement("thead");
  thead.innerHTML = `
    <tr><th colspan="4">${sector.name}</th></tr>
    <tr><th>Level</th><th>Thresholds</th><th>Description</th><th>Key Indicators</th></tr>
  `;
  table.appendChild(thead);

  const tbody = document.createElement("tbody");
  const levels = Object.keys(sector.impact_levels || {});
  levels.forEach((lvl, i) => {
    const row = document.createElement("tr");
    const thresholds = (sector.thresholds && sector.thresholds[lvl]) || "—";
    row.innerHTML = `
      <td><b>${lvl}</b></td>
      <td>${thresholds}</td>
      <td>${sector.impact_levels[lvl]}</td>
      ${i === 0
        ? `<td rowspan="${levels.length}">${(sector.key_indicators || []).join("<br>")}</td>`
        : ""}`
    ;
    tbody.appendChild(row);
  });

  table.appendChild(tbody);
  tableContainer.appendChild(table);
}

function drawRiskMatrix() {
  const matrixContainer = document.getElementById("idssMatrixContainer");
  matrixContainer.innerHTML = "";

  const likelihoods = [
    "Extremely Unlikely",
    "Unlikely",
    "As Likely as Not",
    "Likely",
    "Very Likely"
  ];
  const impacts = [
    "1 (No Impact)",
    "2 (Minor)",
    "3 (Moderate)",
    "4 (Major)",
    "5 (Extreme)"
  ];

  // --- Build risk matrix values: ceil((impact * likelihood)/5)
  const z = impacts.map((_, i) =>
    likelihoods.map((__, j) => Math.ceil(((i + 1) * (j + 1)) / 5))
  );

  const trace = {
    x: likelihoods,
    y: impacts,
    z: z,
    type: "heatmap",
    colorscale: [
      [0.00, "#00A878"],   // Little to None
      [0.25, "#FFE864"],   // Minor
      [0.50, "#FF8C42"],   // Moderate
      [0.75, "#E84F4F"],   // High
      [1.00, "#C12AFF"]    // Extreme
    ],
    zmin: 1,
    zmax: 5,
    showscale: false
  };

  const layout = {
    title: "Space Weather IDSS Risk Matrix",
    xaxis: {
      title: "Likelihood of Occurrence",
      tickangle: -30,
      side: "bottom"
    },
    yaxis: {
      title: "Impact Level",
      autorange: false,           // ✅ stop reversing
      range: [0, 4]               // ensures 1→bottom, 5→top
    },
    width: 700,
    height: 600,
    margin: { t: 80, l: 100, r: 120, b: 100 }
  };

  // === Color legend ===
  const legendHTML = `
    <div style="position:relative; left:730px; top:0;">
      <table style="border-collapse:collapse; text-align:center;">
        <tr><th style="border:1px solid #000; padding:4px;">Risk Level</th></tr>
        <tr><td style="background:#00A878; color:black; padding:4px;">Little to None</td></tr>
        <tr><td style="background:#FFE864; color:black; padding:4px;">Minor</td></tr>
        <tr><td style="background:#FF8C42; color:white; padding:4px;">Moderate</td></tr>
        <tr><td style="background:#E84F4F; color:white; padding:4px;">High</td></tr>
        <tr><td style="background:#C12AFF; color:white; padding:4px;">Extreme</td></tr>
      </table>
    </div>`;
  matrixContainer.insertAdjacentHTML("beforeend", legendHTML);

  Plotly.purge(matrixContainer);
  Plotly.newPlot(matrixContainer, [trace], layout);
}

function calculateRisk() {
  const likelihood = parseInt(document.getElementById("likelihoodSelect").value, 10);
  const impact = parseInt(document.getElementById("impactSelect").value, 10);
  const resultDiv = document.getElementById("riskResult");

  const colors = ["#00A878","#FFE864","#FF8C42","#E84F4F","#C12AFF"];
  const labels = ["Little to None","Minor","Moderate","High","Extreme"];

  // Same rule as heatmap
  const riskLevel = Math.ceil((likelihood * impact) / 5); // 1..5
  const levelText = labels[riskLevel - 1];
  const color = colors[riskLevel - 1];

  const lText = document.getElementById("likelihoodSelect").options[likelihood - 1].text;
  const iText = document.getElementById("impactSelect").options[impact - 1].text;

  resultDiv.innerHTML =
    `Probability: <b>${lText}</b>, Impact: <b>${iText}</b> → ` +
    `<span style="background:${color}; color:white; padding:3px 8px; border-radius:4px;">${levelText} Risk</span>`;

  highlightRiskCell(likelihood, impact);
}

// ============================================================
// === Utility Buttons ========================================
// ============================================================

function clearText() {
  const sections = schemaData[currentMode] || [];
  sections.forEach((_, idx) => {
    const el = document.getElementById(`section_${idx}`);
    if (el) el.value = "";
  });
  localStorage.removeItem(`briefing_${currentMode}`);
  alert("Cleared all text fields for " + currentMode);
}

function saveDraft() {
  if (!currentMode) return;

  // Skip Partner tab entirely
  if (currentMode === "Partner") {
    console.log("[DEBUG] Partner tab has no draft content — skipping saveDraft().");
    return;
  }

  const sectionContainer = document.getElementById("sectionContainer");
  if (!sectionContainer) return;

  const sections = schemaData[currentMode] || [];
  const dataToSave = {};

  sections.forEach((title, idx) => {
    // === Probability Table logic ===
    if (title.toLowerCase().includes("probability table")) {
      const table = sectionContainer.querySelectorAll("table")[idx];
      if (table) {
        const rows = table.querySelectorAll("tr");
        rows.forEach((row, rIdx) => {
          const th = row.querySelector("th");
          if (!th || rIdx === 0) return; // skip header
          const cat = th.textContent.trim();
          const cells = row.querySelectorAll("td input");
          cells.forEach((input, dIdx) => {
            const key = `${title}_${cat}_day${dIdx + 1}`;
            dataToSave[key] = input.value || "";
          });
        });
      }
    } else {
      // === Normal text section ===
      const textarea = document.getElementById(`section_${idx}`);
      if (textarea) dataToSave[title] = textarea.value || "";
    }
  });

  // === Save to localStorage (not new JSON file) ===
  localStorage.setItem(`briefing_${currentMode}`, JSON.stringify(dataToSave));
  console.log(`[DEBUG] Saved ${currentMode} draft to localStorage`, dataToSave);

  // === Inline confirmation message ===
  let status = document.getElementById("statusMessage");
  if (!status) {
    status = document.createElement("div");
    status.id = "statusMessage";
    status.style.color = "#006400";
    status.style.fontWeight = "bold";
    status.style.marginTop = "8px";
    document.body.appendChild(status);
  }

  const timestamp = new Date().toLocaleTimeString();
  status.textContent = `✓ ${currentMode} draft saved at ${timestamp}`;
  setTimeout(() => (status.textContent = ""), 4000);
}

async function loadPrevious() {
  if (!currentMode) {
    alert("Please select a briefing type first.");
    return;
  }

  console.log(`[DEBUG] Attempting to load previous ${currentMode} briefing...`);

  // === 1. Try localStorage first ===
  const saved = localStorage.getItem(`briefing_${currentMode}`);
  if (saved) {
    try {
      const data = JSON.parse(saved);
      const sections = schemaData[currentMode] || [];

      sections.forEach((title, idx) => {
        // Text boxes
        const el = document.getElementById(`section_${idx}`);
        if (el && data[title]) el.value = data[title];

        // Probability tables
        if (title.toLowerCase().includes("probability table")) {
          const table = document.querySelectorAll(`table`)[idx];
          if (table) {
            const rows = table.querySelectorAll("tr");
            rows.forEach((row, rIdx) => {
              const th = row.querySelector("th");
              if (!th || rIdx === 0) return; // skip header
              const cat = th.textContent.trim();
              const cells = row.querySelectorAll("td input");
              cells.forEach((input, dIdx) => {
                const key = `${title}_${cat}_day${dIdx + 1}`;
                if (data[key]) input.value = data[key];
              });
            });
          }
        }
      });

      alert(`Loaded previous ${currentMode} briefing from local draft.`);
      console.log(`[DEBUG] Loaded from localStorage:`, data);
      return; // ✅ success — no need to fetch server
    } catch (err) {
      console.warn(`[WARN] Failed to load local draft for ${currentMode}:`, err);
    }
  }

  // === 2. Fallback: Fetch from Flask archive route ===
  try {
    const res = await fetch("/load_previous_briefing?type=" + currentMode);
    const data = await res.json();

    const sections = schemaData[currentMode] || [];
    sections.forEach((title, idx) => {
      const el = document.getElementById(`section_${idx}`);
      if (el && data[title]) el.value = data[title];
    });

    alert(`Loaded previous ${currentMode} briefing from archive.`);
    console.log(`[DEBUG] Loaded from Flask archive:`, data);
  } catch (err) {
    console.error(`[ERROR] Could not load previous ${currentMode}:`, err);
    alert("No previous draft found locally or on server.");
  }
}

function pushDownstream() {
  console.log("[DEBUG] Pushing Master content downstream...");

  if (currentMode !== "Master") {
    alert("You can only push downstream from the Master briefing.");
    return;
  }

  // Pull all Master values from the text boxes
  const sectionContainer = document.getElementById("sectionContainer");
  const inputs = sectionContainer.querySelectorAll("textarea");

  if (!inputs.length) {
    alert("No Master fields found to push.");
    return;
  }

  // Load stored schemas (used to build boxes)
  const masterSchema = schemaData["Master"];
  const targets = ["Discussion", "ICAO", "Staff"];

  // Build a simple key-value map of section → content
  const contentMap = {};
  inputs.forEach((ta, i) => {
    contentMap[masterSchema[i]] = ta.value || "";
  });

  // For each downstream target tab, store new data in localStorage
  targets.forEach((tab) => {
    const tabSchema = schemaData[tab];
    if (!tabSchema) return;

    const downstreamMap = {};
    tabSchema.forEach((section) => {
      // If section exists in Master, copy its value
      if (contentMap[section]) downstreamMap[section] = contentMap[section];
    });

    // Save downstreamMap to localStorage under tab key
    localStorage.setItem(`briefing_${tab}`, JSON.stringify(downstreamMap));
    console.log(`[DEBUG] Pushed content to ${tab}:`, downstreamMap);
  });

  // alert("Master content successfully pushed to Discussion, ICAO, and Staff.");
  const confirm = document.getElementById("pushConfirm");
  if (confirm) {
    confirm.textContent = "✓ Master content pushed successfully!";
    confirm.style.display = "block";
    setTimeout(() => (confirm.style.display = "none"), 4000);
  }

}

// === Temporary placeholder for loadDraft() ===
// Prevents ReferenceError when switching modes
function loadDraft() {
  console.log("[DEBUG] loadDraft() placeholder called – no draft system yet");
}


// === Auto-save every 30 seconds ===
setInterval(() => {
  if (currentMode && document.visibilityState === "visible") {
    console.log(`[DEBUG] Auto-saving draft for ${currentMode}...`);
    saveDraft();
  }
}, 30000);
