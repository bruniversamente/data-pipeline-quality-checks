"""Build portfolio-ready outputs for the data pipeline case study."""

from __future__ import annotations

import json
import math
import subprocess
import sys
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data_pipeline.duckdb"
OUTPUTS = ROOT / "outputs"
DASHBOARD = ROOT / "dashboard"
SQL_FILES = [
    ROOT / "sql" / "01_load_raw_tables.sql",
    ROOT / "sql" / "02_create_staging_tables.sql",
    ROOT / "sql" / "03_data_quality_checks.sql",
    ROOT / "sql" / "04_create_marts.sql",
]


def run_generator() -> None:
    subprocess.run([sys.executable, str(ROOT / "scripts" / "generate_raw_data.py")], check=True)


def run_sql_file(connection: duckdb.DuckDBPyConnection, sql_file: Path) -> None:
    sql = sql_file.read_text(encoding="utf-8")
    for statement in [part.strip() for part in sql.split(";") if part.strip()]:
        connection.execute(statement)


def export_csv(connection: duckdb.DuckDBPyConnection, query: str, filename: str):
    df = connection.execute(query).fetchdf()
    df.to_csv(OUTPUTS / filename, index=False)
    return df


def money(value: float) -> str:
    if value is None:
        return "n/a"
    try:
        if math.isnan(float(value)):
            return "n/a"
    except (TypeError, ValueError):
        return "n/a"
    return f"${value:,.0f}"


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def write_dashboard_variants(html: str) -> None:
    replacements = [
        ('<html lang="pt-BR">', '<html lang="en">'),
        ("Dashboard de Qualidade do Pipeline", "Data Pipeline Quality Dashboard"),
        (
            "Pipeline de pedidos e pagamentos com gates de validação, registros em quarentena e marts prontos para BI.",
            "Order-to-payment pipeline with validation gates, quarantined records and BI-ready marts.",
        ),
        ("falhas críticas encontradas; publicar apenas os marts Ready.", "critical failures found; publish only Ready marts."),
        ("Sem falhas críticas e score acima do limite.", "No critical failures and score above threshold."),
        ("Pedidos brutos", "Raw orders"),
        ("registros carregados", "input records loaded"),
        ("Pedidos prontos", "Ready orders"),
        ("seguros para marts de BI", "safe for BI marts"),
        ("Pedidos em revisão", "Review orders"),
        ("retidos pelas checagens", "quarantined by checks"),
        ("Falhas críticas", "Critical failures"),
        ("regras bloqueantes", "blocking rule hits"),
        ("meta de 98,0%", "98.0% target"),
        ("Regras com falha", "Failed rules"),
        ("Regra", "Rule"),
        ("Severidade", "Severity"),
        ("Registros com falha", "Failed records"),
        ("Taxa de prontidão por sistema", "Ready rate by source system"),
        ("Receita pronta para BI", "BI-ready revenue"),
        ("Pedidos que exigem revisão", "Orders requiring review"),
        ("Pedido", "Order"),
        ("Origem", "Source"),
        ("Capturado", "Captured"),
        ("Resumo do problema", "Issue summary"),
        (
            "Gerado a partir dos outputs em DuckDB. Falhas críticas bloqueiam a atualização executiva de BI até correção ou aprovação formal pelo responsável pelos dados.",
            "Generated from DuckDB outputs. Critical failures block executive BI refresh until fixed or formally approved by the data owner.",
        ),
    ]
    en_html = html
    for source, target in replacements:
        en_html = en_html.replace(source, target)

    (DASHBOARD / "data_pipeline_quality_dashboard_pt-BR.html").write_text(html, encoding="utf-8")
    (DASHBOARD / "data_pipeline_quality_dashboard_en.html").write_text(en_html, encoding="utf-8")
    (DASHBOARD / "data_pipeline_quality_dashboard.html").write_text(en_html, encoding="utf-8")


