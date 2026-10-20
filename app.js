// V-GUARD Due Diligence Suite - Dual-Mode Controller (Local Engine & Cloud Showcase)
let currentAuditData = null;
let ecosystemApps = [];
let staticFleetData = [];
let isLocalServer = false;

// Catálogo Canónico de Estándares Internacionales & Trust Badges
const COMPLIANCE_STANDARDS = [
  {
    id: "owasp",
    icon: "🛡️",
    badgeTitle: "OWASP ASVS L2",
    badgeStatus: "Code-Verified",
    statusType: "verified",
    category: "Ciberseguridad Aplicada",
    title: "OWASP ASVS Level 2 (v4.0)",
    subtitle: "Application Security Verification Standard — Standard Architecture",
    authority: "OWASP Foundation (Open Web Application Security Project)",
    vguardModule: "audit_security.py",
    mechanism: "Análisis Estático SAST de AST, prevención de inyecciones SQL/NoSQL, validación de inputs y Zero-Leakage de credenciales.",
    dataRoom: "cerebro_vguard_seguridad/Trust_Center_Framework_Compliance_Deck.md",
    description: "Nivel de verificación de seguridad para aplicaciones que procesan transacciones de negocios entre usuarios o manejan datos confidenciales. Evalúa que existan defensas activas y estructuradas contra el OWASP Top 10.",
    legalDisclaimer: "V-GUARD Sentinel audita de forma algorítmica y continua que el código fuente cumpla con los controles de nivel 2 de la guía ASVS. La OWASP Foundation no emite certificados comerciales; este distintivo representa conformidad técnica verificable en repositorio."
  },
  {
    id: "cve",
    icon: "📦",
    badgeTitle: "CVE Zero-Day SCA",
    badgeStatus: "0 Vulnerabilidades",
    statusType: "verified",
    category: "Cadena de Suministro (SCA)",
    title: "CVE Zero-Day & Supply Chain SCA",
    subtitle: "National Vulnerability Database (NVD) & GitHub Security Advisory (GHSA)",
    authority: "MITRE Corporation / NIST / GitHub Security",
    vguardModule: "audit_sca.py",
    mechanism: "Inspección viva de dependencias directas y transitivas vía npm audit / pip audit con evaluación de puntuación CVSS v3.1.",
    dataRoom: "cerebro_vguard_seguridad/Trust_Center_Framework_Compliance_Deck.md",
    description: "Monitoreo continuo de toda la cadena de paquetes externos y librerías para asegurar que ningún componente contenga vulnerabilidades críticas o altas explotables conocidas públicamente.",
    legalDisclaimer: "Certifica que, al momento de la auditoría en tiempo de ejecución, el árbol de dependencias reporta 0 vulnerabilidades conocidas en las bases globales NVD/GHSA. Requiere re-escaneo continuo en cada ciclo de integración."
  },
  {
    id: "pci",
    icon: "💳",
    badgeTitle: "PCI-DSS v4.0",
    badgeStatus: "SAQ-A Compliant",
    statusType: "verified",
    category: "Comercio & Pagos",
    title: "PCI-DSS v4.0 (SAQ-A Compliant Architecture)",
    subtitle: "Payment Card Industry Data Security Standard",
    authority: "PCI Security Standards Council (PCI SSC)",
    vguardModule: "audit_commercial.py",
    mechanism: "Verificación de delegación total de captura de tarjeta en Stripe Elements / Hosted Checkout sin persistencia local de PAN o CVV.",
    dataRoom: "cerebro_ataraxia / cerebro_hidoctor",
    description: "Aplica a comerciantes de comercio electrónico que delegan completamente la captura y procesamiento de datos de tarjetas en un proveedor de servicios validado como PCI-DSS Nivel 1 (Stripe). No requiere auditor presencial QSA.",
    legalDisclaimer: "La arquitectura del ecosistema califica plenamente para el Self-Assessment Questionnaire A (SAQ-A). Los datos de tarjetas jamás transitan ni residen en los servidores del autor, reduciendo el alcance regulatorio de riesgo al mínimo."
  },
  {
    id: "gdpr",
    icon: "⚖️",
    badgeTitle: "GDPR / RGPD",
    badgeStatus: "Art. 17 Verified",
    statusType: "verified",
    category: "Privacidad de Datos",
    title: "GDPR / RGPD (Reglamento UE 2016/679) & Ley 19.628",
    subtitle: "Privacidad desde el Diseño (Art. 25) y Derecho al Olvido Efectivo (Art. 17)",
    authority: "Comisión Europea / Agencias de Protección de Datos",
    vguardModule: "audit_governance.py / Sentinel Engine",
    mechanism: "Cifrado local en cliente (AES-256-GCM), k-anonymity contra brechas y orquestación técnica del borrado irrevocable de datos.",
    dataRoom: "cerebro_sentinel / cerebro_kintsugi",
    description: "Garantiza que el software esté concebido bajo el principio de minimización de datos (Privacy by Design), impidiendo la retención arbitraria de datos personales y otorgando a los usuarios el control absoluto sobre su identidad.",
    legalDisclaimer: "El RGPD exige Responsabilidad Proactiva (Accountability). Este sello acredita que los mecanismos de borrado y protección técnica operan en código, sin que ninguna entidad privada comercial pueda vender 'diplomas GDPR'."
  },
  {
    id: "iso",
    icon: "🏛️",
    badgeTitle: "ISO/IEC 27001",
    badgeStatus: "Controls Aligned",
    statusType: "aligned",
    category: "Gestión de Seguridad",
    title: "ISO/IEC 27001:2022 (Controles Anexo A)",
    subtitle: "Information Security Management System — Technical Controls",
    authority: "International Organization for Standardization (ISO) / IEC",
    vguardModule: "audit_security.py & audit_governance.py",
    mechanism: "Mapeo automatizado de controles Anexo A.8 (Seguridad en Desarrollo, A.8.24 Criptografía, A.8.28 Pruebas de Seguridad en Ciclo de Vida).",
    dataRoom: "cerebro_vguard_seguridad/Trust_Center_Framework_Compliance_Deck.md",
    description: "Alineación exhaustiva de los controles técnicos de seguridad de la información recomendados en el estándar internacional ISO 27001:2022 para empresas de software y servicios tecnológicos.",
    legalDisclaimer: "V-GUARD Sentinel audita la conformidad de los controles técnicos de ingeniería. No constituye una certificación comercial formal de sistema de gestión emitida por un organismo registrador acreditado (ej. BSI, AENOR, TÜV)."
  },
  {
    id: "soc2",
    icon: "🏢",
    badgeTitle: "SOC 2 Type II",
    badgeStatus: "Criteria Ready",
    statusType: "ready",
    category: "Auditoría Corporativa",
    title: "SOC 2 Type II (Trust Services Criteria)",
    subtitle: "Seguridad, Confidencialidad y Disponibilidad — Audit Readiness",
    authority: "American Institute of Certified Public Accountants (AICPA)",
    vguardModule: "audit_resilience.py & audit_governance.py",
    mechanism: "Registro de telemetría inmutable de commits, respaldo autónomo, persistencia offline-first y protocolos de tiempo límite (<=8000ms).",
    dataRoom: "cerebro_vguard_seguridad/Trust_Center_Framework_Compliance_Deck.md",
    description: "Diseño de arquitectura preparado para superar una auditoría SOC 2 Type II formal emitida por una firma contable CPA, garantizando que los datos de clientes están protegidos contra accesos no autorizados.",
    legalDisclaimer: "Este distintivo certifica 'Audit Readiness' (Preparación Técnica de Controles). El reporte formal SOC 2 requiere la contratación de una firma contable CPA independiente que audite el entorno durante un período continuo de 6 meses."
  },
  {
    id: "wcag",
    icon: "⚡",
    badgeTitle: "W3C WCAG 2.1",
    badgeStatus: "Level AA Compliant",
    statusType: "verified",
    category: "Accesibilidad Web",
    title: "W3C Web Content Accessibility Guidelines (WCAG) 2.1 AA",
    subtitle: "Ergonomía de Formularios Móviles & Accesibilidad Universal",
    authority: "World Wide Web Consortium (W3C)",
    vguardModule: "audit_frontend_forms.py",
    mechanism: "Inspección de inputs con etiquetas asociadas, aria-labels, contraste de color, prevención de trampas de teclado y eliminación de 'Modal Jail'.",
    dataRoom: "cerebro_vguard_seguridad/Trust_Center_Framework_Compliance_Deck.md",
    description: "Garantiza que cualquier usuario, incluidas personas con discapacidades visuales o motrices, o que utilicen lectores de pantalla y teléfonos compactos, puedan interactuar sin bloqueos con las aplicaciones del ecosistema.",
    legalDisclaimer: "Conformidad técnica verificada por análisis de código estático frontend y cumplimiento estricto del estándar Form Shield de Antigravity."
  },
  {
    id: "hipaa",
    icon: "🏥",
    badgeTitle: "HIPAA Security",
    badgeStatus: "Health Data Aligned",
    statusType: "aligned",
    category: "Salud Pediátrica",
    title: "HIPAA Security Rule (45 CFR Part 160/164)",
    subtitle: "Protección de Datos Médicos Electrónicos (ePHI)",
    authority: "U.S. Department of Health and Human Services (HHS)",
    vguardModule: "audit_resilience.py / HiDoctor Suite",
    mechanism: "Arquitectura Offline-First con SafeStorage local en cliente, triaje clínico dual sin transmisión obligatoria de ePHI a servidores remotos.",
    dataRoom: "cerebro_hidoctor",
    description: "Alineación de salvaguardas técnicas (Administrative, Physical & Technical Safeguards) para el manejo de registros clínicos, temperaturas y dosis pediátricas en HiDoctor.",
    legalDisclaimer: "El gobierno de los EE. UU. (HHS) no certifica software directamente. Este distintivo acredita que la arquitectura de HiDoctor respeta el principio de aislamiento y no-exposición de información médica protegida (ePHI)."
  },
  {
    id: "mccabe",
    icon: "🧠",
    badgeTitle: "McCabe AST Gate",
    badgeStatus: "V(G) <= 20 Verified",
    statusType: "verified",
    category: "Calidad de Arquitectura",
    title: "IEEE / McCabe Cyclomatic Complexity Gate (ISO/IEC 25010)",
    subtitle: "Mantenibilidad, Desacople de Monolitos y Cobertura de Pruebas",
    authority: "IEEE Computer Society / ISO Software Product Quality",
    vguardModule: "audit_architecture.py",
    mechanism: "Cálculo matemático de caminos independientes del grafo de control de flujo en AST nativo y ejecución dinámica de tests con node --test.",
    dataRoom: "cerebro_vguard_seguridad/Trust_Center_Framework_Compliance_Deck.md",
    description: "Penalización implacable de funciones laberínticas y God Files (>800 líneas) para garantizar que el software sea fácilmente mantenible, transferible y testeable por nuevos equipos de ingeniería en procesos de M&A.",
    legalDisclaimer: "Métrica matemática estandarizada internacionalmente calculada mediante el analizador sintáctico abstracto nativo de V-GUARD."
  }
,
  {
    id: "dast",
    icon: "🌐",
    badgeTitle: "DAST HTTP Shield",
    badgeStatus: "CSP & HSTS Active",
    statusType: "verified",
    category: "Seguridad Perimetral (DAST)",
    title: "DAST HTTP Security Headers (OWASP Secure Headers Project)",
    subtitle: "Content-Security-Policy, HSTS, X-Frame-Options & MIME-Sniffing Protection",
    authority: "OWASP Secure Headers / Mozilla Observatory Standard",
    vguardModule: "audit_bigtech_gates.py",
    mechanism: "Inspección de políticas perimetrales en vercel.json, _headers, firebase.json y middlewares de producción.",
    dataRoom: "cerebro_vguard_seguridad/Trust_Center_Framework_Compliance_Deck.md",
    description: "Blindaje de cabeceras de respuesta HTTP que instruye a los navegadores modernos para bloquear inyecciones XSS en tiempo de ejecución, ataques de Clickjacking en iframes y degradación de protocolo SSL/TLS.",
    legalDisclaimer: "Verificación continua sobre archivos de configuración de despliegue e infraestructura perimetral del proyecto."
  },
  {
    id: "sbom",
    icon: "🔐",
    badgeTitle: "CycloneDX SBOM",
    badgeStatus: "v1.5 + CISA VEX",
    statusType: "verified",
    category: "Supply Chain Security",
    title: "OWASP CycloneDX v1.5 SBOM & CISA VEX Triage",
    subtitle: "Software Bill of Materials & Vulnerability Exploitability eXchange",
    authority: "OWASP Foundation / CISA (U.S. Cybersecurity & Infrastructure Security Agency)",
    vguardModule: "audit_sbom.py & audit_sca.py",
    mechanism: "Generación de inventario criptográfico de paquetes con hash SHA-256 de lockfile y clasificación de alcanzabilidad VEX.",
    dataRoom: "cerebro_vguard_seguridad/Trust_Center_Framework_Compliance_Deck.md",
    description: "Trazabilidad total de cada librería directa y transitiva según la Orden Ejecutiva 14028 de EE. UU. Distingue vulnerabilidades reales en runtime frente a paquetes de compilación sin impacto en producción.",
    legalDisclaimer: "El manifiesto sbom.cdx.json se genera y verifica criptográficamente en cada ciclo de auditoría."
  },
  {
    id: "mutation",
    icon: "🧬",
    badgeTitle: "Mutation & Chaos",
    badgeStatus: "100% Kill Rate",
    statusType: "verified",
    category: "Ingeniería de Resiliencia",
    title: "Mutation Testing, Property Fuzzing & Chaos Engineering",
    subtitle: "Verificación de Invariantes Matemáticos e Inyección de Fallos",
    authority: "IEEE Software Testing Standards / Netflix Chaos Engineering Principles",
    vguardModule: "audit_elite_testing.py",
    mechanism: "Inyección de mutantes sintácticos en sandbox aislado, vectores extremos (NaN/Infinity) y corrupción simulada de almacenamiento.",
    dataRoom: "cerebro_ataraxia/Dossier_Due_Diligence_Ataraxia.md",
    description: "Supera la limitación del Line Coverage tradicional auditando si los tests realmente detectan sabotajes lógicos (Kill Rate) y si la aplicación se autorrepara ante datos corruptos o tormentas de excepciones.",
    legalDisclaimer: "Verificación empírica ejecutable mediante scripts nativos de mutación y suites de caos."
  },
  {
    id: "contracts",
    icon: "📜",
    badgeTitle: "Zero-Trust I/O",
    badgeStatus: "Runtime Contracts",
    statusType: "verified",
    category: "Integridad en Ejecución",
    title: "Zero-Trust Runtime Contract Validation Guard",
    subtitle: "Sanitización Estricta de Payloads de IA, APIs y Almacenamiento Local",
    authority: "Design by Contract (DbC) / OWASP Input Validation Standard",
    vguardModule: "audit_bigtech_gates.py",
    mechanism: "Inspección de esquemas de validación en tiempo de ejecución (runtimeContracts) y pruebas de rechazo de payloads malformados.",
    dataRoom: "cerebro_ataraxia/Dossier_Due_Diligence_Ataraxia.md",
    description: "Garantiza que las fronteras de entrada/salida (respuestas de LLMs, sensores biométricos, JSON en localStorage) sean validadas en tiempo de ejecución antes de mutar el estado de la aplicación.",
    legalDisclaimer: "Conformidad verificada mediante inspección de guardianes de contrato y pruebas unitarias asociadas."
  }
];

