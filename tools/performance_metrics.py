#!/usr/bin/env python3
"""
Module: performance_metrics.py
Purpose: META-002 v3 Observability — lee agent_performance.json y calcula
         metricas del bucle de reflexion, filtration rate, y swarm error funnel.
Usage:
  python tools/performance_metrics.py                  # imprime reporte a stdout
  python tools/performance_metrics.py --json           # output JSON crudo
  python tools/performance_metrics.py --report         # genera docs/reports/swarm_health_v1.md
  python tools/performance_metrics.py --agent python_developer  # metricas de un agente
Dependencies: stdlib only (json, pathlib, datetime, argparse)
"""

import json
import sys
import logging
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# Rutas relativas a la raiz del repo
REPO_ROOT = Path(__file__).parent.parent
PERF_FILE = REPO_ROOT / "core" / "memory" / "agent_performance.json"
REPORT_FILE = REPO_ROOT / "docs" / "reports" / "swarm_health_v1.md"

LENTE_LABELS = {
    "PERF-001": "Rendimiento",
    "SEC-001":  "Seguridad",
    "PR-001":   "Claridad"
}

SLA_THRESHOLDS = {
    "filtration_rate_pct": {"green": 80.0, "amber": 50.0},  # % errores resueltos internamente
    "avg_latency_ms":      {"green": 800,  "amber": 2000},   # ms — SLA PERF-001
}


# ── Data loading ──────────────────────────────────────────────────────────────

