#!/usr/bin/env python3
"""NovusMundus · Evernote Rich Clipboard Sync

Converts the executive Daily Journaling HTML into native macOS RTF
and loads it into the system clipboard. When you switch to Evernote
and press Cmd+V, it pastes fully formatted with styled badges,
colored headings, and executive checkmarks.
"""

import subprocess
import sys
from pathlib import Path

HTML_CONTENT = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    color: #1e293b;
    line-height: 1.6;
    font-size: 14px;
  }
  h1 { color: #0f172a; font-size: 22px; border-bottom: 2px solid #e2e8f0; padding-bottom: 6px; margin-bottom: 12px; }
  h2 { color: #d97706; font-size: 18px; margin-top: 20px; margin-bottom: 6px; }
  h3 { font-size: 15px; margin-top: 14px; margin-bottom: 4px; }
  .badge-box {
    background-color: #f1f5f9;
    border-left: 4px solid #6366f1;
    padding: 10px 14px;
    margin-bottom: 16px;
    border-radius: 4px;
    font-size: 13px;
    color: #334155;
  }
  .quote-box {
    background-color: #f8fafc;
    border-left: 4px solid #3b82f6;
    padding: 8px 12px;
    margin: 8px 0;
    font-style: italic;
    color: #1e3a8a;
  }
  .task-done { color: #16a34a; font-weight: bold; }
  .task-pending { color: #ea580c; font-weight: bold; }
  ul, ol { margin-top: 4px; margin-bottom: 8px; padding-left: 20px; }
  li { margin-bottom: 4px; }
</style>
</head>
<body>

<h1>📅 Daily Journaling · NovusMundus Executive Edition</h1>

<div class="badge-box">
  <div><b>🏢 Empresa:</b> NovusMundus · Novus Capital</div>
  <div><b>📅 Fecha:</b> 29 de Octubre de 2026</div>
  <div><b>👑 Autor:</b> Mikel Irastorza (<i>Presidente, Fundador &amp; Propietario Supremo</i>)</div>
  <div><b>💼 Enlace Ejecutivo:</b> Chatty (<i>Chief Executive Officer - CEO</i>)</div>
  <div><b>⚡ Lema:</b> <i>"Build your personal growth &amp; lead the technological renaissance with NovusMundus"</i></div>
</div>

<h2>☀️ AM (Morning Intention &amp; Strategic Focus)</h2>
<p style="color: #64748b; font-size: 12px; font-style: italic; margin-top: 0;">Fill this section first thing in the morning to set yourself up for success!</p>

<h3 style="color: #dc2626;">🎯 Goals (Objetivos de Alto Impacto)</h3>
<p style="color: #64748b; font-size: 12px; margin-top: 0;">What are the top things you want to achieve today?</p>
<ul>
  <li><span class="task-done">[✓]</span> <b>Arquitectura Supabase Cloud &amp; RLS:</b> Desplegar y validar las 8 tablas ACID con Row-Level Security en producción (<code>RoomTudy+ | Novus Brother Tech</code>, ID: <code>oxrcgvhthygodjhiible</code>).</li>
  <li><span class="task-done">[✓]</span> <b>Pipeline Streaming Kafka &amp; PySpark:</b> Consolidar procesamiento en tiempo real de 25,000 transacciones y 265 alertas activas de fraude.</li>
  <li><span class="task-done">[✓]</span> <b>Gobierno de Agentes IA &amp; Chatty CEO:</b> Supervisar directivas ejecutivas delegadas al C-Suite (CISO Aegis, CTO Turing, CFO Ledger, CMO Mercury, VP Data Orion).</li>
  <li><span class="task-pending">[ ]</span> <b>Optimización FinOps 137 €:</b> Ajustar consumo elástico de workers y cuotas cloud para maximizar margen operativo de Novus Capital.</li>
</ul>

<h3 style="color: #16a34a;">💚 Feelings (Estado Emocional, Claridad y Soporte)</h3>
<p style="color: #64748b; font-size: 12px; margin-top: 0;">How do you want to feel today? What kind of support do you need from others?</p>
<div class="quote-box" style="border-left-color: #22c55e; background-color: #f0fdf4; color: #14532d;">
  <p style="margin: 0 0 6px 0;"><b>Estado interior:</b> Hoy me siento con máxima determinación, serenidad estratégica y visión clara. Plena confianza en la solidez del sistema que estamos consolidando.</p>
  <p style="margin: 0;"><b>Soporte ejecutivo:</b> Delegación total en Chatty (CEO) para ejecutar la orquestación de agentes con rigor suizo, permitiéndome liderar desde el Nivel 0 como Propietario Supremo.</p>
</div>

<h3 style="color: #ea580c;">🌟 Expectations &amp; Vision (Qué espero del día)</h3>
<p style="color: #64748b; font-size: 12px; margin-top: 0;">What are you looking forward to most today?</p>
<div class="quote-box" style="border-left-color: #f59e0b; background-color: #fffbeb; color: #78350f;">
  <p style="margin: 0;">La sincronización bidireccional impecable entre el Lakehouse local y Supabase Cloud sin pérdidas ni latencia. Ver a NovusMundus operar con la elegancia y potencia de una empresa de primer nivel mundial.</p>
</div>

<hr style="border: 0; border-top: 1px solid #cbd5e1; margin: 24px 0 16px 0;">

<h2 style="color: #4f46e5;">🌙 PM (Evening Review &amp; Executive Closure)</h2>
<p style="color: #64748b; font-size: 12px; font-style: italic; margin-top: 0;">Fill this section at the end of the day to celebrate wins, reflect and recharge!</p>

<h3 style="color: #0284c7;">🏆 Wins (Grandes Victorias de Hoy)</h3>
<ul>
  <li><b>Clean Code &amp; Calidad Absoluta:</b> 27/27 tests unitarios y de integración pasando al 100%, con Ruff linter, Ruff formatter y Mypy en estado impecable.</li>
  <li><b>Base de Datos Dual (ACID + Cloud):</b> SQLite WAL local ultra-rápido sincronizado con DDL PostgreSQL 15+ y políticas RLS activas en Supabase.</li>
  <li><b>Centro de Mando Visual:</b> Visualizador interactivo de red y pipeline funcionando en tiempo real para monitorizar el ecosistema empresarial.</li>
</ul>

<h3 style="color: #9333ea;">🙏 Gratitude (Gratitud Diaria)</h3>
<ol>
  <li><b>Por la visión:</b> Por la lucidez de concebir infraestructuras que resuelven problemas de gran escala.</li>
  <li><b>Por el equipo digital:</b> Por contar con Chatty (CEO) como mano derecha infatigable y alineada con la cultura de NovusMundus.</li>
  <li><b>Por la ejecución:</b> Por cada línea de código que convierte la ambición en una realidad tangible y reutilizable.</li>
</ol>

<h3 style="color: #0d9488;">💡 Learnings &amp; Tomorrow's Focus (Aprendizajes y Foco de Mañana)</h3>
<div class="quote-box" style="border-left-color: #14b8a6; background-color: #f0fdfa; color: #134e4a;">
  <p style="margin: 0 0 6px 0;"><b>Aprendizaje:</b> La simplicidad arquitectónica vence a cualquier artificio. Cuando los contratos de datos y las responsabilidades entre capas están claramente definidos, escalar es trivial.</p>
  <p style="margin: 0;"><b>Foco de mañana:</b> Escalar los conectores de RoomTudy+ y afianzar la orquestación continua de datos con el pipeline Dielsa.</p>
</div>

</body>
</html>
"""


def main():
    print("📋 NovusMundus · Copiando Daily Journaling al portapapeles de macOS...")
    # Convert HTML to RTF via textutil
    process = subprocess.Popen(
        ["textutil", "-stdin", "-format", "html", "-convert", "rtf", "-stdout"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    rtf_data, err = process.communicate(input=HTML_CONTENT.encode("utf-8"))
    if process.returncode != 0:
        print(f"❌ Error en textutil: {err.decode('utf-8')}", file=sys.stderr)
        return 1

    temp_rtf = Path("/tmp/novus_daily_journal.rtf")
    temp_rtf.write_bytes(rtf_data)

    # Use AppleScript to set rich clipboard
    applescript = f'''
    set the clipboard to (read (POSIX file "{temp_rtf}") as «class RTF »)
    '''
    res = subprocess.run(["osascript", "-e", applescript], capture_output=True, text=True)
    if res.returncode == 0:
        print("✅ ¡Éxito! El contenido con formato enriquecido está en tu portapapeles (Cmd+V).")
        print("👉 Ve a tu nota de Evernote y presiona Cmd + V para pegarlo con estilo impecable.")
        return 0
    else:
        print(f"⚠️ Aviso en AppleScript: {res.stderr}", file=sys.stderr)
        # Fallback to plain text
        subprocess.run(["pbcopy"], input=HTML_CONTENT, text=True)
        print("Copiado en modo texto alternativo.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