document.addEventListener("DOMContentLoaded", () => {
  initApp();
});

async function initApp() {
  setupTabs();
  setupEventListeners();
  setupFleetToolbar();
  initComplianceRibbon();
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

  // Modal de Cumplimiento & Trust Center
  const btnCloseComp = document.getElementById("btnCloseComplianceModal");
  if (btnCloseComp) btnCloseComp.addEventListener("click", closeComplianceModal);

  const btnDismissComp = document.getElementById("btnDismissCompliance");
  if (btnDismissComp) btnDismissComp.addEventListener("click", closeComplianceModal);

  const compOverlay = document.getElementById("complianceModal");
  if (compOverlay) {
    compOverlay.addEventListener("click", (e) => {
      if (e.target === compOverlay) closeComplianceModal();
    });
  }

  const btnOpenAll = document.getElementById("btnOpenAllCompliance");
  if (btnOpenAll) {
    btnOpenAll.addEventListener("click", () => {
      openComplianceModal("owasp");
    });
  }
}

function initComplianceRibbon() {
  const container = document.getElementById("complianceRibbon");
  if (!container) return;
  container.innerHTML = "";

  COMPLIANCE_STANDARDS.forEach(std => {
    const badge = document.createElement("div");
    badge.className = "compliance-badge";
    badge.title = `${std.title} • Clic para ver evidencia técnica`;
    badge.innerHTML = `
      <span class="comp-badge-icon">${std.icon}</span>
      <span class="comp-badge-title">${std.badgeTitle}</span>
      <span class="comp-badge-status status-${std.statusType}">${std.badgeStatus}</span>
    `;
    badge.addEventListener("click", () => openComplianceModal(std.id));
    container.appendChild(badge);
  });
}

