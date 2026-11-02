import re

md_path = "CV/DOSSIER_NOTEBOOKLM_MIKEL.md"
html_path = "CV/DOSSIER_NOTEBOOKLM_MIKEL.html"

with open(md_path, encoding="utf-8") as f:
    text = f.read()

header = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>Dossier Maestro MIKEL · NOVUSMUNDUS - Gemini Notebook</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js" onload="renderMathInElement(document.body);"></script>
<style>
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    line-height: 1.6;
    color: #1e293b;
    max-width: 900px;
    margin: 40px auto;
    padding: 0 20px;
  }
  h1, h2, h3, h4 { color: #0f172a; }
  h1 { border-bottom: 2px solid #0284c7; padding-bottom: 8px; font-size: 26px; }
  h2 { border-bottom: 1px solid #cbd5e1; padding-bottom: 6px; margin-top: 30px; font-size: 20px; }
  h3 { margin-top: 24px; color: #0369a1; font-size: 16px; }
  pre { background: #0f172a; color: #f8fafc; border: 1px solid #334155; border-radius: 8px; padding: 16px; overflow-x: auto; font-family: monospace; font-size: 13px; line-height: 1.4; }
  code { font-family: monospace; background: #f1f5f9; padding: 2px 6px; border-radius: 4px; font-size: 13px; }
  hr { border: 0; border-top: 1px solid #e2e8f0; margin: 30px 0; }
  li { margin-bottom: 6px; }
  .banner { background: #e0f2fe; border: 1.5px solid #38bdf8; border-radius: 12px; padding: 14px 18px; margin-bottom: 28px; font-size: 14px; }
  @media print {
    body { max-width: 100%; margin: 0; padding: 15px; }
    .banner { display: none; }
    @page { margin: 15mm; }
  }
</style>
</head>
<body>
<div class="banner">
  💡 <strong>Documento listo para Gemini Notebook (NotebookLM):</strong> Puedes descargarlo con 1 clic en PDF o Markdown para subirlo a <strong>Gemini Notebook</strong> y que te genere mapas conceptuales, presentaciones, resúmenes y podcasts:
  <div style="margin-top: 12px; display: flex; gap: 10px; flex-wrap: wrap;">
    <a href="/dossier.pdf" download style="background: #0284c7; color: white; padding: 8px 16px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 13px;">📥 Descargar PDF Directo</a>
    <a href="/dossier.md" download style="background: #0f172a; color: white; padding: 8px 16px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 13px;">📄 Descargar Markdown (.md)</a>
    <a href="/notebooks.zip" download style="background: #7c3aed; color: white; padding: 8px 16px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 13px;">📦 Descargar Cuadernos (.zip)</a>
    <button onclick="window.print()" style="background: #059669; color: white; border: none; padding: 8px 16px; border-radius: 8px; cursor: pointer; font-weight: bold; font-size: 13px;">🖨️ Imprimir / Guardar PDF</button>
  </div>
</div>
"""

lines = text.split("\n")
in_code = False
html_lines = []

for line in lines:
    if line.startswith("```"):
        if not in_code:
            html_lines.append("<pre>")
            in_code = True
        else:
            html_lines.append("</pre>")
            in_code = False
        continue
    if in_code:
        clean_code = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        html_lines.append(clean_code)
        continue

    if line.startswith("# "):
        html_lines.append(f"<h1>{line[2:]}</h1>")
    elif line.startswith("## "):
        html_lines.append(f"<h2>{line[3:]}</h2>")
    elif line.startswith("### "):
        html_lines.append(f"<h3>{line[4:]}</h3>")
    elif line.startswith("#### "):
        html_lines.append(f"<h4>{line[5:]}</h4>")
    elif line.strip() == "---":
        html_lines.append("<hr>")
    elif line.startswith(("* ", "- ")):
        html_lines.append(f"<li>{line[2:]}</li>")
    elif re.match(r"^\d+\.\s", line.strip()):
        html_lines.append(f"<li>{line.strip()}</li>")
    elif line.strip() == "":
        html_lines.append("<br>")
    else:
        html_lines.append(f"<p>{line}</p>")

body = "\n".join(html_lines)
body = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", body)
body = re.sub(r"`(.*?)`", r"<code>\1</code>", body)

full_html = header + body + "\n</body>\n</html>"

with open(html_path, "w", encoding="utf-8") as f:
    f.write(full_html)

print("HTML generado con éxito en:", html_path)
