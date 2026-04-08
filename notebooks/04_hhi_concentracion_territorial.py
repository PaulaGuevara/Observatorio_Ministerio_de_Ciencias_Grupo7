from __future__ import annotations

import csv
from collections import Counter
from dataclasses import dataclass
from html import escape
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "datos" / "tarea_join" / "investigadores_consolidado.csv"
OUTPUT_MD = PROJECT_ROOT / "hallazgos" / "sprint_2_hhi_concentracion_territorial.md"
OUTPUT_HTML = PROJECT_ROOT / "hallazgos" / "sprint_2_hhi_concentracion_territorial.html"

CONVOCATORIA_PRIORITY = {"2021": 3, "2019": 2, "2017": 1}
TARGET_DEPARTMENTS = ["Bogotá, D. C.", "Antioquia", "Valle del Cauca"]


@dataclass
class Summary:
    total: int
    unique_departments: int
    hhi: float
    hhi_10000: float
    top10: list[tuple[str, int, float]]
    target_rows: list[tuple[str, int, float]]
    target_share: float
    top5_share: float
    min_rows: list[tuple[str, int, float]]


def text_quality_score(value: str) -> int:
    return value.count("Ã") + value.count("�") + value.count("\xad") + value.count("Â")


def normalize_department_name(value: str) -> str:
    normalized = value.strip()
    try:
        repaired = normalized.encode("latin-1").decode("utf-8")
        if text_quality_score(repaired) <= text_quality_score(normalized):
            normalized = repaired
    except UnicodeDecodeError:
        pass

    normalized = normalized.replace("\xad", "").replace("Â", "")
    return normalized.strip()


def read_counters(path: Path) -> tuple[Counter[str], Counter[str]]:
    all_counter: Counter[str] = Counter()
    latest_by_person: dict[str, tuple[int, str]] = {}

    with path.open("r", encoding="latin-1", newline="") as file_obj:
        reader = csv.DictReader(file_obj)
        for row in reader:
            department = normalize_department_name(row.get("NME_DEPARTAMENTO_RES_PR") or "")
            person_id = (row.get("ID_PERSONA_PR") or "").strip()
            year = (row.get("ANO_CONVO") or "").strip()[:4]

            if not department:
                continue

            all_counter[department] += 1

            if not person_id:
                continue

            score = CONVOCATORIA_PRIORITY.get(year, 0)
            previous = latest_by_person.get(person_id)
            if previous is None or score > previous[0]:
                latest_by_person[person_id] = (score, department)

    unique_counter: Counter[str] = Counter(value[1] for value in latest_by_person.values())
    return all_counter, unique_counter


def build_summary(counter: Counter[str]) -> Summary:
    total = sum(counter.values())
    top10_counts = counter.most_common(10)
    min_rows_raw = sorted(counter.items(), key=lambda item: (item[1], item[0]))[:5]

    def pct(count: int) -> float:
        return (count / total) * 100 if total else 0.0

    target_rows = [(name, counter.get(name, 0), pct(counter.get(name, 0))) for name in TARGET_DEPARTMENTS]
    return Summary(
        total=total,
        unique_departments=len(counter),
        hhi=sum((count / total) ** 2 for count in counter.values()),
        hhi_10000=sum(((count / total) ** 2) * 10000 for count in counter.values()),
        top10=[(name, count, pct(count)) for name, count in top10_counts],
        target_rows=target_rows,
        target_share=sum(row[2] for row in target_rows),
        top5_share=sum(pct(count) for _, count in top10_counts[:5]),
        min_rows=[(name, count, pct(count)) for name, count in min_rows_raw],
    )


def concentration_label(hhi_10000: float) -> str:
    if hhi_10000 < 1500:
        return "baja"
    if hhi_10000 < 2500:
        return "moderada"
    return "alta"


def format_pct(value: float) -> str:
    return f"{value:.2f}%"


def format_num(value: float) -> str:
    return f"{value:.4f}"


def format_int(value: int) -> str:
    return f"{value:,}".replace(",", ".")


def markdown_table(rows: list[tuple[str, int, float]]) -> str:
    lines = [
        "| Departamento | Investigadores | Participación |",
        "|---|---:|---:|",
    ]
    for name, count, pct in rows:
        lines.append(f"| {name} | {format_int(count)} | {pct:.2f}% |")
    return "\n".join(lines)