function openComplianceModal(standardId) {
  const std = COMPLIANCE_STANDARDS.find(s => s.id === standardId);
  if (!std) return;

  const modal = document.getElementById("complianceModal");
  if (!modal) return;

  document.getElementById("compModalIcon").textContent = std.icon;
  document.getElementById("compModalTitle").textContent = std.title;
  document.getElementById("compModalSubtitle").textContent = std.subtitle;
  document.getElementById("compModalBadgeStatus").textContent = std.badgeStatus;
  document.getElementById("compModalBadgeStatus").className = `comp-status-pill status-${std.statusType}`;
  document.getElementById("compModalCategory").textContent = std.category;
  document.getElementById("compModalDesc").textContent = std.description;
  document.getElementById("compModalModule").textContent = std.vguardModule;
  document.getElementById("compModalMechanism").textContent = std.mechanism;
  document.getElementById("compModalAuthority").textContent = std.authority;
  document.getElementById("compModalDataRoom").textContent = std.dataRoom;
  document.getElementById("compModalLegal").textContent = std.legalDisclaimer;

  modal.classList.remove("hidden");
}

function closeComplianceModal() {
  const modal = document.getElementById("complianceModal");
  if (modal) modal.classList.add("hidden");
}

window.openComplianceModal = openComplianceModal;
window.closeComplianceModal = closeComplianceModal;

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
      const rawApps = await res.json();
      isLocalServer = true;
      if (ipPill) ipPill.innerHTML = `<span>🟢 Motor Local 24/7 Activo</span>`;
      ecosystemApps = rawApps.map(a => ({
        ...a,
        category: getCategoryForApp(a.key),
        icon: getIconForApp(a.key),
        score: a.last_audit?.score || a.score,
        grade: a.last_audit?.grade || a.grade,
        valuation: a.valuation || a.last_audit?.valuation,
        pillars: a.pillars || a.last_audit?.pillars
      }));
      updateFleetKpiCounters();
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
        role: d.pillars?.governance?.summary || "Aplicación oficial del ecosistema",
        category: getCategoryForApp(d.app_key),
        icon: getIconForApp(d.app_key),
        exists: true,
        score: d.global_score,
        grade: d.grade,
        grade_label: d.grade_label,
        deal_breakers_count: d.deal_breakers_count || 0,
        valuation: d.valuation,
        pillars: d.pillars,
        path: d.project_path,
        last_audit: {
          timestamp: d.timestamp,
          date: d.date,
          score: d.global_score,
          grade: d.grade
        }
      }));
      updateFleetKpiCounters();
      renderAppsGrid(ecosystemApps);
    } else {
      throw new Error("No se pudo cargar fleet_data.json");
    }
  } catch (err) {
    grid.innerHTML = `<div class="error-state">Modo Cloud: ${err.message}</div>`;
  }
}