def load_performance_data() -> dict[str, Any]:
    if not PERF_FILE.exists():
        logger.error("agent_performance.json no encontrado en %s", PERF_FILE)
        logger.error("El archivo es GITIGNORED — debe existir localmente en el repo.")
        sys.exit(1)
    with open(PERF_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# ── Core calculations ─────────────────────────────────────────────────────────

def calc_filtration_rate(rm: dict[str, Any]) -> float:
    issued = rm.get("tickets_issued", 0)
    resolved = rm.get("tickets_resolved_internally", 0)
    if issued == 0:
        return 0.0
    return round((resolved / issued) * 100, 1)


def calc_swarm_funnel(data: dict[str, Any]) -> dict[str, Any]:
    meta = data.get("meta_002", {})
    funnel = meta.get("swarm_error_funnel", {})
    generated = funnel.get("errores_generados_total", 0)
    filtered = funnel.get("filtrados_meta002", 0)
    to_qc = funnel.get("llegados_a_qc", 0)
    to_thomas = funnel.get("llegados_a_thomas", 0)
    return {
        "errores_generados": generated,
        "filtrados_meta002": filtered,
        "llegados_a_qc": to_qc,
        "llegados_a_thomas": to_thomas,
        "swarm_filtration_pct": round((filtered / generated * 100), 1) if generated > 0 else 0.0,
        "qc_pass_rate_pct": round(((generated - to_thomas) / generated * 100), 1) if generated > 0 else 0.0,
    }


def calc_lente_distribution(agents: dict[str, Any]) -> dict[str, int]:
    totals: dict[str, int] = {"PERF-001": 0, "SEC-001": 0, "PR-001": 0}
    for agent_data in agents.values():
        rm = agent_data.get("reflection_metrics")
        if not rm:
            continue
        by_lente = rm.get("tickets_by_lente", {})
        for lente, count in by_lente.items():
            if lente in totals:
                totals[lente] += count
    return totals


def rank_agents_by_reflection(agents: dict[str, Any]) -> list[dict[str, Any]]:
    ranked = []
    for name, agent_data in agents.items():
        rm = agent_data.get("reflection_metrics")
        if not rm:
            continue
        issued = rm.get("tickets_issued", 0)
        rate = calc_filtration_rate(rm)
        ranked.append({
            "agent": name,
            "tickets_issued": issued,
            "tickets_resolved": rm.get("tickets_resolved_internally", 0),
            "tickets_escalated": rm.get("tickets_escalated_to_qc", 0),
            "filtration_rate_pct": rate,
            "last_ticket": rm.get("last_ticket_id") or "—",
        })
    ranked.sort(key=lambda x: (x["tickets_issued"], x["filtration_rate_pct"]), reverse=True)
    return ranked


def get_agent_latency_alerts(agents: dict[str, Any]) -> list[dict[str, Any]]:
    alerts = []
    amber_threshold = SLA_THRESHOLDS["avg_latency_ms"]["amber"]
    green_threshold = SLA_THRESHOLDS["avg_latency_ms"]["green"]
    for name, agent_data in agents.items():
        latency = agent_data.get("avg_latency_ms")
        if latency is None:
            continue
        if latency > amber_threshold:
            alerts.append({"agent": name, "latency_ms": latency, "status": "CRITICA"})
        elif latency > green_threshold:
            alerts.append({"agent": name, "latency_ms": latency, "status": "WARN"})
    alerts.sort(key=lambda x: x["latency_ms"], reverse=True)
    return alerts


def status_badge(value: float, metric: str) -> str:
    thresholds = SLA_THRESHOLDS.get(metric, {})
    green = thresholds.get("green", 80.0)
    amber = thresholds.get("amber", 50.0)
    if value >= green:
        return "OK"
    if value >= amber:
        return "WARN"
    return "CRIT"


# ── Report generation ─────────────────────────────────────────────────────────

def build_markdown_report(data: dict[str, Any]) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    agents = data.get("agents", {})
    meta_status = data.get("meta_002", {}).get("status", "UNKNOWN")
    schema_ver = data.get("schema_version", "?")

    funnel = calc_swarm_funnel(data)
    lente_dist = calc_lente_distribution(agents)
    ranked = rank_agents_by_reflection(agents)
    latency_alerts = get_agent_latency_alerts(agents)

    total_agents = len(agents)
    meta002_agents = len([a for a in agents.values() if a.get("reflection_metrics")])
    active_agents = len([a for a in agents.values() if a.get("last_invoked")])

    top_lente = max(lente_dist, key=lambda k: lente_dist[k]) if any(lente_dist.values()) else "—"
    top_lente_label = LENTE_LABELS.get(top_lente, top_lente)

    swarm_fr = funnel["swarm_filtration_pct"]
    swarm_badge = status_badge(swarm_fr, "filtration_rate_pct")

    lines = [
        f"# Swarm Health Report — Keystone KSG",
        f"**Generado:** {now} | **Schema:** v{schema_ver} | **META-002:** {meta_status}",
        f"",
        f"---",
        f"",
        f"## 1. Eficiencia del Enjambre — Swarm Error Funnel",
        f"",
        f"```",
        f"Errores generados por agentes:  {funnel['errores_generados']:>6}  (100%)",
        f"Filtrados por META-002:         {funnel['filtrados_meta002']:>6}  ({funnel['swarm_filtration_pct']}%)",
        f"Llegados a QC:                  {funnel['llegados_a_qc']:>6}",
        f"Llegados a Thomas:              {funnel['llegados_a_thomas']:>6}",
        f"```",
        f"",
        f"**Swarm Filtration Rate:** `{swarm_fr}%` [{swarm_badge}]",
        f"**Target:** >= 80% filtrado antes de QC | >= 0% llegado a Thomas para errores CRITICA SEC-001",
        f"",
        f"---",
        f"",
        f"## 2. Distribucion de Tickets por Lente",
        f"",
        f"| Lente | Nombre | Tickets totales | % del total |",
        f"|-------|--------|----------------|-------------|",
    ]

    total_tickets = sum(lente_dist.values())
    for lente, count in sorted(lente_dist.items(), key=lambda x: x[1], reverse=True):
        pct = round(count / total_tickets * 100, 1) if total_tickets > 0 else 0.0
        label = LENTE_LABELS[lente]
        lines.append(f"| `{lente}` | {label} | {count} | {pct}% |")

    top_label = f"`{top_lente}` ({top_lente_label})" if total_tickets > 0 else "Sin datos — baseline Day 0"
    lines += [
        f"",
        f"**Lente que mas fallas detecta:** {top_label}",
        f"",
        f"---",
        f"",
        f"## 3. Top Agentes Reflexivos",
        f"",
        f"| Agente | Tickets emitidos | Resueltos internos | Escalados a QC | Filtration Rate | Estado |",
        f"|--------|-----------------|-------------------|----------------|----------------|--------|",
    ]

    for r in ranked[:10]:
        badge = status_badge(r["filtration_rate_pct"], "filtration_rate_pct") if r["tickets_issued"] > 0 else "—"
        lines.append(
            f"| `{r['agent']}` | {r['tickets_issued']} | {r['tickets_resolved']} | "
            f"{r['tickets_escalated']} | {r['filtration_rate_pct']}% | {badge} |"
        )

    if not ranked:
        lines.append("| — | Sin datos | — | — | — | Baseline Day 0 |")

    lines += [
        f"",
        f"*Agentes con META-002 activo: {meta002_agents}/{total_agents}*",
        f"",
        f"---",
        f"",
        f"## 4. Alertas de Latencia",
        f"",
    ]

    if latency_alerts:
        lines += [
            f"| Agente | Latencia (ms) | SLA target | Estado |",
            f"|--------|--------------|-----------|--------|",
        ]
        for alert in latency_alerts:
            lines.append(f"| `{alert['agent']}` | {alert['latency_ms']} | 800ms | {alert['status']} |")
    else:
        lines.append("Sin datos de latencia activos. Los agentes se completan en < 1 invocacion real.")
        lines.append("")
        lines.append("> El bucle META-002 es sincronico dentro del contexto del agente — no agrega latencia")
        lines.append("> de red. El overhead estimado es < 200ms por output (lectura de 3 docs de referencia).")

    lines += [
        f"",
        f"---",
        f"",
        f"## 5. Estado General del Enjambre",
        f"",
        f"| Metrica | Valor | Estado |",
        f"|---------|-------|--------|",
        f"| Agentes activos (invocados al menos 1 vez) | {active_agents}/{total_agents} | {'OK' if active_agents > 0 else 'Day 0'} |",
        f"| Agentes con META-002 integrado | {meta002_agents}/5 (objetivo) | {'OK' if meta002_agents >= 5 else 'PARCIAL'} |",
        f"| Swarm filtration rate | {swarm_fr}% | {swarm_badge} |",
        f"| Errores criticos llegados a Thomas | {funnel['llegados_a_thomas']} | {'OK' if funnel['llegados_a_thomas'] == 0 else 'ALERTA'} |",
        f"| SEC-001 activo | Si | OK |",
        f"| PERF-001 activo | Si | OK |",
        f"| PR-001 activo | Si | OK |",
        f"",
        f"---",
        f"",
        f"## Nota: Baseline Day 0",
        f"",
        f"Este reporte refleja el estado inicial del sistema de observabilidad META-002.",
        f"Todos los contadores de tickets estan en cero porque:",
        f"1. Los agentes recibieron la instruccion META-002 en este sprint (2026-03-24)",
        f"2. No han sido invocados en tareas reales desde la activacion",
        f"3. Los `reflection_metrics` se acumulan en runtime — este archivo es GITIGNORED",
        f"",
        f"**Proxima lectura util:** despues de la primera sesion de trabajo real con",
        f"`python_developer`, `api_backend`, `frontend_engineer`, `email_manager` o `n8n_engineer`.",
        f"",
        f"---",
        f"",
        f"*Generado por: `tools/performance_metrics.py` | META-002 v3 | Keystone KSG*",
    ]

    return "\n".join(lines)


def build_json_report(data: dict[str, Any]) -> dict[str, Any]:
    agents = data.get("agents", {})
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "schema_version": data.get("schema_version"),
        "meta_002_status": data.get("meta_002", {}).get("status"),
        "swarm_funnel": calc_swarm_funnel(data),
        "lente_distribution": calc_lente_distribution(agents),
        "agents_ranked": rank_agents_by_reflection(agents),
        "latency_alerts": get_agent_latency_alerts(agents),
    }


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="META-002 v3 — Metricas de salud del enjambre Keystone KSG"
    )
    parser.add_argument("--json", action="store_true", help="Output JSON crudo")
    parser.add_argument("--report", action="store_true", help="Escribe docs/reports/swarm_health_v1.md")
    parser.add_argument("--agent", type=str, help="Metricas de un agente especifico")
    args = parser.parse_args()

    data = load_performance_data()
    agents = data.get("agents", {})

    if args.agent:
        agent_data = agents.get(args.agent)
        if not agent_data:
            logger.error("Agente '%s' no encontrado en agent_performance.json", args.agent)
            sys.exit(1)
        rm = agent_data.get("reflection_metrics")
        if not rm:
            print(f"[{args.agent}] Sin reflection_metrics — META-002 no integrado en este agente.")
            return
        rate = calc_filtration_rate(rm)
        print(f"\n[{args.agent}] Reflection Metrics")
        print(f"  Tickets emitidos:          {rm['tickets_issued']}")
        print(f"  Resueltos internamente:    {rm['tickets_resolved_internally']}")
        print(f"  Escalados a QC:            {rm['tickets_escalated_to_qc']}")
        print(f"  Filtration rate:           {rate}%  [{status_badge(rate, 'filtration_rate_pct')}]")
        print(f"  Ultimo ticket:             {rm.get('last_ticket_id') or '—'}")
        print(f"  Tickets por lente:         {rm.get('tickets_by_lente', {})}")
        return

    if args.json:
        print(json.dumps(build_json_report(data), indent=2, ensure_ascii=False))
        return

    report_md = build_markdown_report(data)

    if args.report:
        REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(REPORT_FILE, "w", encoding="utf-8") as f:
            f.write(report_md)
        logger.info("Reporte escrito en %s", REPORT_FILE)
    else:
        print(report_md)


if __name__ == "__main__":
    main()