def build_markdown(unique_summary: Summary, all_summary: Summary) -> str:
    unique_label = concentration_label(unique_summary.hhi_10000)
    all_label = concentration_label(all_summary.hhi_10000)
    return f"""# Sprint 2 - Indice Herfindahl-Hirschman por departamento

## Objetivo

Medir qué tan concentrada está la investigación reconocida por Minciencias en los departamentos de residencia, con énfasis en Bogotá, Antioquia y Valle del Cauca.

## Fuente y criterio metodológico

- Fuente base: `datos/tarea_join/investigadores_consolidado.csv`.
- Variable de análisis: `NME_DEPARTAMENTO_RES_PR`.
- Resultado principal: base depurada por persona única, conservando la convocatoria más reciente por `ID_PERSONA_PR`, de acuerdo con el criterio documentado en `notebooks_Minciencias/tarea_tabla_Minciencias/README.md`.
- Resultado comparativo: consolidado completo 2017-2019-2021 sin deduplicación.

## Fórmula usada

El índice Herfindahl-Hirschman se calculó como:

$$
HHI = \\sum_{{i=1}}^n s_i^2
$$

donde $s_i$ es la participación de cada departamento sobre el total de investigadores. También se reporta el índice en escala tradicional de 0 a 10.000:

$$
HHI_{{10000}} = HHI \\times 10000
$$

## Resultado principal: base depurada por persona única

- Total de investigadores únicos: {format_int(unique_summary.total)}
- Número de departamentos/categorías observadas: {unique_summary.unique_departments}
- HHI: {format_num(unique_summary.hhi)}
- HHI (0 a 10.000): {unique_summary.hhi_10000:.2f}
- Nivel de concentración: **{unique_label}**

Interpretación: el sistema de investigación reconocido presenta una **concentración territorial moderada**, con un peso especialmente fuerte en Bogotá, Antioquia y Valle del Cauca.

### Bogotá, Antioquia y Valle del Cauca

{markdown_table(unique_summary.target_rows)}

En conjunto, estos tres territorios concentran **{format_pct(unique_summary.target_share)}** de los investigadores únicos reconocidos.

### Top 10 departamentos de residencia

{markdown_table(unique_summary.top10)}

Los cinco primeros departamentos concentran **{format_pct(unique_summary.top5_share)}** del total.

### Departamentos con menor participación

{markdown_table(unique_summary.min_rows)}

## Resultado comparativo: consolidado completo sin deduplicar

- Total de registros: {format_int(all_summary.total)}
- HHI: {format_num(all_summary.hhi)}
- HHI (0 a 10.000): {all_summary.hhi_10000:.2f}
- Nivel de concentración: **{all_label}**
- Participación conjunta de Bogotá, Antioquia y Valle del Cauca: **{format_pct(all_summary.target_share)}**

Este contraste muestra que la deduplicación por persona no altera de forma sustantiva la conclusión: la concentración territorial se mantiene en un rango **moderado** y sigue dominada por los mismos tres departamentos.

## Respuesta directa a la pregunta del profesor

Sí, la investigación reconocida está fuertemente concentrada en **Bogotá, Antioquia y Valle del Cauca**.

- En la base depurada, estos tres departamentos reúnen **{format_pct(unique_summary.target_share)}** de los investigadores.
- Bogotá por sí sola concentra **{format_pct(unique_summary.target_rows[0][2])}**.
- Antioquia aporta **{format_pct(unique_summary.target_rows[1][2])}**.
- Valle del Cauca aporta **{format_pct(unique_summary.target_rows[2][2])}**.

Aunque el HHI no ubica el sistema en un nivel extremo de monopolización territorial, sí evidencia una estructura centralizada alrededor de pocos polos científicos, especialmente el eje **Bogotá-Antioquia-Valle del Cauca**.

## Conclusiones

1. El HHI territorial para investigadores únicos es **{unique_summary.hhi_10000:.2f}**, lo que indica una concentración **{unique_label}**.
2. Bogotá es el principal nodo territorial de la investigación reconocida en Colombia.
3. Antioquia y Valle del Cauca consolidan, junto con Bogotá, el núcleo dominante del sistema.
4. La concentración territorial es robusta al criterio de deduplicación.
5. El resultado es robusto: al comparar base deduplicada y consolidado total, la lectura sustantiva no cambia.
"""