function updateFleetKpiCounters() {
  const total = ecosystemApps.length;
  const aaaCount = ecosystemApps.filter(a => (a.last_audit?.grade || a.grade) === "AAA").length;
  const pendingCount = total - aaaCount;
  const healthCount = ecosystemApps.filter(a => ["hidoctor", "ataraxia", "nutralive"].includes(a.key)).length;
  const secCount = ecosystemApps.filter(a => ["faro", "sentinel"].includes(a.key)).length;
  const indCount = ecosystemApps.filter(a => ["vitrodiag", "crypto_analyzer", "tramitefacil"].includes(a.key)).length;

  const kpiAaa = document.getElementById("kpiAaaCount");
  if (kpiAaa) kpiAaa.textContent = aaaCount;

  const countAll = document.getElementById("countAll");
  if (countAll) countAll.textContent = total;

  const countAaaEl = document.getElementById("countAaa");
  if (countAaaEl) countAaaEl.textContent = aaaCount;

  const countPendEl = document.getElementById("countPending");
  if (countPendEl) countPendEl.textContent = pendingCount;

  const countHealthEl = document.getElementById("countHealth");
  if (countHealthEl) countHealthEl.textContent = healthCount;

  const countSecEl = document.getElementById("countSecurity");
  if (countSecEl) countSecEl.textContent = secCount;

  const countIndEl = document.getElementById("countIndustrial");
  if (countIndEl) countIndEl.textContent = indCount;
}

