"""Motor heurístico versionado: no llama modelos ni promete resultados."""

import io
from PIL import Image, UnidentifiedImageError

ENGINE_VERSION = "rules-v1"


def analyze(data: bytes, copy: str):
    notes = []
    try:
        with Image.open(io.BytesIO(data)) as image:
            image.verify()
        with Image.open(io.BytesIO(data)) as image:
            width, height = image.size
            mime = Image.MIME[image.format]
            if image.format not in ("JPEG", "PNG", "WEBP") or width * height > 40_000_000:
                raise ValueError("Imagen no admitida o excesivamente grande")
        if width < 1080:
            notes.append("Probar una versión de al menos 1080 píxeles de ancho.")
        ratio = width / height
        notes.append("Preparar recortes 4:5 y 9:16 y revisar las zonas seguras.")
        result = {"kind": "image", "mime": mime, "width": width, "height": height, "ratio": round(ratio, 3)}
    except (UnidentifiedImageError, OSError, SyntaxError):
        if len(data) >= 12 and data[4:8] == b"ftyp":
            mime = "video/mp4"
        elif data[:4] == b"\x1aE\xdf\xa3":
            mime = "video/webm"
        else:
            raise ValueError("Solo se admiten JPEG, PNG, WEBP, MP4 y WEBM reconocibles") from None
        result = {"kind": "video", "mime": mime, "width": None, "height": None, "ratio": None}
        notes.append("Contenedor reconocido por cabecera; duración, códec y contenido aún no verificados. Revisar manualmente.")
        notes.append("Probar un inicio que muestre el uso del producto y subtítulos legibles.")
    if not copy.strip():
        notes.append("Agregar texto, beneficio comprobable y llamada a la acción.")
    elif len(copy) > 500:
        notes.append("Probar un texto más breve junto a la versión actual.")
    notes.append("Evaluación técnica y reglas de texto; no se realizó análisis visual ni de audio con IA.")
    return {**result, "bytes": len(data), "notes": notes, "engine": ENGINE_VERSION}


def build_plan(payload, creatives, product, tenant):
    # Presupuesto/coste objetivo orientan una hipótesis, no demuestran causalidad.
    strategy = "ABO" if payload.daily_budget_minor < payload.target_cpa_minor * 10 else "CBO"
    group_count = min(2 if strategy == "ABO" else 3, len(creatives), max(1, payload.daily_budget_minor // payload.target_cpa_minor))
    quotient, remainder = divmod(payload.daily_budget_minor, group_count)
    groups = []
    for index in range(group_count):
        group = creatives[index::group_count]
        groups.append(
            {
                "name": f"Exploración {index + 1}",
                "creative_ids": [item.id for item in group],
                "daily_budget_minor": quotient + (1 if index < remainder else 0) if strategy == "ABO" else None,
                "audience": {"country": payload.country, "age_min": payload.age_min, "age_max": payload.age_max},
            }
        )
    break_even_roas = round(100 / product.margin_pct, 2)
    return {
        "engine": ENGINE_VERSION,
        "provider": "deterministic-demo",
        "objective": "SALES",
        "strategy": strategy,
        "currency": tenant.currency,
        "product_id": product.id,
        "daily_budget_minor": payload.daily_budget_minor,
        "campaign_budget_minor": payload.daily_budget_minor if strategy == "CBO" else None,
        "target_cpa_minor": payload.target_cpa_minor,
        "ad_sets": groups,
        "reasoning": [
            f"{strategy} es una hipótesis según la relación presupuesto / CPA objetivo; requiere un experimento controlado.",
            "Se distribuyeron todos los anuncios una sola vez sin conjuntos vacíos.",
            f"ROAS de equilibrio estimado: {break_even_roas} con margen declarado de {product.margin_pct}%; no incluye gastos fijos.",
        ],
        "warnings": [
            "Datos de demo. No existe conexión a Meta.",
            "El CPA objetivo es una entrada del usuario, no una predicción.",
            "65 representa 65+; revisar elegibilidad, políticas y categorías especiales antes de conectar Meta.",
        ],
        "creative_briefs": [
            f"Demostración de {product.name}: mostrar uso real, beneficio verificable y cierre con llamada a la acción.",
            "Comparar dos aperturas con la misma oferta; medir compras y coste por compra.",
        ],
        "publishable": False,
    }


def evaluate(campaign, tenant):
    if campaign.status != "active" or campaign.days_observed < 3 or campaign.spend_minor < 10000:
        return None
    roas = campaign.revenue_minor / campaign.spend_minor if campaign.spend_minor else 0
    if campaign.purchases == 0 and campaign.spend_minor >= campaign.daily_budget_minor * 2:
        return {
            "action": "pause",
            "reason": "Sin compras tras gastar al menos dos presupuestos diarios y observar 3 días. Revisar atribución antes de aprobar.",
            "suggested_budget_minor": None,
        }
    if campaign.purchases >= 10 and roas >= 3:
        budget = campaign.daily_budget_minor * (100 + tenant.max_increase_pct) // 100
        return {
            "action": "increase_budget",
            "reason": f"{campaign.purchases} compras, ROAS {roas:.2f}; propone aumento limitado a {tenant.max_increase_pct}%. No demuestra resultados futuros.",
            "suggested_budget_minor": budget,
        }
    return None
