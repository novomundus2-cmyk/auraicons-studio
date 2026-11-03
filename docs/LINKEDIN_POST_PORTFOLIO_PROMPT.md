# 🚀 Kit de Difusión LinkedIn · Mikel Irastorza
**Autor:** Mikel Irastorza (Lead Software Engineer & Systems Architect)  
**Tema:** Contrastando "Vanity Badges" (sellos de vanidad B2B) vs. Ingeniería Real, Clean Code y Demostrabilidad en Producción.

---

## 📋 1. Texto Definitivo Listo para Publicar (Copiar y Pegar)

```text
Navegando por páginas de agencias de desarrollo como hashtrust.in, es habitual encontrar la misma postal: una cuadrícula con más de 10 medallas y sellos de "Top Software Development Company" emitidos por directorios B2B.

La realidad detrás de esos sellos la conocemos casi todos en la industria:
No hay una auditoría técnica detrás.
No hay inspección de código ni de arquitectura.
No hay revisión de concurrencia, ni pruebas de estrés, ni contratos de datos.

En la gran mayoría de casos, son "vanity badges" (sellos de vanidad) que se obtienen rellenando un formulario o a cambio de un enlace en el pie de página para arañar puntos de SEO.

Siempre he creído que en la ingeniería de software la credibilidad no se compra con un diploma en PNG: se demuestra en el terminal y en producción.

Para quienes aún no me conozcáis por aquí, soy Mikel Irastorza.
Me defino como Lead Software Engineer, constructor de sistemas ("Project-First Builder") y un pythonista apasionado del Clean Code, el tipado estricto y la verificabilidad matemática.

Mi rigor técnico nació en la precisión física industrial (operando células robóticas de conformado de chapa con tolerancias de ±0.2 mm en EPTA France). Hoy aplico exactamente esa misma aversión al error a la arquitectura de software:

• Motores concurrentes de streaming y contabilidad formal Pacioli (consistencia ACID de doble entrada).
• 58 tests automatizados ejecutados en CI/CD verificando leyes monoidales O(1) y ausencia de deadlocks.
• Microservicios y telemetría en tiempo real a 60 FPS con WebSockets y Canvas sin dependencias innecesarias.

En lugar de coleccionar sellos estáticos, he preferido volcar toda esta arquitectura en un entorno interactivo y público, donde cualquiera puede auditar el código, probar el bot cuantitativo y comprobar cómo responde el sistema en milisegundos:

🌐 Portfolio interactivo & Simulación:
👉 https://auraicons-studio.vercel.app/portfolio

📄 CV de Ingeniería & Repositorios de GitHub:
👉 https://auraicons-studio.vercel.app/cv

Menos diplomas de plástico y más código probado en producción.

¿Qué opináis vosotros: siguen teniendo algún peso real este tipo de sellos a la hora de evaluar la competencia técnica de un equipo o candidato?

#SoftwareEngineering #Python #CleanCode #DataEngineering #SystemsArchitecture #TechLeadership #BuildInPublic
```

---

## 🖼️ 2. Imagen Recomendada para Adjuntar
Sube una de estas dos opciones junto al post:
1. **Captura de `hashtrust.in`**: Muestra la cuadrícula de sellos (AppFutura, UpFirms, etc.). Detiene el scroll en LinkedIn porque despierta curiosidad inmediata.
2. **Captura de tu Terminal con los Tests**: El resultado de `pytest: 58 passed in 92.45s` en color verde, que refuerza visualmente la frase *"muéstrame el terminal"*.

---

## 🤖 3. El Prompt Maestro (Para usar en un chat nuevo o con cualquier IA)

Si en el futuro quieres abrir un chat nuevo con cualquier modelo (ChatGPT, Claude, Gemini) y generar publicaciones, respuestas a comentarios o artículos con tu misma voz y rigor, copia y pega este **prompt de sistema**:

```text
Actúa como Mikel Irastorza, Lead Software Engineer & Systems Architect especializado en backend distribuido, concurrencia, motores de streaming de baja latencia y Python Clean Code.

Mi perfil técnico clave:
1. Origen y disciplina: Vengo de la precisión industrial física (operación de células robóticas de conformado de chapa y planos CAD con tolerancias de ±0.2 mm en EPTA France). Traslado esa misma aversión al error a la consistencia de memoria, contratos de datos deterministas y cero tolerancia al código descuidado.
2. Enfoque: "Project-First Builder". No hablo de teoría que no pueda demostrar. Todo mi CV está respaldado por 58 tests automatizados en verde (Pacioli ACID double-entry ledger con SHA-256, monoide de streaming O(1), enjambre de agentes IA, Lakehouse SQLite/Parquet ZSTD).
3. Producción real:
   - Portfolio interactivo: https://auraicons-studio.vercel.app/portfolio
   - CV Oficial: https://auraicons-studio.vercel.app/cv
   - Trading Bot cuantitativo en vivo: https://auraicons-studio.vercel.app/bot
   - Cockpit Big Data: https://auraicons-studio.vercel.app/cockpit
4. Tono de comunicación: Directo, técnico, sobrio, sin clichés corporativos vacíos ni arrogancia. Pasión por el Clean Code, la elegancia pythonista y la verificabilidad matemática (Show, Don't Tell).

Usa este contexto para redactar contenido técnico, responder preguntas en LinkedIn o defender decisiones de arquitectura de alto nivel.
```

---

## 💬 4. Respuestas Preparadas para los Comentarios en LinkedIn

### Si alguien comenta: *"Totalmente de acuerdo, esos sellos son puro marketing..."*
> Exacto. En agencias de bajo coste son el gancho comercial para clientes no técnicos. Pero cuando hablas con un CTO o un Lead Architect, lo único que cuenta es si tus pipelines tienen contrapresión, si tu base de datos escala y si tus tests pasan en el pipeline de despliegue.

### Si alguien pregunta: *"¿Cómo implementas la consistencia Pacioli en Python?"*
> Mediante transacciones formales con bloqueos lexicográficos (`SELECT ... FOR UPDATE`), garantizando que cada céntimo que entra en el Debe tiene su contrapartida exacta en el Haber ($\sum Debe = \sum Haber$). Si la suma no cuadra a cero o si el hash SHA-256 no valida, la transacción aborta automáticamente. Tienes la implementación completa en el repo enlazado en mi CV.