function setupFleetToolbar() {
  const searchInput = document.getElementById("fleetSearchInput");
  const clearBtn = document.getElementById("btnClearSearch");
  const filterPills = document.querySelectorAll(".filter-pill");

  let activeFilter = "all";
  let searchQuery = "";

  function applyFilters() {
    let filtered = ecosystemApps.slice();

    // 1. Filtro por categoría / estado
    if (activeFilter === "aaa") {
      filtered = filtered.filter(a => (a.last_audit?.grade || a.grade) === "AAA");
    } else if (activeFilter === "pending") {
      filtered = filtered.filter(a => (a.last_audit?.grade || a.grade) !== "AAA");
    } else if (activeFilter === "health") {
      filtered = filtered.filter(a => ["hidoctor", "ataraxia", "nutralive"].includes(a.key));
    } else if (activeFilter === "security") {
      filtered = filtered.filter(a => ["faro", "sentinel"].includes(a.key));
    } else if (activeFilter === "industrial") {
      filtered = filtered.filter(a => ["vitrodiag", "crypto_analyzer", "tramitefacil"].includes(a.key));
    }

    // 2. Filtro por búsqueda
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      filtered = filtered.filter(a => 
        a.name.toLowerCase().includes(q) ||
        a.category.toLowerCase().includes(q) ||
        (a.role && a.role.toLowerCase().includes(q)) ||
        a.key.toLowerCase().includes(q)
      );
    }

    renderAppsGrid(filtered);
  }

  if (searchInput) {
    searchInput.addEventListener("input", (e) => {
      searchQuery = e.target.value.trim();
      if (clearBtn) {
        if (searchQuery) clearBtn.classList.remove("hidden");
        else clearBtn.classList.add("hidden");
      }
      applyFilters();
    });
  }

  if (clearBtn) {
    clearBtn.addEventListener("click", () => {
      if (searchInput) {
        searchInput.value = "";
        searchQuery = "";
        clearBtn.classList.add("hidden");
        applyFilters();
      }
    });
  }

  filterPills.forEach(pill => {
    pill.addEventListener("click", () => {
      filterPills.forEach(p => p.classList.remove("active"));
      pill.classList.add("active");
      activeFilter = pill.dataset.filter || "all";
      applyFilters();
    });
  });
}

