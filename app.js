// V-GUARD Due Diligence Suite - Dual-Mode Controller (Local Engine & Cloud Showcase)
let currentAuditData = null;
let ecosystemApps = [];
let staticFleetData = [];
let isLocalServer = false;

document.addEventListener("DOMContentLoaded", () => {
  initApp();
});

async function initApp() {
  setupTabs();
  setupEventListeners();
  await loadApps();
}

function setupTabs() {
  const tabs = document.querySelectorAll(".tab-btn");
  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      tabs.forEach(t => t.classList.remove("active"));
      document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));

      tab.classList.add("active");
      const targetId = tab.dataset.tab;
      const targetEl = document.getElementById(targetId);
      if (targetEl) targetEl.classList.add("active");
    });
  });
}

function setupEventListeners() {
  document.getElementById("btnAuditCustom").addEventListener("click", () => {
    const customPath = document.getElementById("customPathInput").value.trim();
    if (!customPath) {
      alert("Por favor ingresa una ruta local o URL de GitHub para inspeccionar.");
      return;
    }
    runAudit({ path: customPath });
  });

  document.getElementById("btnAuditAll").addEventListener("click", () => {
    runFleetAudit();
  });

  document.getElementById("btnCloseFleet").addEventListener("click", () => {
    document.getElementById("fleetModal").classList.add("hidden");
  });

  document.getElementById("btnSaveObsidian").addEventListener("click", async () => {
    if (!currentAuditData) return;
    if (!isLocalServer) {
      // En modo cloud, descargar como archivo .md directo
      downloadMarkdown(currentAuditData.markdown_report, `Dossier_Due_Diligence_${currentAuditData.app_name.replace(/\s+/g, '_')}.md`);
      return;
    }
    try {
      const res = await fetch("/api/save-obsidian", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          key: currentAuditData.app_key,
          name: currentAuditData.app_name,
          markdown: currentAuditData.markdown_report
        })
      });
      const data = await res.json();
      if (data.success) {
        alert("✅ ¡Dossier guardado exitosamente en Cerebros Obsidian!\n\nRuta:\n" + data.saved_path);
      } else {
        alert("❌ Error al guardar en Obsidian: " + (data.error || "Desconocido"));
      }
    } catch (e) {
      // Fallback a descarga
      downloadMarkdown(currentAuditData.markdown_report, `Dossier_Due_Diligence_${currentAuditData.app_name.replace(/\s+/g, '_')}.md`);
    }
  });

  document.getElementById("btnPrintReport").addEventListener("click", () => {
    window.print();
  });

  document.getElementById("btnCopySummary").addEventListener("click", () => {
    if (!currentAuditData) return;
    navigator.clipboard.writeText(currentAuditData.markdown_report).then(() => {
      alert("📋 ¡Informe Markdown de Due Diligence copiado al portapapeles!");
    });
  });
}