def build_dashboard(data: dict) -> str:
    rule_rows = "\n".join(
        f"""
        <tr>
          <td>{row['rule_name']}</td>
          <td><span class="badge {row['severity'].lower()}">{row['severity']}</span></td>
          <td>{row['failed_records']}</td>
        </tr>
        """
        for row in data["failed_rules"]
    )
    review_rows = "\n".join(
        f"""
        <tr>
          <td>{row['order_id']}</td>
          <td>{row['source_system']}</td>
          <td>{row['order_status']}</td>
          <td>{money(row['order_total'] or 0)}</td>
          <td>{money(row['captured_payment_amount'] or 0)}</td>
          <td>{row['issue_summary']}</td>
        </tr>
        """
        for row in data["review_records"][:10]
    )
    source_bars = "\n".join(
        f"""
        <div class="bar-row">
          <div class="bar-label">{row['source_system']}</div>
          <div class="bar-track"><span style="width: {row['ready_rate'] * 100:.1f}%"></span></div>
          <div class="bar-value">{pct(row['ready_rate'])}</div>
        </div>
        """
        for row in data["source_quality"]
    )
    revenue_bars = "\n".join(
        f"""
        <div class="revenue-row">
          <span>{row['source_system']}</span>
          <strong>{money(row['order_total'])}</strong>
        </div>
        """
        for row in data["revenue_ready"]
    )
    status_class = "blocked" if data["publication_status"] == "Blocked" else "approved"

    return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Dashboard de Qualidade do Pipeline</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #111827;
      --muted: #667085;
      --line: #d7dce3;
      --paper: #f7f8fa;
      --panel: #ffffff;
      --critical: #b42318;
      --warn: #b54708;
      --good: #027a48;
      --blue: #175cd3;
      --teal: #0f766e;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--paper);
      color: var(--ink);
      font-family: Inter, Segoe UI, Arial, sans-serif;
    }}
    main {{
      width: min(1180px, calc(100vw - 32px));
      margin: 0 auto;
      padding: 28px 0 40px;
    }}
    header {{
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 20px;
      align-items: end;
      border-bottom: 1px solid var(--line);
      padding-bottom: 18px;
      margin-bottom: 18px;
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: clamp(1.7rem, 3vw, 2.8rem);
      line-height: 1.03;
      letter-spacing: 0;
    }}
    p {{ margin: 0; color: var(--muted); line-height: 1.5; }}
    .status {{
      min-width: 230px;
      border: 1px solid var(--line);
      background: var(--panel);
      padding: 16px;
      border-radius: 8px;
    }}
    .status span {{
      display: inline-flex;
      font-weight: 800;
      padding: 6px 10px;
      border-radius: 999px;
      margin-bottom: 10px;
    }}
    .status .blocked {{ color: #fff; background: var(--critical); }}
    .status .approved {{ color: #fff; background: var(--good); }}
    .kpis {{
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 12px;
      margin-bottom: 18px;
    }}
    .tile, section {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
    }}
    .tile {{ padding: 15px; min-height: 112px; }}
    .tile .label {{ color: var(--muted); font-size: .82rem; font-weight: 700; }}
    .tile .value {{ font-size: 2rem; font-weight: 850; margin: 10px 0 6px; }}
    .tile .note {{ color: var(--muted); font-size: .84rem; }}
    .grid {{
      display: grid;
      grid-template-columns: 1.1fr .9fr;
      gap: 14px;
      margin-bottom: 14px;
    }}
    section {{ padding: 16px; overflow: hidden; }}
    h2 {{ margin: 0 0 12px; font-size: 1rem; letter-spacing: 0; }}
    table {{ width: 100%; border-collapse: collapse; font-size: .88rem; }}
    th, td {{ padding: 10px 8px; border-bottom: 1px solid #edf0f3; text-align: left; vertical-align: top; }}
    th {{ color: var(--muted); font-size: .76rem; text-transform: uppercase; }}
    .badge {{ display: inline-flex; border-radius: 999px; padding: 4px 8px; font-weight: 800; font-size: .72rem; }}
    .critical {{ color: var(--critical); background: #fef3f2; }}
    .warning {{ color: var(--warn); background: #fffaeb; }}
    .bar-row {{ display: grid; grid-template-columns: 96px 1fr 56px; gap: 10px; align-items: center; margin: 13px 0; }}
    .bar-label, .bar-value, .revenue-row span {{ color: var(--muted); font-size: .86rem; }}
    .bar-track {{ height: 12px; border-radius: 999px; background: #e7eaee; overflow: hidden; }}
    .bar-track span {{ display: block; height: 100%; background: var(--teal); }}
    .revenue-row {{ display: flex; justify-content: space-between; gap: 16px; padding: 11px 0; border-bottom: 1px solid #edf0f3; }}
    .footnote {{ margin-top: 14px; color: var(--muted); font-size: .78rem; }}
    @media (max-width: 900px) {{
      header, .grid {{ grid-template-columns: 1fr; }}
      .kpis {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    }}
    @media (max-width: 560px) {{
      main {{ width: min(100vw - 20px, 1180px); padding-top: 16px; }}
      .kpis {{ grid-template-columns: 1fr; }}
      section {{ overflow-x: auto; }}
      table {{ min-width: 720px; }}
      .bar-row {{ grid-template-columns: 82px 1fr 52px; }}
    }}
  </style>
</head>
<body>
<main>
  <header>
    <div>
      <h1>Data Pipeline Quality Dashboard</h1>
      <p>Pipeline de pedidos e pagamentos com gates de validação, registros em quarentena e marts prontos para BI.</p>
    </div>
    <div class="status">
      <span class="{status_class}">{data['publication_status']}</span>
      <p>{data['publication_reason']}</p>
    </div>
  </header>

  <div class="kpis">
    <div class="tile"><div class="label">Pedidos brutos</div><div class="value">{data['kpis']['raw_orders']}</div><div class="note">registros carregados</div></div>
    <div class="tile"><div class="label">Pedidos prontos</div><div class="value">{data['kpis']['ready_orders']}</div><div class="note">seguros para marts de BI</div></div>
    <div class="tile"><div class="label">Pedidos em revisão</div><div class="value">{data['kpis']['review_orders']}</div><div class="note">retidos pelas checagens</div></div>
    <div class="tile"><div class="label">Falhas críticas</div><div class="value">{data['kpis']['critical_failures']}</div><div class="note">regras bloqueantes</div></div>
    <div class="tile"><div class="label">Quality score</div><div class="value">{pct(data['kpis']['quality_score'])}</div><div class="note">meta de 98,0%</div></div>
  </div>

  <div class="grid">
    <section>
      <h2>Regras com falha</h2>
      <table>
        <thead><tr><th>Regra</th><th>Severidade</th><th>Registros com falha</th></tr></thead>
        <tbody>{rule_rows}</tbody>
      </table>
    </section>
    <section>
      <h2>Taxa de prontidão por sistema</h2>
      {source_bars}
      <h2 style="margin-top: 22px;">Receita pronta para BI</h2>
      {revenue_bars}
    </section>
  </div>

  <section>
    <h2>Pedidos que exigem revisão</h2>
    <table>
      <thead><tr><th>Pedido</th><th>Origem</th><th>Status</th><th>Total</th><th>Capturado</th><th>Resumo do problema</th></tr></thead>
      <tbody>{review_rows}</tbody>
    </table>
    <p class="footnote">Gerado a partir dos outputs em DuckDB. Falhas críticas bloqueiam a atualização executiva de BI até correção ou aprovação formal pelo responsável pelos dados.</p>
  </section>
</main>
</body>
</html>
"""


def main() -> None:
    run_generator()
    OUTPUTS.mkdir(exist_ok=True)
    DASHBOARD.mkdir(exist_ok=True)

    if DB_PATH.exists():
        DB_PATH.unlink()

    con = duckdb.connect(str(DB_PATH))
    try:
        for sql_file in SQL_FILES:
            run_sql_file(con, sql_file)

        dq_summary = export_csv(
            con,
            """
            SELECT severity, COUNT(*) AS rules_checked,
                   SUM(failed_records) AS total_failed_records,
                   SUM(CASE WHEN failed_records > 0 THEN 1 ELSE 0 END) AS failed_rules
            FROM dq_summary
            GROUP BY severity
            ORDER BY severity
            """,
            "dq_summary.csv",
        )
        failed_rules = export_csv(
            con,
            """
            SELECT rule_name, severity, failed_records
            FROM dq_summary
            WHERE failed_records > 0
            ORDER BY CASE severity WHEN 'Critical' THEN 1 WHEN 'Warning' THEN 2 ELSE 3 END,
                     failed_records DESC,
                     rule_name
            """,
            "failed_rules.csv",
        )
        quality_score = export_csv(
            con,
            """
            WITH totals AS (SELECT COUNT(*) AS total_orders FROM mart_orders),
            critical AS (
                SELECT SUM(failed_records) AS critical_failures
                FROM dq_summary
                WHERE severity = 'Critical'
            )
            SELECT total_orders,
                   COALESCE(critical_failures, 0) AS critical_failures,
                   ROUND(1 - COALESCE(critical_failures, 0) / NULLIF(total_orders, 0), 4) AS quality_score
            FROM totals CROSS JOIN critical
            """,
            "quality_score.csv",
        )
        orders_by_status = export_csv(
            con,
            """
            SELECT data_quality_status, COUNT(*) AS orders
            FROM mart_orders
            GROUP BY data_quality_status
            ORDER BY orders DESC
            """,
            "orders_by_quality_status.csv",
        )
        source_quality = export_csv(
            con,
            """
            SELECT source_system,
                   COUNT(*) AS orders,
                   SUM(CASE WHEN data_quality_status = 'Ready' THEN 1 ELSE 0 END) AS ready_orders,
                   ROUND(SUM(CASE WHEN data_quality_status = 'Ready' THEN 1 ELSE 0 END)::DOUBLE / COUNT(*), 4) AS ready_rate
            FROM mart_orders
            GROUP BY source_system
            ORDER BY ready_rate DESC, orders DESC
            """,
            "source_system_quality.csv",
        )
        revenue_ready = export_csv(
            con,
            """
            SELECT source_system,
                   COUNT(*) AS completed_orders,
                   ROUND(SUM(order_total), 2) AS order_total,
                   ROUND(SUM(captured_payment_amount), 2) AS captured_payment_amount
            FROM mart_orders
            WHERE order_status = 'Completed'
              AND data_quality_status = 'Ready'
            GROUP BY source_system
            ORDER BY order_total DESC
            """,
            "revenue_ready_orders.csv",
        )
        category_metrics = export_csv(
            con,
            """
            SELECT category,
                   COUNT(DISTINCT order_id) AS orders,
                   SUM(quantity) AS units,
                   ROUND(SUM(net_item_amount), 2) AS net_revenue,
                   ROUND(SUM(gross_margin), 2) AS gross_margin
            FROM mart_order_items
            WHERE order_status = 'Completed'
              AND has_product_issue = FALSE
              AND has_quantity_issue = FALSE
            GROUP BY category
            ORDER BY net_revenue DESC
            """,
            "category_metrics.csv",
        )
        review_records = export_csv(
            con,
            """
            SELECT order_id, order_date, customer_id, order_status, source_system,
                   order_total, captured_payment_amount,
                   CONCAT_WS(', ',
                     CASE WHEN has_customer_issue THEN 'missing customer' END,
                     CASE WHEN has_date_issue THEN 'invalid date' END,
                     CASE WHEN has_missing_payment_issue THEN 'missing payment' END,
                     CASE WHEN has_product_reference_issue THEN 'missing product' END,
                     CASE WHEN has_item_quantity_issue THEN 'invalid item quantity' END,
                     CASE WHEN has_payment_mismatch_issue THEN 'payment mismatch' END
                   ) AS issue_summary
            FROM mart_orders
            WHERE data_quality_status = 'Review'
            ORDER BY order_id
            """,
            "records_requiring_review.csv",
        )
        export_csv(con, "SELECT * FROM mart_orders ORDER BY order_id LIMIT 50", "mart_orders_preview.csv")
        export_csv(con, "SELECT * FROM mart_order_items ORDER BY order_item_id LIMIT 50", "mart_order_items_preview.csv")

        total_orders = int(quality_score.iloc[0]["total_orders"])
        critical_failures = int(quality_score.iloc[0]["critical_failures"])
        score = float(quality_score.iloc[0]["quality_score"])
        ready_orders = int(orders_by_status.loc[orders_by_status["data_quality_status"] == "Ready", "orders"].sum())
        review_orders = int(orders_by_status.loc[orders_by_status["data_quality_status"] == "Review", "orders"].sum())
        warning_failures = int(dq_summary.loc[dq_summary["severity"] == "Warning", "total_failed_records"].sum())
        publication_status = "Blocked" if critical_failures > 0 or score < 0.98 else "Approved"
        publication_reason = (
            f"{critical_failures} falhas críticas encontradas; publicar apenas os marts Ready."
            if publication_status == "Blocked"
            else "Sem falhas críticas e score acima do limite."
        )

        data = {
            "publication_status": publication_status,
            "publication_reason": publication_reason,
            "kpis": {
                "raw_orders": total_orders,
                "ready_orders": ready_orders,
                "review_orders": review_orders,
                "critical_failures": critical_failures,
                "warning_failures": warning_failures,
                "quality_score": score,
            },
            "failed_rules": failed_rules.to_dict(orient="records"),
            "source_quality": source_quality.to_dict(orient="records"),
            "revenue_ready": revenue_ready.to_dict(orient="records"),
            "review_records": review_records.to_dict(orient="records"),
            "category_metrics": category_metrics.to_dict(orient="records"),
        }

        (OUTPUTS / "dashboard_data.json").write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
        write_dashboard_variants(build_dashboard(data))
        executive_findings_en = "\n".join(
            [
                "# Executive findings - Data Pipeline Quality",
                "",
                f"- Publication status: **{publication_status}**.",
                f"- Quality score: **{pct(score)}** against a 98.0% target.",
                f"- Ready orders: **{ready_orders}**; review orders: **{review_orders}**.",
                f"- Critical failing records: **{critical_failures}**; warning failing records: **{warning_failures}**.",
                f"- Largest BI-ready revenue source: **{revenue_ready.iloc[0]['source_system']}** with **{money(float(revenue_ready.iloc[0]['order_total']))}**.",
                "- Recommendation: publish only Ready marts and route Review records to data owners before executive reporting.",
            ]
        )
        executive_findings_pt = "\n".join(
            [
                "# Achados executivos - Data Pipeline Quality",
                "",
                f"- Status de publicação: **{publication_status}**.",
                f"- Quality score: **{pct(score)}** contra uma meta de 98,0%.",
                f"- Pedidos prontos: **{ready_orders}**; pedidos em revisão: **{review_orders}**.",
                f"- Registros com falha crítica: **{critical_failures}**; registros com warning: **{warning_failures}**.",
                f"- Maior fonte de receita pronta para BI: **{revenue_ready.iloc[0]['source_system']}** com **{money(float(revenue_ready.iloc[0]['order_total']))}**.",
                "- Recomendação: publicar apenas os marts Ready e direcionar registros em Review aos responsáveis pelos dados antes do reporte executivo.",
            ]
        )
        (OUTPUTS / "executive_findings.md").write_text(executive_findings_en, encoding="utf-8")
        (OUTPUTS / "executive_findings.pt-BR.md").write_text(executive_findings_pt, encoding="utf-8")
    finally:
        con.close()

    print(f"Outputs written to {OUTPUTS}")
    print(f"Dashboard written to {DASHBOARD / 'data_pipeline_quality_dashboard.html'}")


if __name__ == "__main__":
    main()