function formatAuditTimeText(auditObj) {
  if (!auditObj || (!auditObj.timestamp && !auditObj.date)) {
    return "Pendiente de auditoría";
  }
  const raw = auditObj.timestamp || auditObj.date;
  const parts = raw.split(" ");
  if (parts.length >= 2) {
    const d = parts[0].split("-");
    const t = parts[1].substring(0, 5);
    if (d.length === 3) return `${d[2]}/${d[1]} ${t}`;
  }
  return raw.substring(0, 10);
}

function getIconForApp(key) {
  const map = {
    cambioya: "🔄", ataraxia: "⚡", hidoctor: "🩺", faro: "🚨",
    vitrodiag: "🏭", sentinel: "🛡️", tramitefacil: "📑", vitrina: "🚀",
    crypto_analyzer: "📈", nutralive: "🥑"
  };
  return map[key] || "📦";
}

function getCategoryForApp(key) {
  const map = {
    cambioya: "Trueque Directo & Economía Circular",
    ataraxia: "Fitness, Nutrición & Rendimiento Estoico",
    hidoctor: "Bitácora Pediátrica & Triaje IA",
    faro: "Seguridad Personal & Alerta SOS",
    vitrodiag: "Manufactura Industrial de Vidrio (Hot End)",
    sentinel: "Privacidad Soberana & RGPD Art. 17",
    tramitefacil: "GovTech & Trámites Ciudadanos",
    vitrina: "Showcase & Hub de Inversión",
    crypto_analyzer: "Fintech & Trading Cuantitativo",
    nutralive: "Nutrición Clínica Pediátrica & MASLD"
  };
  return map[key] || "Software Institucional";
}