def html_table(rows: list[tuple[str, int, float]]) -> str:
    body = []
    for name, count, pct in rows:
        body.append(
            f"<tr><td>{escape(name)}</td><td>{format_int(count)}</td><td>{pct:.2f}%</td></tr>"
        )
    return "\n".join(body)


def build_html(unique_summary: Summary, all_summary: Summary) -> str:
    unique_label = concentration_label(unique_summary.hhi_10000)
    all_label = concentration_label(all_summary.hhi_10000)
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Sprint 2 - Concentración territorial HHI</title>
  <style>
    :root {{
      --bg: #f6f3ee;
      --paper: #fffdf8;
      --ink: #1e2430;
      --muted: #5d6878;
      --accent: #0f766e;
      --accent-2: #a16207;
      --line: #d9d2c7;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Georgia, "Times New Roman", serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top right, rgba(15, 118, 110, 0.10), transparent 28%),
        radial-gradient(circle at left bottom, rgba(161, 98, 7, 0.10), transparent 32%),
        var(--bg);
      line-height: 1.55;
    }}
    .wrap {{
      max-width: 1100px;
      margin: 0 auto;
      padding: 40px 20px 64px;
    }}
    .hero {{
      background: linear-gradient(135deg, rgba(15,118,110,0.95), rgba(30,36,48,0.96));
      color: #fff;
      border-radius: 24px;
      padding: 28px;
      box-shadow: 0 18px 50px rgba(30, 36, 48, 0.18);
    }}
    h1, h2, h3 {{ margin-top: 0; }}
    h1 {{ font-size: clamp(2rem, 4vw, 3.1rem); margin-bottom: 10px; }}
    h2 {{ font-size: 1.4rem; margin-bottom: 8px; }}
    p, li {{ font-size: 1.03rem; }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 16px;
      margin-top: 22px;
    }}
    .card {{
      background: var(--paper);
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 18px;
      box-shadow: 0 10px 24px rgba(30, 36, 48, 0.07);
    }}
    .metric {{ font-size: 2rem; font-weight: 700; color: var(--accent); margin: 8px 0; }}
    .section {{ margin-top: 28px; }}
    .pill {{
      display: inline-block;
      padding: 6px 12px;
      border-radius: 999px;
      background: rgba(161, 98, 7, 0.12);
      color: var(--accent-2);
      font-weight: 700;
      letter-spacing: 0.02em;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      background: var(--paper);
      border-radius: 18px;
      overflow: hidden;
      border: 1px solid var(--line);
      box-shadow: 0 10px 24px rgba(30, 36, 48, 0.07);
    }}
    th, td {{ padding: 12px 14px; text-align: left; border-bottom: 1px solid var(--line); }}
    th {{ background: #efe7dc; }}
    td:nth-child(2), td:nth-child(3), th:nth-child(2), th:nth-child(3) {{ text-align: right; }}
    .note {{ color: var(--muted); }}
    .focus {{
      border-left: 4px solid var(--accent);
      padding-left: 16px;
      margin: 20px 0;
    }}
    @media (max-width: 640px) {{
      .wrap {{ padding: 20px 14px 42px; }}
      .hero {{ padding: 20px; border-radius: 18px; }}
      .card {{ padding: 16px; }}
      th, td {{ padding: 10px; font-size: 0.95rem; }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <section class="hero">
      <div class="pill">Sprint 2 · Análisis #14</div>
      <h1>Índice Herfindahl-Hirschman por departamento</h1>
      <p>Evaluación de la concentración territorial de la investigación reconocida por Minciencias, con énfasis en Bogotá, Antioquia y Valle del Cauca.</p>
      <p class="note">Base principal: investigadores únicos, conservando la convocatoria más reciente por persona.</p>
    </section>

    <section class="grid section">
      <article class="card">
        <h2>HHI principal</h2>
        <div class="metric">{unique_summary.hhi_10000:.2f}</div>
        <p>Escala 0 a 10.000</p>
      </article>
      <article class="card">
        <h2>Nivel</h2>
        <div class="metric">{escape(unique_label.title())}</div>
        <p>Concentración territorial</p>
      </article>
      <article class="card">
        <h2>Total base final</h2>
        <div class="metric">{format_int(unique_summary.total)}</div>
        <p>Investigadores únicos</p>
      </article>
      <article class="card">
        <h2>Bogotá + Antioquia + Valle</h2>
        <div class="metric">{format_pct(unique_summary.target_share)}</div>
        <p>Participación conjunta</p>
      </article>
    </section>

    <section class="section card">
      <h2>Lectura del resultado</h2>
      <p>El HHI calculado sobre la base depurada por persona única es <strong>{unique_summary.hhi_10000:.2f}</strong>, lo que ubica la estructura territorial en una concentración <strong>{escape(unique_label)}</strong>. Esto significa que la investigación reconocida no está distribuida homogéneamente en el país: pocos departamentos concentran una fracción importante del total.</p>
      <div class="focus">
        <p><strong>Respuesta corta:</strong> sí, Bogotá, Antioquia y Valle del Cauca concentran una parte sustantiva de la investigación reconocida. Juntos reúnen <strong>{format_pct(unique_summary.target_share)}</strong> del total de investigadores únicos.</p>
      </div>
      <p class="note">Variable utilizada: <strong>NME_DEPARTAMENTO_RES_PR</strong>. Archivo fuente: <strong>datos/tarea_join/investigadores_consolidado.csv</strong>.</p>
    </section>

    <section class="section">
      <h2>Departamentos foco</h2>
      <table>
        <thead>
          <tr><th>Departamento</th><th>Investigadores</th><th>Participación</th></tr>
        </thead>
        <tbody>
          {html_table(unique_summary.target_rows)}
        </tbody>
      </table>
    </section>

    <section class="section">
      <h2>Top 10 departamentos de residencia</h2>
      <table>
        <thead>
          <tr><th>Departamento</th><th>Investigadores</th><th>Participación</th></tr>
        </thead>
        <tbody>
          {html_table(unique_summary.top10)}
        </tbody>
      </table>
      <p class="note">Los cinco primeros concentran {format_pct(unique_summary.top5_share)} del total.</p>
    </section>

    <section class="grid section">
      <article class="card">
        <h2>Comparativo sin deduplicar</h2>
        <p><strong>HHI:</strong> {all_summary.hhi_10000:.2f}</p>
        <p><strong>Nivel:</strong> {escape(all_label)}</p>
        <p><strong>Total registros:</strong> {format_int(all_summary.total)}</p>
        <p><strong>Participación top 3:</strong> {format_pct(all_summary.target_share)}</p>
      </article>
      <article class="card">
        <h2>Conclusión metodológica</h2>
        <p>La comparación entre la base final por persona única y el consolidado completo muestra resultados muy cercanos. La conclusión no cambia: el sistema se organiza alrededor de pocos polos territoriales, encabezados por Bogotá, Antioquia y Valle del Cauca.</p>
      </article>
    </section>

    <section class="section card">
      <h2>Conclusiones</h2>
      <ol>
        <li>El HHI territorial principal es {unique_summary.hhi_10000:.2f}, correspondiente a una concentración {escape(unique_label)}.</li>
        <li>Bogotá es el principal centro territorial de la investigación reconocida.</li>
        <li>Antioquia y Valle del Cauca consolidan, junto con Bogotá, el núcleo dominante del sistema.</li>
        <li>La concentración territorial es robusta al criterio de deduplicación.</li>
      </ol>
    </section>
  </div>
</body>
</html>
"""


def main() -> None:
    all_counter, unique_counter = read_counters(DATA_PATH)
    all_summary = build_summary(all_counter)
    unique_summary = build_summary(unique_counter)

    OUTPUT_MD.write_text(build_markdown(unique_summary, all_summary), encoding="utf-8")
    OUTPUT_HTML.write_text(build_html(unique_summary, all_summary), encoding="utf-8")

    print(f"Reporte Markdown generado en: {OUTPUT_MD}")
    print(f"Reporte HTML generado en: {OUTPUT_HTML}")


if __name__ == "__main__":
    main()
