"use client";
import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { api, API_URL } from "../lib/api";
import type {
  Audit,
  Creative,
  Dashboard,
  Product,
  Proposal,
  Recommendation,
  Rules,
  Session,
} from "../lib/types";

const tabs = [
  "Resumen",
  "Anuncios",
  "Productos",
  "Planificador",
  "Optimización",
  "Actividad",
  "Configuración",
] as const;
type Tab = (typeof tabs)[number];
const eventLabels: Record<string, string> = {
  "product.created": "Producto agregado",
  "product.updated": "Producto actualizado",
  "creative.uploaded": "Anuncio cargado",
  "proposal.created": "Propuesta generada",
  "proposal.approved": "Propuesta aprobada",
  "proposal.rejected": "Propuesta rechazada",
  "rules.updated": "Reglas actualizadas",
  "optimization.evaluated": "Campañas evaluadas",
  "recommendation.approved": "Cambio aprobado",
  "recommendation.rejected": "Cambio rechazado",
  "recommendation.simulated": "Simulación aplicada",
  "recommendation.invalidated_by_rules":
    "Revisión invalidada por nuevas reglas",
};
const icons = ["◈", "▧", "◫", "✦", "◎", "≋", "⚙"];
const labels: Record<string, string> = {
  pending: "Por revisar",
  approved: "Aprobada",
  rejected: "Rechazada",
  applied: "Simulada",
  active: "Activa · demo",
  paused: "Pausada · demo",
};