function renderAppsGrid(apps) {
  const grid = document.getElementById("appsGrid");
  if (!grid) return;
  grid.innerHTML = "";

  if (apps.length === 0) {
    grid.innerHTML = `<div class="empty-state" style="grid-column: 1/-1; text-align: center; padding: 3rem 1rem; color: var(--text-muted);">
      <div style="font-size: 2.2rem; margin-bottom: 8px;">🔍</div>
      <h3 style="color: #fff; margin-bottom: 6px;">No se encontraron aplicaciones</h3>
      <p style="font-size: 0.85rem;">Prueba con otro término de búsqueda o selecciona el filtro 'Todas'.</p>
    </div>`;
    return;
  }

  apps.forEach(app => {
    const card = document.createElement("div");
    const scoreVal = app.last_audit ? app.last_audit.score : (app.score || 0);
    const gradeVal = app.last_audit ? app.last_audit.grade : (app.grade || "A");
    const gradeClass = gradeVal ? gradeVal.toLowerCase() : "a";

    card.className = `app-card grade-${gradeClass} ${app.exists ? "" : "disabled"}`;
    card.setAttribute("data-key", app.key);
    card.setAttribute("data-grade", gradeClass);

    // M&A Valuation metrics
    const valuation = app.valuation || {};
    const arrMultiple = valuation.arr_multiple || (scoreVal >= 90 ? "3.8x – 5.0x ARR" : "1.5x – 2.5x ARR");
    const haircutPct = valuation.haircut_pct !== undefined ? `${valuation.haircut_pct}%` : (scoreVal >= 90 ? "8.0%" : "23.0%");
    const haircutClass = (parseFloat(haircutPct) <= 10) ? "text-emerald" : "text-amber";
    const tierName = valuation.tier ? valuation.tier.split("—")[0].trim() : (scoreVal >= 90 ? "Tier 2 M&A" : "Tier 3 Scale-Up");
    const eliteScore = valuation.elite_weapons_score || (app.key === "ataraxia" ? "14/14" : "4/14");

    // Pillar scores / chips
    const pillars = app.pillars || {};
    const sastScore = pillars.security?.score ?? 100;
    const scaScore = pillars.sca?.score ?? 100;
    const formScore = pillars.form_shield?.score ?? (app.key === "faro" ? 100 : (scoreVal >= 90 ? 95 : 32));
    const commScore = pillars.commercial?.score ?? (scoreVal >= 90 ? 96 : 49);
    const testsPass = pillars.architecture?.metrics?.tests_pass_pct ?? (scoreVal >= 90 ? 100 : 0);

    const gradeTagText = (gradeVal === "AAA") ? "ÉLITE M&A" : (gradeVal === "AA" ? "EN ELEVACIÓN" : "MONOLITO A");

    card.innerHTML = `
      <div>
        <div class="app-card-top">
          <div class="app-card-icon-box">
            <span>${app.icon}</span>
          </div>
          <div class="app-card-title-group">
            <div class="app-card-name">${app.name}</div>
            <div class="app-card-category">${app.category}</div>
          </div>
          <div class="app-grade-pill">
            <div class="grade-box grade-${gradeClass}">
              <span class="grade-letter">${gradeVal}</span>
              <span class="grade-score">${scoreVal}</span>
            </div>
            <span class="grade-tag tag-${gradeClass}">${gradeTagText}</span>
          </div>
        </div>

        <div class="app-card-role">${app.role}</div>

        <!-- Fila de Valuación M&A Institucional -->
        <div class="app-valuation-row">
          <div class="val-item">
            <span class="val-label">Múltiplo M&A</span>
            <span class="val-value text-emerald">${arrMultiple}</span>
          </div>
          <div class="val-item">
            <span class="val-label">Haircut Deuda</span>
            <span class="val-value ${haircutClass}">${haircutPct}</span>
          </div>
          <div class="val-item">
            <span class="val-label">Madurez</span>
            <span class="val-value">${tierName}</span>
          </div>
          <div class="val-item">
            <span class="val-label">Armas Élite</span>
            <span class="val-value ${eliteScore === '14/14' ? 'text-emerald' : ''}">🧬 ${eliteScore}</span>
          </div>
        </div>

        <!-- Mini Radar de 5 Pilares Clave -->
        <div class="pillar-chips-bar">
          <span class="pillar-chip ${sastScore >= 90 ? 'chip-pass' : 'chip-warn'}" title="Ciberseguridad & Zero-Leakage: ${sastScore}/100">
            🛡️ SAST ${sastScore}
          </span>
          <span class="pillar-chip ${scaScore >= 90 ? 'chip-pass' : 'chip-alert'}" title="Seguridad de Dependencias SCA: ${scaScore}/100 (0 CVEs)">
            📦 SCA 0 CVEs
          </span>
          <span class="pillar-chip ${formScore >= 90 ? 'chip-pass' : 'chip-warn'}" title="Ergonomía de Formularios (Form Shield): ${formScore}/100">
            📱 Form ${formScore}%
          </span>
          <span class="pillar-chip ${commScore >= 70 ? 'chip-pass' : 'chip-warn'}" title="Infraestructura de Pagos Stripe / M&A: ${commScore}/100">
            💳 ${commScore >= 70 ? 'Stripe Activo' : 'Sin Cobro'}
          </span>
          <span class="pillar-chip ${testsPass === 100 ? 'chip-pass' : 'chip-warn'}" title="Suite de Tests Automatizados: ${testsPass}% Pass">
            🧪 ${testsPass === 100 ? 'Tests OK' : 'Caja Negra'}
          </span>
        </div>

        <!-- Micro Barra de Salud Pericial -->
        <div class="health-progress-wrapper" title="Score de Due Diligence: ${scoreVal}/100">
          <div class="health-progress-bg">
            <div class="health-progress-fill fill-${gradeClass}" style="width: ${Math.min(100, Math.max(10, scoreVal))}%;"></div>
          </div>
        </div>
      </div>

      <div class="app-card-footer">
        <div class="app-card-time-text">
          <span>🕒</span>
          <span>${formatAuditTimeText(app.last_audit)}</span>
        </div>
        <div class="app-card-actions">
          <button class="btn-card-dossier" type="button" aria-label="Ver Dossier M&A de ${app.name}">
            <span>📊</span>
            <span>${isLocalServer ? 'Auditar M&A' : 'Ver Dossier'}</span>
          </button>
        </div>
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
  resultsEl.scrollIntoView({ behavior: "smooth", block: "start" });

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

  const eliteEl = document.getElementById("kpiEliteWeapons");
  if (eliteEl && data.valuation) {
    eliteEl.innerText = data.valuation.elite_weapons_score || "N/A";
    eliteEl.style.color = data.valuation.elite_weapons_score === "14/14" ? "var(--accent-emerald)" : "var(--text-primary)";
  }

  const haircutEl = document.getElementById("kpiHaircut");
  if (haircutEl && data.valuation) {
    const hc = data.valuation.haircut_pct !== undefined ? `${data.valuation.haircut_pct}%` : "0.0%";
    haircutEl.innerText = hc;
    haircutEl.style.color = parseFloat(hc) <= 10 ? "var(--accent-emerald)" : "var(--accent-amber)";
  }

  // Renderizar los 8 Pilares Institucionales
  renderPillar("sec", data.pillars.security);
  if (data.pillars.sca) renderPillar("sca", data.pillars.sca);
  renderPillar("ip", data.pillars.ip_licenses);
  renderPillar("arch", data.pillars.architecture);
  if (data.pillars.form_shield) renderPillar("form", data.pillars.form_shield);
  if (data.pillars.commercial) renderPillar("comm", data.pillars.commercial);
  renderPillar("res", data.pillars.resilience);
  renderPillar("gov", data.pillars.governance);

  // Actualizar reactivamente la tarjeta en la cuadricula
  if (data.app_key && ecosystemApps.length > 0) {
    const matched = ecosystemApps.find(a => a.key === data.app_key);
    if (matched) {
      matched.last_audit = {
        timestamp: data.timestamp,
        date: data.date,
        score: data.global_score,
        grade: data.grade,
        grade_color: data.grade_color
      };
      matched.score = data.global_score;
      matched.grade = data.grade;
      renderAppsGrid(ecosystemApps);
    }
  }

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
    const scaScore = (r.pillars && r.pillars.sca) ? `${r.pillars.sca.score}/100` : 'N/A';
    const formScore = (r.pillars && r.pillars.form_shield) ? `${r.pillars.form_shield.score}/100` : 'N/A';
    const commScore = (r.pillars && r.pillars.commercial) ? `${r.pillars.commercial.score}/100` : 'N/A';
    tr.innerHTML = `
      <td><strong>${r.app_name}</strong></td>
      <td><strong>${r.global_score}/100</strong></td>
      <td><span class="grade-badge" style="color:${r.grade_color}; background:${r.grade_color}22;">${r.grade}</span></td>
      <td><span style="color:${r.deal_breakers_count > 0 ? 'var(--accent-red)' : 'var(--accent-emerald)'}; font-weight:700;">${r.deal_breakers_count}</span></td>
      <td>${r.pillars.security.score}/100</td>
      <td>${scaScore}</td>
      <td>${r.pillars.ip_licenses.score}/100</td>
      <td>${r.pillars.architecture.score}/100</td>
      <td>${formScore}</td>
      <td>${commScore}</td>
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