function downloadMarkdown(content, filename) {
  const blob = new Blob([content], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  alert(`💾 Dossier descargado como ${filename}`);
}

async function loadApps() {
  const grid = document.getElementById("appsGrid");
  const ipPill = document.getElementById("ipPill");

  // 1. Probar si el servidor backend local está respondiendo
  try {
    const res = await fetch("/api/apps");
    if (res.ok) {
      ecosystemApps = await res.json();
      isLocalServer = true;
      if (ipPill) ipPill.innerHTML = `<span>🟢 Motor Local 24/7 Activo</span>`;
      renderAppsGrid(ecosystemApps);
      return;
    }
  } catch (e) {
    // Backend local no disponible -> Entrar en Modo Cloud
  }

  // 2. Modo Cloud / GitHub Pages: Cargar dataset pre-auditado
  isLocalServer = false;
  if (ipPill) ipPill.innerHTML = `<span>☁️ Nube 24/7 (Showcase Activo)</span>`;

  try {
    const res = await fetch("fleet_data.json");
    if (res.ok) {
      staticFleetData = await res.json();
      ecosystemApps = staticFleetData.map(d => ({
        key: d.app_key,
        name: d.app_name,
        role: d.pillars.governance.summary || "Aplicación oficial del ecosistema",
        category: getCategoryForApp(d.app_key),
        icon: getIconForApp(d.app_key),
        exists: true,
        score: d.global_score,
        grade: d.grade,
        path: d.project_path
      }));
      renderAppsGrid(ecosystemApps);
    } else {
      throw new Error("No se pudo cargar fleet_data.json");
    }
  } catch (err) {
    grid.innerHTML = `<div class="error-state">Modo Cloud: ${err.message}</div>`;
  }
}

function getIconForApp(key) {
  const map = {
    cambioya: "🔄", ataraxia: "⚡", hidoctor: "🩺", faro: "🚨",
    vitrodiag: "🔬", sentinel: "🛡️", tramitefacil: "📑", vitrina: "🚀",
    crypto_analyzer: "📈"
  };
  return map[key] || "📦";
}

function getCategoryForApp(key) {
  const map = {
    cambioya: "Economía Colaborativa", ataraxia: "HealthTech & Stoic Coaching",
    hidoctor: "HealthTech Pediátrico", faro: "Seguridad Personal & SOS",
    vitrodiag: "Diagnóstico In-Vitro", sentinel: "Ciberseguridad & RGPD",
    tramitefacil: "GovTech & Ciudadanía", vitrina: "Showcase & Hub de Inversión",
    crypto_analyzer: "Fintech & Trading Cuantitativo"
  };
  return map[key] || "Software";
}

function renderAppsGrid(apps) {
  const grid = document.getElementById("appsGrid");
  grid.innerHTML = "";

  apps.forEach(app => {
    const card = document.createElement("div");
    card.className = `app-card ${app.exists ? "" : "disabled"}`;
    
    const scoreBadge = app.score ? `<span class="badge-app" style="float:right;">${app.grade} (${app.score}/100)</span>` : "";

    card.innerHTML = `
      <div>
        <div class="app-card-top">
          <span class="app-card-icon">${app.icon}</span>
          <div style="flex:1;">
            <div class="app-card-name">${app.name}</div>
            <div class="app-card-category">${app.category}</div>
          </div>
          ${scoreBadge}
        </div>
        <div class="app-card-role">${app.role}</div>
      </div>
      <div class="app-card-footer">
        <span class="${app.exists ? 'status-badge-ready' : 'status-badge-missing'}">
          ${isLocalServer ? '● Listo para auditar' : '● Certificado Cloud'}
        </span>
        <button class="btn btn-primary btn-sm" ${app.exists ? '' : 'disabled'}>
          ${isLocalServer ? 'Auditar' : 'Ver Dossier'}
        </button>
      </div>
    `;

    if (app.exists) {
      card.addEventListener("click", () => {
        runAudit({ key: app.key });
      });
    }

    grid.appendChild(card);
  });
}

async function runAudit(payload) {
  const scanningEl = document.getElementById("scanningState");
  const resultsEl = document.getElementById("resultsSection");
  const scanningTitle = document.getElementById("scanningAppTitle");

  resultsEl.classList.add("hidden");
  scanningEl.classList.remove("hidden");

  // Modo Cloud con dataset estático
  if (!isLocalServer) {
    setTimeout(() => {
      scanningEl.classList.add("hidden");
      if (payload.key && staticFleetData.length > 0) {
        const found = staticFleetData.find(d => d.app_key === payload.key);
        if (found) {
          currentAuditData = found;
          renderResults(found);
          return;
        }
      }
      alert("En el modo Cloud desplegado, las auditorías en vivo requieren el servidor local o un repositorio GitHub.");
    }, 400);
    return;
  }

  // Modo Local en vivo
  if (payload.key) {
    const matched = ecosystemApps.find(a => a.key === payload.key);
    if (matched) scanningTitle.innerText = `Auditando ${matched.name}...`;
  } else {
    scanningTitle.innerText = "Auditando directorio personalizado...";
  }

  try {
    const res = await fetch("/api/audit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.error || "Fallo en la auditoría");
    }

    const data = await res.json();
    currentAuditData = data;
    renderResults(data);
  } catch (err) {
    alert("❌ Error durante la auditoría: " + err.message);
  } finally {
    scanningEl.classList.add("hidden");
  }
}

function renderResults(data) {
  const resultsEl = document.getElementById("resultsSection");
  resultsEl.classList.remove("hidden");

  // Encabezado
  document.getElementById("resAppName").innerText = data.app_name;
  document.getElementById("resAppPath").innerText = data.project_path;
  document.getElementById("resAppCategory").innerText = getCategoryForApp(data.app_key);

  // Score Gauge
  const score = data.global_score;
  document.getElementById("scoreValue").innerText = score;
  
  const circle = document.getElementById("gaugeCircle");
  const circumference = 314; // 2 * PI * 50
  const offset = circumference - (circumference * (score / 100));
  circle.style.strokeDashoffset = offset;
  circle.style.stroke = data.grade_color;

  // Grade
  const gradeBadge = document.getElementById("gradeBadge");
  gradeBadge.innerText = data.grade;
  gradeBadge.style.color = data.grade_color;
  gradeBadge.style.background = `${data.grade_color}22`;
  document.getElementById("gradeDesc").innerText = data.grade_label;

  // Mini KPIs
  const dbEl = document.getElementById("kpiDealBreakers");
  dbEl.innerText = data.deal_breakers_count;
  dbEl.style.color = data.deal_breakers_count > 0 ? "var(--accent-red)" : "var(--accent-emerald)";

  const sloc = data.pillars.architecture.metrics.total_code_lines || 0;
  document.getElementById("kpiSLOC").innerText = sloc.toLocaleString();

  const ipVerified = data.pillars.ip_licenses.metrics.founder_ip_verified;
  const ipEl = document.getElementById("kpiIP");
  ipEl.innerText = ipVerified ? "✅ Verificada" : "⚠️ No explícita";
  ipEl.style.color = ipVerified ? "var(--accent-emerald)" : "var(--accent-amber)";

  const depsCount = data.pillars.ip_licenses.metrics.total_dependencies || 0;
  document.getElementById("kpiDeps").innerText = depsCount;

  // Renderizar Pilares
  renderPillar("sec", data.pillars.security);
  renderPillar("ip", data.pillars.ip_licenses);
  renderPillar("arch", data.pillars.architecture);
  renderPillar("res", data.pillars.resilience);
  renderPillar("gov", data.pillars.governance);

  // Scroll suave hacia los resultados
  resultsEl.scrollIntoView({ behavior: "smooth" });
}

function renderPillar(prefix, pillarData) {
  const badgeEl = document.getElementById(`${prefix}ScoreBadge`);
  badgeEl.innerText = `${pillarData.score}/100`;
  badgeEl.className = `pillar-score-badge ${pillarData.score >= 80 ? 'badge-good' : (pillarData.score >= 50 ? 'badge-warn' : 'badge-danger')}`;
  if (pillarData.score >= 80) {
    badgeEl.style.color = "var(--accent-emerald)";
    badgeEl.style.background = "rgba(16, 185, 129, 0.15)";
  } else if (pillarData.score >= 60) {
    badgeEl.style.color = "var(--accent-amber)";
    badgeEl.style.background = "rgba(245, 158, 11, 0.15)";
  } else {
    badgeEl.style.color = "var(--accent-red)";
    badgeEl.style.background = "rgba(239, 68, 68, 0.15)";
  }

  const listEl = document.getElementById(`${prefix}Findings`);
  listEl.innerHTML = "";

  const findings = pillarData.findings || [];
  if (findings.length === 0) {
    listEl.innerHTML = `<div class="finding-item finding-low"><div class="finding-title">✅ No se detectaron anomalías ni advertencias en este pilar.</div></div>`;
    return;
  }

  findings.forEach(f => {
    const item = document.createElement("div");
    const sevClass = f.severity ? f.severity.toLowerCase() : "low";
    item.className = `finding-item finding-${sevClass}`;
    
    let locationHtml = "";
    if (f.file) {
      const lineStr = f.line ? `:${f.line}` : "";
      locationHtml = `<div class="finding-location">📁 ${f.file}${lineStr}</div>`;
    }

    item.innerHTML = `
      <div class="finding-top">
        <span class="finding-title">${f.title}</span>
        <span class="finding-badge badge-${sevClass}">${f.severity || 'INFO'}</span>
      </div>
      <div class="finding-detail">${f.detail}</div>
      ${locationHtml}
    `;
    listEl.appendChild(item);
  });
}

async function runFleetAudit() {
  const scanningEl = document.getElementById("scanningState");
  const scanningTitle = document.getElementById("scanningAppTitle");
  
  if (!isLocalServer && staticFleetData.length > 0) {
    populateFleetTable(staticFleetData);
    document.getElementById("fleetModal").classList.remove("hidden");
    return;
  }

  scanningEl.classList.remove("hidden");
  scanningTitle.innerText = "Auditando toda la flota de aplicaciones...";

  try {
    const res = await fetch("/api/audit-all", { method: "POST" });
    const results = await res.json();
    populateFleetTable(results);
    document.getElementById("fleetModal").classList.remove("hidden");
  } catch (e) {
    alert("❌ Error al auditar la flota: " + e.message);
  } finally {
    scanningEl.classList.add("hidden");
  }
}

function populateFleetTable(results) {
  const tbody = document.getElementById("fleetTableBody");
  tbody.innerHTML = "";

  results.forEach(r => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><strong>${r.app_name}</strong></td>
      <td><strong>${r.global_score}/100</strong></td>
      <td><span class="grade-badge" style="color:${r.grade_color}; background:${r.grade_color}22;">${r.grade}</span></td>
      <td><span style="color:${r.deal_breakers_count > 0 ? 'var(--accent-red)' : 'var(--accent-emerald)'}; font-weight:700;">${r.deal_breakers_count}</span></td>
      <td>${r.pillars.security.score}/100</td>
      <td>${r.pillars.ip_licenses.score}/100</td>
      <td>${r.pillars.architecture.score}/100</td>
      <td>${r.pillars.resilience.score}/100</td>
      <td>${r.pillars.governance.score}/100</td>
      <td><button class="btn btn-outline btn-sm" onclick='viewFleetAppDetail(${JSON.stringify(r.app_key)})'>Ver</button></td>
    `;
    tbody.appendChild(tr);
  });
}

window.viewFleetAppDetail = function(appKey) {
  document.getElementById("fleetModal").classList.add("hidden");
  runAudit({ key: appKey });
};