export default function Home() {
  const [session, setSession] = useState<Session | null>(null);
  const [ready, setReady] = useState(false);
  const [tab, setTab] = useState<Tab>("Resumen");
  const [tenant, setTenant] = useState("cristal-demo");
  const [role, setRole] = useState("owner");
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [products, setProducts] = useState<Product[]>([]);
  const [creatives, setCreatives] = useState<Creative[]>([]);
  const [proposals, setProposals] = useState<Proposal[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [rules, setRules] = useState<Rules | null>(null);
  const [audit, setAudit] = useState<Audit[]>([]);
  const [selectedProduct, setSelectedProduct] = useState("");
  const [selectedAds, setSelectedAds] = useState<string[]>([]);
  const [budget, setBudget] = useState("1000");
  const [cpa, setCpa] = useState("250");
  const [country, setCountry] = useState("UY");
  const [ageMin, setAgeMin] = useState("18");
  const [ageMax, setAgeMax] = useState("65");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);
  const owner = session?.member.role === "owner";
  const money = (minor: number) =>
    new Intl.NumberFormat("es-UY", {
      style: "currency",
      currency: session?.tenant.currency || "UYU",
      maximumFractionDigits: 2,
    }).format(minor / 100);

  async function load(s: Session) {
    const t = s.access_token;
    const [d, p, c, pr, r, ru, a] = await Promise.all([
      api<Dashboard>("/api/dashboard", t),
      api<Product[]>("/api/products", t),
      api<Creative[]>("/api/creatives", t),
      api<Proposal[]>("/api/proposals", t),
      api<Recommendation[]>("/api/recommendations", t),
      api<Rules>("/api/rules", t),
      api<Audit[]>("/api/audit", t),
    ]);
    setDashboard(d);
    setProducts(p);
    setCreatives(c);
    setProposals(pr);
    setRecommendations(r);
    setRules(ru);
    setAudit(a);
    setSelectedProduct((current) =>
      p.some((item) => item.id === current) ? current : p[0]?.id || "",
    );
  }

  useEffect(() => {
    setReady(true);
    const raw = sessionStorage.getItem("meta-demo-session");
    if (raw) {
      let s: Session;
      try {
        s = JSON.parse(raw);
      } catch {
        sessionStorage.removeItem("meta-demo-session");
        return;
      }
      setBusy(true);
      api("/api/me", s.access_token)
        .then(() => load(s))
        .then(() => setSession(s))
        .catch(() => {
          sessionStorage.removeItem("meta-demo-session");
          setError(
            "La sesión terminó o la API no está disponible. Volvé a entrar.",
          );
        })
        .finally(() => setBusy(false));
    }
  }, []);

  async function work(action: () => Promise<void>) {
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await action();
      return true;
    } catch (e) {
      setError(
        e instanceof Error ? e.message : "No se pudo completar la operación",
      );
      return false;
    } finally {
      setBusy(false);
    }
  }

  async function login(event: FormEvent) {
    event.preventDefault();
    await work(async () => {
      const s = await api<Session>("/api/auth/demo", undefined, "POST", {
        tenant,
        role,
      });
      await load(s);
      setSession(s);
      sessionStorage.setItem("meta-demo-session", JSON.stringify(s));
    });
  }

  async function mutate(
    path: string,
    body?: unknown,
    method = "POST",
    message = "Cambios guardados en el demo.",
  ) {
    if (!session) return;
    return await work(async () => {
      await api(path, session.access_token, method, body);
      await load(session);
      setNotice(message);
    });
  }

  async function saveProduct(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const data = new FormData(form);
    const saved = await mutate(
      editingProduct ? `/api/products/${editingProduct.id}` : "/api/products",
      {
        name: data.get("name"),
        description: data.get("description"),
        price_minor: Math.round(Number(data.get("price")) * 100),
        margin_pct: Number(data.get("margin")),
      },
      editingProduct ? "PUT" : "POST",
    );
    if (saved) {
      setEditingProduct(null);
      form.reset();
    }
  }

  async function upload(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const data = new FormData(form);
    const file = data.get("file") as File;
    if (file.size > 25 * 1024 * 1024) {
      setError("El archivo supera los 25 MiB.");
      return;
    }
    await mutate(
      "/api/creatives/upload",
      data,
      "POST",
      "Anuncio cargado. Ya podés revisar su análisis técnico.",
    );
  }

  async function download(id: string) {
    await work(async () => {
      const response = await fetch(`${API_URL}/api/creatives/${id}/file`, {
        headers: { Authorization: `Bearer ${session!.access_token}` },
      });
      if (!response.ok) throw new Error("No se pudo descargar el archivo.");
      const url = URL.createObjectURL(await response.blob());
      const link = document.createElement("a");
      link.href = url;
      link.download = creatives.find((c) => c.id === id)?.name || "anuncio";
      link.click();
      URL.revokeObjectURL(url);
    });
  }

  if (!session)
    return (
      <main className="welcome">
        <div className="welcome-copy">
          <div className="wordmark">
            <span className="logo">m</span> meta ads <b>ai</b>
          </div>
          <p className="eyebrow">DE LA IDEA A UNA DECISIÓN MEJOR</p>
          <h1>
            Tu próxima campaña.
            <br />
            <em>Con un plan.</em>
          </h1>
          <p>
            Reuní tus productos y anuncios. Explorá estrategias, entendé los
            números y revisá cada cambio en un solo lugar.
          </p>
          <div className="welcome-tags">
            <span>01 · Prepará</span>
            <span>02 · Planificá</span>
            <span>03 · Revisá</span>
          </div>
        </div>
        <form onSubmit={login} className="login-card">
          <span className="pill">ENTORNO DE DEMOSTRACIÓN</span>
          <h2>Explorá tu espacio</h2>
          <p>
            Datos ficticios. Sin credenciales de Meta y sin gasto publicitario.
          </p>
          <label>
            Empresa
            <select
              aria-label="Empresa"
              disabled={!ready || busy}
              value={tenant}
              onChange={(e) => setTenant(e.target.value)}
            >
              <option value="cristal-demo">Cristal · Demo</option>
              <option value="norte-demo">Norte · Demo</option>
            </select>
          </label>
          <label>
            Acceso de prueba
            <select
              aria-label="Acceso de prueba"
              disabled={!ready || busy}
              value={role}
              onChange={(e) => setRole(e.target.value)}
            >
              <option value="owner">
                Administrador · puede revisar cambios
              </option>
              <option value="viewer">Lector · solo consulta</option>
            </select>
          </label>
          <button disabled={busy || !ready} className="primary">
            {busy ? "Preparando espacio…" : "Entrar al demo →"}
          </button>
          {error && (
            <p role="alert" className="error">
              {error}
            </p>
          )}
          <small>
            Estas empresas son espacios de prueba compartidos. No cargues
            información confidencial.
          </small>
        </form>
      </main>
    );

  return (
    <div className="shell" aria-busy={busy}>
      <aside className="sidebar">
        <div className="wordmark">
          <span className="logo">m</span> meta ads <b>ai</b>
        </div>
        <div className="workspace">
          <span className="avatar">{session.tenant.name[0]}</span>
          <div>
            <strong>{session.tenant.name}</strong>
            <small>Espacio de trabajo</small>
          </div>
          <span>⌄</span>
        </div>
        <p className="nav-label">TU PUBLICIDAD, EN ORDEN</p>
        <nav aria-label="Navegación principal">
          {tabs.map((item, i) => (
            <button
              aria-label={item}
              key={item}
              onClick={() => {
                setTab(item);
                setError("");
                setNotice("");
              }}
              className={tab === item ? "nav-active" : ""}
            >
              <span>{icons[i]}</span>
              {item}
              {item === "Optimización" &&
                recommendations.filter((r) => r.status === "pending").length >
                  0 && (
                  <b className="nav-count">
                    {
                      recommendations.filter((r) => r.status === "pending")
                        .length
                    }
                  </b>
                )}
            </button>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="connection">
            <span className="dot amber" /> Meta desconectado
          </div>
          <small>
            Demo independiente de Meta.
            <br />
            Ningún cambio genera gasto.
          </small>
          <button
            className="logout"
            disabled={busy}
            onClick={() =>
              work(async () => {
                sessionStorage.removeItem("meta-demo-session");
                setSession(null);
                setSelectedProduct("");
                setSelectedAds([]);
                setTab("Resumen");
                await api("/api/auth/logout", session.access_token, "POST");
              })
            }
          >
            Salir del espacio ↗
          </button>
        </div>
      </aside>
      <div className="main-area">
        <header className="topbar">
          <span>
            Espacio de trabajo <span className="slash">/</span>{" "}
            <strong>{tab}</strong>
          </span>
          <div>
            <span className="pill">DEMO</span>
            <span className="role">
              {owner ? "Administrador" : "Solo lectura"}
            </span>
            <button
              className="mobile-exit"
              aria-label="Salir"
              disabled={busy}
              onClick={() =>
                work(async () => {
                  sessionStorage.removeItem("meta-demo-session");
                  setSession(null);
                  setSelectedProduct("");
                  setSelectedAds([]);
                  setTab("Resumen");
                  await api("/api/auth/logout", session.access_token, "POST");
                })
              }
            >
              Salir
            </button>
            <span className="avatar small">{owner ? "AD" : "LE"}</span>
          </div>
        </header>
        <main className="content">
          <div className="page-heading">
            <div>
              <p className="eyebrow">CONTROL + CLARIDAD</p>
              <h1>{tab === "Resumen" ? "Una mirada a tu publicidad" : tab}</h1>
              <p>
                {
                  (
                    {
                      Resumen:
                        "Tus resultados de ejemplo, las oportunidades y el próximo paso.",
                      Anuncios:
                        "Tu biblioteca creativa, lista para pensar la próxima campaña.",
                      Productos:
                        "El contexto de tu negocio empieza por lo que vendés.",
                      Planificador:
                        "Una estrategia explicada, con cada anuncio en su lugar.",
                      Optimización:
                        "Evaluá las señales. Vos decidís qué cambios simular.",
                      Actividad: "Un registro de las decisiones de tu equipo.",
                      Configuración:
                        "Límites claros antes de proponer cualquier cambio.",
                    } as Record<Tab, string>
                  )[tab]
                }
              </p>
            </div>
            {tab === "Resumen" && (
              <button
                className="primary"
                onClick={() => setTab("Planificador")}
              >
                ✦ Crear propuesta
              </button>
            )}
          </div>
          <div className="demo-banner">
            <span>◉</span>
            <div>
              <strong>Estás explorando una demostración.</strong> Las métricas
              son ficticias y las recomendaciones usan reglas explicables. Meta
              está desconectado.
            </div>
          </div>
          {error && (
            <div role="alert" className="error">
              {error}
            </div>
          )}
          {notice && (
            <div role="status" className="notice">
              {notice}
            </div>
          )}
          {busy && (
            <div role="status" className="loading">
              Procesando…
            </div>
          )}

          {tab === "Resumen" && dashboard && (
            <>
              <div className="section-line">
                <h2>Rendimiento general</h2>
                <span className="period">◷ {dashboard.period}</span>
              </div>
              <div className="stats">
                {[
                  [
                    "Inversión",
                    money(dashboard.spend_minor),
                    "Gasto simulado del período",
                  ],
                  [
                    "Ingresos atribuidos",
                    money(dashboard.revenue_minor),
                    "Atribución ficticia",
                  ],
                  [
                    "Retorno publicitario",
                    dashboard.roas == null
                      ? "—"
                      : `${dashboard.roas.toFixed(2)}×`,
                    "Ingresos / inversión",
                  ],
                  [
                    "Compras",
                    dashboard.purchases,
                    `CPA ${dashboard.cpa_minor == null ? "—" : money(dashboard.cpa_minor)}`,
                  ],
                ].map(([name, value, sub], i) => (
                  <article
                    className={`stat ${i === 2 ? "featured" : ""}`}
                    key={name}
                  >
                    <span>
                      {name}
                      <i>{["↗", "◇", "◎", "◫"][i]}</i>
                    </span>
                    <strong>{value}</strong>
                    <small>{sub}</small>
                  </article>
                ))}
              </div>
              <div className="overview-grid">
                <section className="panel performance">
                  <div className="section-line">
                    <div>
                      <h2>Cómo se reparte el resultado</h2>
                      <p>Ingresos atribuidos por campaña · demo</p>
                    </div>
                    <span className="chart-key">
                      <i /> Ingresos
                    </span>
                  </div>
                  <div
                    className="bar-chart"
                    role="img"
                    aria-label="Comparación de ingresos ficticios por campaña"
                  >
                    {dashboard.campaigns.map((c) => (
                      <div className="bar-row" key={c.id}>
                        <div>
                          <span>{c.name}</span>
                          <b>{money(c.revenue_minor)}</b>
                        </div>
                        <div className="bar-track">
                          <div
                            style={{
                              width: `${Math.max(0, (c.revenue_minor / Math.max(...dashboard.campaigns.map((item) => item.revenue_minor), 1)) * 100)}%`,
                            }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                  <p className="chart-caption">
                    Una comparación descriptiva; no representa una tendencia ni
                    una predicción.
                  </p>
                </section>
                <section className="next-step">
                  <span className="spark">✦</span>
                  <p className="eyebrow">EL SIGUIENTE PASO</p>
                  <h2>
                    Menos intuición.
                    <br />
                    Más contexto.
                  </h2>
                  <p>
                    Revisá las campañas con suficiente información y convertí
                    sus señales en propuestas de mejora.
                  </p>
                  <button onClick={() => setTab("Optimización")}>
                    Revisar oportunidades <span>↗</span>
                  </button>
                  <small>Siempre con aprobación humana.</small>
                </section>
              </div>
              <section className="panel">
                <div className="section-line">
                  <h2>Campañas de ejemplo</h2>
                  <span className="muted">
                    {dashboard.campaigns.length} campañas ·{" "}
                    {money(dashboard.active_daily_budget_minor)} / día activo
                  </span>
                </div>
                <div className="table-scroll">
                  <table>
                    <thead>
                      <tr>
                        <th>Campaña</th>
                        <th>Estado</th>
                        <th>Presupuesto / día</th>
                        <th>Inversión</th>
                        <th>Compras</th>
                        <th>ROAS</th>
                      </tr>
                    </thead>
                    <tbody>
                      {dashboard.campaigns.map((c) => (
                        <tr key={c.id}>
                          <td>
                            <strong>{c.name}</strong>
                            <small>Ventas · datos de muestra</small>
                          </td>
                          <td>
                            <span className={`badge ${c.status}`}>
                              {labels[c.status]}
                            </span>
                          </td>
                          <td>{money(c.daily_budget_minor)}</td>
                          <td>{money(c.spend_minor)}</td>
                          <td>{c.purchases}</td>
                          <td>
                            {c.spend_minor
                              ? `${(c.revenue_minor / c.spend_minor).toFixed(2)}×`
                              : "—"}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </section>
            </>
          )}

          {tab === "Productos" && (
            <div className="two-columns">
              <section>
                <div className="section-line">
                  <h2>Tu catálogo</h2>
                  <span className="muted">{products.length} productos</span>
                </div>
                <div className="product-list">
                  {products.map((p) => (
                    <article className="panel product" key={p.id}>
                      <span className="product-icon">◫</span>
                      <div>
                        <h3>{p.name}</h3>
                        <p>{p.description || "Sin descripción"}</p>
                        <strong>{money(p.price_minor)}</strong>
                        <small>
                          Margen declarado: {p.margin_pct}% · equilibrio
                          estimado {(100 / p.margin_pct).toFixed(2)}×
                        </small>
                      </div>
                      {owner && (
                        <button
                          className="text-button"
                          disabled={busy}
                          onClick={() => setEditingProduct(p)}
                        >
                          Editar
                        </button>
                      )}
                    </article>
                  ))}
                </div>
              </section>
              {owner ? (
                <form
                  className="panel form-panel"
                  key={editingProduct?.id || "new"}
                  onSubmit={saveProduct}
                >
                  <h2>
                    {editingProduct ? "Editar producto" : "Agregar producto"}
                  </h2>
                  <label>
                    Nombre
                    <input
                      name="name"
                      required
                      minLength={2}
                      maxLength={120}
                      defaultValue={editingProduct?.name}
                    />
                  </label>
                  <label>
                    Descripción
                    <textarea
                      name="description"
                      maxLength={2000}
                      defaultValue={editingProduct?.description}
                      placeholder="Qué lo hace útil, para quién y por qué"
                    />
                  </label>
                  <div className="form-row">
                    <label>
                      Precio (UYU)
                      <input
                        name="price"
                        type="number"
                        min="0.01"
                        max="1000000"
                        step="0.01"
                        required
                        defaultValue={
                          editingProduct ? editingProduct.price_minor / 100 : ""
                        }
                      />
                    </label>
                    <label>
                      Margen (%)
                      <input
                        name="margin"
                        type="number"
                        min="1"
                        max="100"
                        required
                        defaultValue={editingProduct?.margin_pct || 40}
                      />
                    </label>
                  </div>
                  <button className="primary" disabled={busy}>
                    {editingProduct
                      ? "Guardar producto"
                      : "Agregar al catálogo"}
                  </button>
                  {editingProduct && (
                    <button
                      type="button"
                      onClick={() => setEditingProduct(null)}
                    >
                      Cancelar edición
                    </button>
                  )}
                </form>
              ) : (
                <div className="panel">
                  Tenés acceso de lectura. Un administrador puede editar el
                  catálogo.
                </div>
              )}
            </div>
          )}

          {tab === "Anuncios" && (
            <>
              <div className="two-columns">
                <div className="panel form-panel">
                  <h2>Una biblioteca con contexto</h2>
                  <p>
                    Vinculá cada anuncio a un producto para crear propuestas
                    coherentes.
                  </p>
                  <div className="mini-stats">
                    <span>
                      <b>
                        {creatives.filter((c) => c.kind === "image").length}
                      </b>{" "}
                      imágenes
                    </span>
                    <span>
                      <b>
                        {creatives.filter((c) => c.kind === "video").length}
                      </b>{" "}
                      videos
                    </span>
                  </div>
                  <p className="muted">
                    El análisis comprueba archivos de imagen y su tamaño. En
                    video identifica la cabecera del contenedor. Las sugerencias
                    de texto son heurísticas; no se evalúa el contenido con IA.
                  </p>
                </div>
                {owner && (
                  <form className="panel form-panel" onSubmit={upload}>
                    <h2>Cargar anuncio</h2>
                    <label>
                      Producto
                      <select aria-label="Producto" name="product_id" required>
                        {products.map((p) => (
                          <option key={p.id} value={p.id}>
                            {p.name}
                          </option>
                        ))}
                      </select>
                    </label>
                    <label>
                      Archivo · hasta 25 MiB
                      <input
                        type="file"
                        name="file"
                        accept="image/png,image/jpeg,image/webp,video/mp4,video/webm"
                        required
                      />
                    </label>
                    <label>
                      Texto del anuncio
                      <textarea
                        name="copy"
                        maxLength={4000}
                        placeholder="Beneficio, oferta y llamada a la acción"
                      />
                    </label>
                    <button
                      className="primary"
                      disabled={busy || !products.length}
                    >
                      Cargar y analizar
                    </button>
                  </form>
                )}
              </div>
              <div className="creative-grid">
                {creatives.map((c, i) => (
                  <article className="panel creative" key={c.id}>
                    <div className={`creative-art art-${i % 3}`}>
                      <span>{c.kind === "image" ? "▧" : "▷"}</span>
                      <small>
                        {c.has_file
                          ? "ARCHIVO CARGADO"
                          : "FICHA DE MUESTRA · SIN ARCHIVO"}
                      </small>
                    </div>
                    <div className="creative-body">
                      <span className="eyebrow">
                        {c.kind === "image" ? "IMAGEN" : "VIDEO"} ·{" "}
                        {products.find((p) => p.id === c.product_id)?.name}
                      </span>
                      <h3>{c.name}</h3>
                      <p>{c.copy || "Sin texto"}</p>
                      {c.analysis.width && (
                        <span className="badge">
                          {c.analysis.width} × {c.analysis.height} px
                        </span>
                      )}
                      <ul>
                        {c.analysis.notes.map((note) => (
                          <li key={note}>{note}</li>
                        ))}
                      </ul>
                      {c.has_file && (
                        <button disabled={busy} onClick={() => download(c.id)}>
                          Descargar archivo
                        </button>
                      )}
                    </div>
                  </article>
                ))}
              </div>
            </>
          )}

          {tab === "Planificador" && (
            <>
              <div className="two-columns">
                <form
                  className="panel form-panel"
                  onSubmit={async (e) => {
                    e.preventDefault();
                    await mutate(
                      "/api/proposals",
                      {
                        product_id: selectedProduct,
                        creative_ids: selectedAds,
                        daily_budget_minor: Math.round(Number(budget) * 100),
                        target_cpa_minor: Math.round(Number(cpa) * 100),
                        country,
                        age_min: Number(ageMin),
                        age_max: Number(ageMax),
                      },
                      "POST",
                      "Propuesta generada. Revisá el razonamiento antes de aprobar.",
                    );
                  }}
                >
                  <h2>Prepará el contexto</h2>
                  <label>
                    Producto
                    <select
                      aria-label="Producto"
                      value={selectedProduct}
                      onChange={(e) => {
                        setSelectedProduct(e.target.value);
                        setSelectedAds([]);
                      }}
                    >
                      {products.map((p) => (
                        <option key={p.id} value={p.id}>
                          {p.name}
                        </option>
                      ))}
                    </select>
                  </label>
                  <div className="form-row">
                    <label>
                      Presupuesto diario (UYU)
                      <input
                        type="number"
                        min="0.01"
                        max={rules ? rules.max_daily_minor / 100 : 1000000}
                        step="0.01"
                        required
                        value={budget}
                        onChange={(e) => setBudget(e.target.value)}
                      />
                    </label>
                    <label>
                      CPA objetivo (UYU)
                      <input
                        type="number"
                        min="0.01"
                        step="0.01"
                        required
                        value={cpa}
                        onChange={(e) => setCpa(e.target.value)}
                      />
                    </label>
                  </div>
                  <div className="form-row">
                    <label>
                      País
                      <select
                        aria-label="País"
                        value={country}
                        onChange={(e) => setCountry(e.target.value)}
                      >
                        <option value="UY">Uruguay</option>
                        <option value="AR">Argentina</option>
                        <option value="MX">México</option>
                        <option value="ES">España</option>
                        <option value="US">Estados Unidos</option>
                        <option value="CL">Chile</option>
                        <option value="CO">Colombia</option>
                      </select>
                    </label>
                    <label>
                      Edad mínima
                      <input
                        type="number"
                        min="18"
                        max="65"
                        value={ageMin}
                        onChange={(e) => setAgeMin(e.target.value)}
                        required
                      />
                    </label>
                    <label>
                      Edad máxima (65+)
                      <input
                        type="number"
                        min={ageMin}
                        max="65"
                        value={ageMax}
                        onChange={(e) => setAgeMax(e.target.value)}
                        required
                      />
                    </label>
                  </div>
                  <fieldset>
                    <legend>
                      Elegí los anuncios ({selectedAds.length}/20)
                    </legend>
                    {creatives
                      .filter((c) => c.product_id === selectedProduct)
                      .map((c) => (
                        <label className="check" key={c.id}>
                          <input
                            type="checkbox"
                            checked={selectedAds.includes(c.id)}
                            onChange={(e) =>
                              setSelectedAds((current) =>
                                e.target.checked
                                  ? [...current, c.id]
                                  : current.filter((id) => id !== c.id),
                              )
                            }
                          />
                          <span>
                            {c.name}
                            <small>
                              {c.kind === "image" ? "Imagen" : "Video"} ·{" "}
                              {c.has_file ? "archivo cargado" : "ficha demo"}
                            </small>
                          </span>
                        </label>
                      ))}
                  </fieldset>
                  <button
                    className="primary"
                    disabled={
                      busy ||
                      !owner ||
                      selectedAds.length === 0 ||
                      selectedAds.length > 20
                    }
                  >
                    ✦ Generar propuesta
                  </button>
                </form>
                <section className="panel guide">
                  <span className="spark">✦</span>
                  <h2>
                    Una hipótesis,
                    <br />
                    con sus razones.
                  </h2>
                  <p>
                    El motor compara presupuesto y CPA objetivo para sugerir ABO
                    o CBO. Distribuye los anuncios y explica la decisión.
                  </p>
                  <ol>
                    <li>ABO: distribución explícita por conjunto.</li>
                    <li>CBO: presupuesto a nivel de campaña.</li>
                    <li>Revisión: aprobar solo guarda tu decisión.</li>
                  </ol>
                  <div className="callout">
                    No existe una estrategia universalmente ganadora. Este demo
                    no consulta tendencias actuales ni predice ventas.
                  </div>
                  <p>
                    Límite de la empresa:{" "}
                    <strong>{money(rules?.max_daily_minor || 0)} / día</strong>
                  </p>
                </section>
              </div>
              <div className="section-line">
                <h2>Propuestas guardadas</h2>
                <span className="muted">{proposals.length} propuestas</span>
              </div>
              {!proposals.length && (
                <div className="empty">
                  Tu primer plan empieza arriba. Elegí al menos un anuncio.
                </div>
              )}
              {proposals.map((p) => (
                <article className="panel proposal" key={p.id}>
                  <div className="section-line">
                    <div>
                      <h2>{p.title}</h2>
                      <p>
                        {money(p.plan.daily_budget_minor)} / día · motor de
                        reglas demo
                      </p>
                    </div>
                    <span className={`badge ${p.status}`}>
                      {labels[p.status]}
                    </span>
                  </div>
                  <div className="adsets">
                    {p.plan.ad_sets.map((group, i) => (
                      <div key={group.name}>
                        <span className="eyebrow">CONJUNTO 0{i + 1}</span>
                        <h3>{group.name}</h3>
                        <p>
                          {group.daily_budget_minor == null
                            ? "Presupuesto compartido CBO"
                            : `${money(group.daily_budget_minor)} / día`}
                        </p>
                        <small>
                          {group.audience.country} · {group.audience.age_min}–
                          {group.audience.age_max === 65
                            ? "65+"
                            : group.audience.age_max}{" "}
                          años
                        </small>
                        <ul>
                          {group.creative_ids.map((id) => (
                            <li key={id}>
                              {creatives.find((c) => c.id === id)?.name || id}
                            </li>
                          ))}
                        </ul>
                      </div>
                    ))}
                  </div>
                  <details open>
                    <summary>Por qué esta estructura</summary>
                    <ul>
                      {p.plan.reasoning.map((text) => (
                        <li key={text}>{text}</li>
                      ))}
                    </ul>
                    <h3>Ideas para probar</h3>
                    <ul>
                      {p.plan.creative_briefs.map((text) => (
                        <li key={text}>{text}</li>
                      ))}
                    </ul>
                    <p className="muted">{p.plan.warnings.join(" ")}</p>
                  </details>
                  {p.status === "pending" && owner && (
                    <div className="actions">
                      <button
                        className="primary"
                        disabled={busy}
                        onClick={() =>
                          mutate(
                            `/api/proposals/${p.id}/decision`,
                            { decision: "approve" },
                            "POST",
                            "Propuesta aprobada y guardada. No se publicó en Meta.",
                          )
                        }
                      >
                        Aprobar propuesta
                      </button>
                      <button
                        disabled={busy}
                        onClick={() =>
                          mutate(`/api/proposals/${p.id}/decision`, {
                            decision: "reject",
                          })
                        }
                      >
                        Rechazar
                      </button>
                    </div>
                  )}
                  <small className="muted">
                    Publicación real deshabilitada en este MVP.
                  </small>
                </article>
              ))}
            </>
          )}

          {tab === "Optimización" && (
            <>
              <div className="panel section-line">
                <div>
                  <h2>Un cambio a la vez</h2>
                  <p>
                    Solo se evalúan datos ficticios. Aprobar y simular son pasos
                    separados.
                  </p>
                </div>
                <button
                  className="primary"
                  disabled={busy || !owner}
                  onClick={() =>
                    mutate(
                      "/api/optimization/evaluate",
                      undefined,
                      "POST",
                      "Evaluación completa. Las campañas siguen sin cambios.",
                    )
                  }
                >
                  Evaluar campañas
                </button>
              </div>
              <div className="rule-summary">
                <span>
                  Observación mínima <b>{rules?.min_days} días</b>
                </span>
                <span>
                  Escalado desde{" "}
                  <b>
                    {rules?.min_purchases_scale} compras · ROAS{" "}
                    {rules?.min_roas_scale}×
                  </b>
                </span>
                <span>
                  Aumento máximo <b>{rules?.max_increase_pct}%</b>
                </span>
              </div>
              {!recommendations.length && (
                <div className="empty">
                  Todavía no hay recomendaciones. Evaluá las campañas para
                  encontrar señales.
                </div>
              )}
              {recommendations.map((r) => (
                <article className="panel recommendation" key={r.id}>
                  <div className="section-line">
                    <div>
                      <span className="eyebrow">
                        {
                          dashboard?.campaigns.find(
                            (c) => c.id === r.campaign_id,
                          )?.name
                        }
                      </span>
                      <h2>
                        {r.action === "pause"
                          ? "Pausar campaña"
                          : "Aumentar presupuesto"}
                      </h2>
                    </div>
                    <span className={`badge ${r.status}`}>
                      {labels[r.status]}
                    </span>
                  </div>
                  <p>{r.reason}</p>
                  {r.suggested_budget_minor != null && (
                    <p>
                      Presupuesto diario propuesto:{" "}
                      <strong>{money(r.suggested_budget_minor)}</strong>
                    </p>
                  )}
                  {owner && (
                    <div className="actions">
                      {r.status === "pending" && (
                        <>
                          <button
                            className="primary"
                            disabled={busy}
                            onClick={() =>
                              mutate(`/api/recommendations/${r.id}/decision`, {
                                decision: "approve",
                              })
                            }
                          >
                            Aprobar cambio
                          </button>
                          <button
                            disabled={busy}
                            onClick={() =>
                              mutate(`/api/recommendations/${r.id}/decision`, {
                                decision: "reject",
                              })
                            }
                          >
                            Rechazar
                          </button>
                        </>
                      )}
                      {r.status === "approved" && (
                        <button
                          className="primary"
                          disabled={busy}
                          onClick={() =>
                            mutate(
                              `/api/recommendations/${r.id}/apply`,
                              undefined,
                              "POST",
                              "Simulación aplicada a datos locales. No hubo cambios en Meta.",
                            )
                          }
                        >
                          Aplicar simulación
                        </button>
                      )}
                    </div>
                  )}
                </article>
              ))}
            </>
          )}

          {tab === "Actividad" && (
            <section className="panel">
              <h2>Historial de decisiones</h2>
              <p>
                Últimos 100 eventos de esta empresa, del más reciente al más
                antiguo.
              </p>
              {!audit.length && (
                <div className="empty">
                  El historial se completa al cargar anuncios, crear propuestas
                  y revisar cambios.
                </div>
              )}
              <div className="timeline">
                {audit.map((a) => (
                  <article key={a.id}>
                    <span className="timeline-dot" />
                    <div>
                      <strong>
                        {eventLabels[a.action] || "Actividad registrada"}
                      </strong>
                      <small>
                        {new Date(a.created_at).toLocaleString("es-UY")}
                      </small>
                      <details>
                        <summary>Ver registro</summary>
                        <code>{a.entity_id}</code>
                        {Object.keys(a.detail).length > 0 && (
                          <pre>{JSON.stringify(a.detail, null, 2)}</pre>
                        )}
                      </details>
                    </div>
                  </article>
                ))}
              </div>
            </section>
          )}

          {tab === "Configuración" && (
            <div className="two-columns">
              <form
                className="panel form-panel"
                key={`${rules?.max_daily_minor}-${rules?.max_increase_pct}`}
                onSubmit={async (e) => {
                  e.preventDefault();
                  const data = new FormData(e.currentTarget);
                  await mutate(
                    "/api/rules",
                    {
                      max_daily_minor: Math.round(
                        Number(data.get("limit")) * 100,
                      ),
                      max_increase_pct: Number(data.get("increase")),
                    },
                    "PUT",
                  );
                }}
              >
                <h2>Reglas de presupuesto</h2>
                <p>
                  El límite agregado se vuelve a comprobar al aplicar cada
                  aumento simulado.
                </p>
                <label>
                  Límite diario de la empresa (UYU)
                  <input
                    name="limit"
                    type="number"
                    min="0.01"
                    max="1000000"
                    step="0.01"
                    required
                    defaultValue={(rules?.max_daily_minor || 0) / 100}
                  />
                </label>
                <label>
                  Aumento máximo por cambio (%)
                  <input
                    name="increase"
                    type="number"
                    min="1"
                    max="20"
                    required
                    defaultValue={rules?.max_increase_pct}
                  />
                </label>
                <button className="primary" disabled={busy || !owner}>
                  Guardar reglas
                </button>
                <small>
                  Un período mínimo y un número de compras no garantizan
                  significancia estadística. Revisá atribución, márgenes y
                  retrasos de conversión.
                </small>
              </form>
              <section className="panel integration">
                <span className="integration-icon">∞</span>
                <span className="badge pending">Desconectado</span>
                <h2>Meta Ads</h2>
                <p>
                  La conexión OAuth y la sincronización con Marketing API están
                  pendientes. No se importaron cuentas, campañas ni métricas
                  reales.
                </p>
                <button disabled>
                  Conexión disponible en una próxima etapa
                </button>
                <div className="callout">
                  No necesitás ni debés cargar tokens reales para probar este
                  demo.
                </div>
              </section>
            </div>
          )}
          <footer>
            Meta Ads AI <span>Planificá con contexto. Decidí con control.</span>
            <small>Demo v0.1 · Sin afiliación con Meta</small>
          </footer>
        </main>
      </div>
    </div>
  );
}
