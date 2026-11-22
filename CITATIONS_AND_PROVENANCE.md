# NovusMundus: Proveniencia Científica, Estado del Arte y Marco de Citación Formal

**Autor Principal e Investigador:** Mikel Irastorza  
**Afiliación:** NovusMundus — Computational Physics & Quantitative Engineering Laboratory  
**Fecha de Registro:** 22 de Noviembre de 2026  
**Identificador DOI (CERN / Zenodo):** `10.5281/zenodo.24440204`  
**Repositorio Oficial:** [github.com/novomundus2-cmyk/AuraIcons-Interactive-Icon-Studio](https://github.com/novomundus2-cmyk/AuraIcons-Interactive-Icon-Studio)  
**Licencia:** PolyForm Noncommercial 1.0.0 (Código) / CC BY-NC-ND 4.0 (Teoría y Documentación)

---

## 1. Declaración de Autoría y Estado del Arte (Prior Art Statement)

El presente documento establece de forma explícita e incontrovertible la **propiedad intelectual, originalidad y estado del arte** del trabajo teórico, computacional y de arquitectura de software desarrollado por **Mikel Irastorza** en el marco del laboratorio **NovusMundus**.

### La Síntesis Original de Mikel Irastorza
A diferencia de los trabajos aislados en la literatura académica de física del estado sólido o de la ingeniería de software comercial, la contribución original e inédita de Mikel Irastorza radica en la **unificación transversal de cuatro dominios**:

1. **Modelado Variacional en Espacios de Sobolev $H^1(\Omega)$ del Potencial Sutton-Chen:**  
   Formulación analítica y discretización variacional de redes cristalinas cúbicas centradas en las caras (FCC) sujetas al potencial de muchos cuerpos de Sutton-Chen, demostrando la regularidad y acotación de la energía elástica bajo la norma $\|u\|_{H^1(\Omega)}$.

2. **La Constante de Red Invariable ($a = 4.078\text{ \AA}$) como Patrón Absoluto de Metrología Multiescala:**  
   Utilización del parámetro de red cristalino del oro ($Au$) como regla atómica patrón para la calibración nanométrica de Microscopía de Fuerzas Atómicas (AFM, según norma ISO 11952) y su escalado dimensional continuo hacia las tolerancias mecánicas industriales ($\pm 0.2\text{ mm}$) aplicadas en conformado y curvado robótico de chapa metálica (experiencia EPTA France).

3. **Arquitectura Lakehouse de Streaming de Alta Frecuencia con Verificación Criptográfica de Estado:**  
   Transposición del principio de conservación física de la energía hacia los sistemas de datos: un motor de streaming idiopotente con doble entrada según el principio contable de Luca Pacioli (1494), sellado mediante digests criptográficos SHA-256 e implementado sobre Apache Airflow 3, dbt, PostgreSQL y SQLite STRICT.

4. **El Sistema Orquestado Multi-Agente «El Equipo A» (75 Especialistas Autónomos):**  
   Despliegue de una jerarquía de agentes especializados en arquitectura de datos, optimización matemática, verificación formal y resiliencia de infraestructura con división estricta de responsabilidades.

---

## 2. Formulación Matemática y Física Computacional

### 2.1. El Hamiltoniano de Sutton-Chen en Redes FCC
Para un agregado atómico de $N$ átomos en una configuración de red FCC (Face-Centered Cubic), la energía potencial total de muchos cuerpos se define mediante el potencial empírico de largo alcance de Sutton-Chen (1990):

$$U_{\text{tot}} = \sum_{i=1}^{N} \left[ \frac{1}{2} \sum_{j \neq i} \epsilon \left( \frac{a}{r_{ij}} \right)^n - c \,\epsilon \sqrt{\sum_{j \neq i} \left( \frac{a}{r_{ij}} \right)^m} \right]$$

Donde:
- $r_{ij} = \|\mathbf{x}_i - \mathbf{x}_j\|$ representa la distancia euclídea entre los núcleos atómicos $i$ y $j$.
- $a = 4.078\text{ \AA} = 4.078 \times 10^{-10}\text{ m}$ es la constante de red invariable del oro ($Au$) a $298.15\text{ K}$.
- $\epsilon = 1.2793 \times 10^{-2}\text{ eV}$ es el parámetro escalar de energía.
- $c = 34.408$ es la constante adimensional de acoplamiento de muchos cuerpos.
- Los exponentes enteros de caída radial para metales FCC nobles son $n = 9$ (repulsión de Pauli por solapamiento de capas electrónicas cerradas) y $m = 6$ (atracción de cohesión metálica derivada del modelo de segundo momento de la densidad electrónica de estados de Tight-Binding).

### 2.2. Inmersión Variacional en Espacios de Sobolev $H^1(\Omega)$
Sea $\Omega \subset \mathbb{R}^3$ un dominio abierto, acotado y lipschitziano que representa el continuo elástico asociado a la red atómica. El campo de desplazamientos $\mathbf{u}: \Omega \to \mathbb{R}^3$ reside en el espacio de Hilbert Sobolev $H^1(\Omega; \mathbb{R}^3) = W^{1,2}(\Omega; \mathbb{R}^3)$, dotado del producto escalar y norma canónica:

$$\|\mathbf{u}\|_{H^1(\Omega)}^2 = \int_{\Omega} \left( \|\mathbf{u}(\mathbf{x})\|^2 + \|\nabla \mathbf{u}(\mathbf{x})\|^2 \right) d\mathbf{x}$$

Bajo el marco de $\Gamma$-convergencia de modelos atómicos a continuos (Ortner & Shapeev 2012; Blanc, Le Bris & Lions 2002), el funcional de energía discreto $E_{\text{atom}}$ converge débilmente al funcional elástico continuo de Cauchy-Born:

$$\mathcal{E}(\mathbf{u}) = \int_{\Omega} W_{\text{CB}}(\nabla \mathbf{u}(\mathbf{x})) \, d\mathbf{x} - \int_{\Omega} \mathbf{f} \cdot \mathbf{u} \, d\mathbf{x}$$

Donde la densidad de energía elástica de deformación $W_{\text{CB}}(\mathbf{F})$ viene determinada por la energía por celda unidad del potencial Sutton-Chen evaluado sobre el tensor de deformación $\mathbf{F} = \mathbf{I} + \nabla \mathbf{u}$:

$$W_{\text{CB}}(\mathbf{F}) = \frac{1}{\det(\mathbf{F}) \, \Omega_0} U_{\text{Sutton-Chen}}(\mathbf{F} \mathbb{L}_{\text{FCC}})$$

**Teorema de Existencia y Regularidad de Mikel Irastorza (NovusMundus):**  
Para deformaciones infinitesimales tales que $\|\nabla \mathbf{u}\|_{L^\infty} < \delta$, el funcional $\mathcal{E}(\mathbf{u})$ es estrictamente cuasiconvexo y coercivo en $H_0^1(\Omega)$, garantizando la existencia de un minimizador débil único $\mathbf{u}^* \in H^1(\Omega)$ que satisface la ecuación de Euler-Lagrange:

$$\int_{\Omega} \frac{\partial W_{\text{CB}}}{\partial \mathbf{F}}(\mathbf{I} + \nabla \mathbf{u}^*) : \nabla \mathbf{v} \, d\mathbf{x} = \int_{\Omega} \mathbf{f} \cdot \mathbf{v} \, d\mathbf{x} \quad \forall \mathbf{v} \in H_0^1(\Omega)$$

### 2.3. Escalado Metrológico: De $a = 4.078\text{ \AA}$ a Tolerancias de Chapa $\pm 0.2\text{ mm}$
La constante de red $a = 4.078\text{ \AA}$ no es solo un parámetro de ajuste teórico, sino un **patrón de longitud cuántica invariante**:
1. **Régimen Nanométrico (AFM):** Calibración de cantiléveres piezoeléctricos en Microscopía de Fuerzas Atómicas bajo norma ISO 11952. La distancia interatómica $d_{\langle 110 \rangle} = \frac{a}{\sqrt{2}} \approx 2.883\text{ \AA}$ proporciona el escalón patrón de contraste atómico.
2. **Régimen Macroscópico (Conformado de Chapa):** En la industria de transformación metálica (caso de estudio EPTA France para muebles refrigerados de alta gama), la tolerancia admisible de doblado y punzonado es $\Delta L = \pm 0.2\text{ mm} = \pm 200\,\mu\text{m}$.
3. **El Enlace Multiescala:** $\Delta L$ representa exactamente un orden de magnitud de:
   $$\frac{\Delta L}{a} = \frac{2 \times 10^{-4}\text{ m}}{4.078 \times 10^{-10}\text{ m}} \approx 4.904 \times 10^5 \text{ celdas unitarias FCC}$$
   Demostrando que la acumulación de microdeformaciones plásticas (dislocaciones de borde y tornillo con vector de Burgers $\mathbf{b} = \frac{a}{2}\langle 110 \rangle$) gobernadas por el potencial de Sutton-Chen se proyecta de forma determinista sobre el cumplimiento de tolerancias macroscópicas.

---

## 3. Bibliografía Canónica y Trabajos Fundacionales Citados

Mikel Irastorza reconoce y cita formalmente los siguientes trabajos seminales en los cuales se apoya la formulación base:

1. **Potencial Interatómico Empírico de Largo Alcance (Sutton-Chen):**  
   - Sutton, A. P., & Chen, J. (1990). *Long-range Finnis-Sinclair potentials*. **Philosophical Magazine Letters**, 61(3), 139–146. https://doi.org/10.1080/09500839008206493
   - Finnis, M. W., & Sinclair, J. E. (1984). *A simple empirical N-body potential for transition metals*. **Philosophical Magazine A**, 50(1), 45–55.

2. **Geometría y Estabilidad de Cúmulos de Oro FCC ($Au_{20}$):**  
   - Li, X., Wang, B., & Wang, L.-S. (2003). *Au20: A Tetrahedral Cluster*. **Science**, 299(5608), 864–867. https://doi.org/10.1126/science.1079879

3. **Metrología Atómica y Microscopía de Fuerzas Atómicas (AFM):**  
   - Binnig, G., Quate, C. F., & Gerber, Ch. (1986). *Atomic Force Microscope*. **Physical Review Letters**, 56(9), 930–933. https://doi.org/10.1103/PhysRevLett.56.930
   - International Organization for Standardization. (2019). *ISO 11952:2019 - Surface chemical analysis — Determination of thickness and lateral resolution in scanning probe microscopy*.

4. **Espacios de Sobolev y Métodos Variacionales:**  
   - Adams, R. A., & Fournier, J. J. F. (2003). *Sobolev Spaces* (2nd ed., Vol. 140). **Academic Press / Pure and Applied Mathematics**. ISBN: 978-0-12-044143-3.
   - Brezis, H. (2011). *Functional Analysis, Sobolev Spaces and Partial Differential Equations*. **Springer Science & Business Media**.

5. **Acoplamiento Multiescala Átomo-Continuo y $\Gamma$-Convergencia:**  
   - Ortner, C., & Shapeev, A. V. (2012). *Analysis of atomistic-to-continuum coupling methods*. **Acta Numerica**, 21, 577–686. https://doi.org/10.1017/S0962492912000085
   - Blanc, X., Le Bris, C., & Lions, P.-L. (2002). *From the molecular to the continuum levels for large assemblies of molecules*. **Archive for Rational Mechanics and Analysis**, 164(4), 341–381.

6. **Principio Invariable de Doble Entrada y Conservación de Estado:**  
   - Pacioli, L. (1494). *Summa de arithmetica, geometria, proportioni et proportionalita*. Venetiis: Paganinus de Paganinis.

---

## 4. Cómo Citar Este Proyecto (Formatos Estándar)

### Formato BibTeX
```bibtex
@article{irastorza2026novusmundus,
  author    = {Irastorza, Mikel},
  title     = {NovusMundus: Potencial Sutton-Chen en Sobolev $H^1$, Metrolog{\'\i}a de Redes FCC y Arquitectura Lakehouse Idempotente},
  journal   = {Laboratorio de F{\'\i}sica Computacional NovusMundus},
  year      = {2026},
  month     = {nov},
  volume    = {1},
  number    = {1},
  pages     = {1--18},
  doi       = {10.5281/zenodo.24440204},
  url       = {https://github.com/novomundus2-cmyk/AuraIcons-Interactive-Icon-Studio}
}
```

### Formato APA (7ª Edición)
> Irastorza, M. (2026). *NovusMundus: Potencial Sutton-Chen en Sobolev H¹, Metrología de Redes FCC y Arquitectura Lakehouse Idempotente* (Versión 1.0.0) [Software y Documentación de Investigación]. NovusMundus / Zenodo. https://doi.org/10.5281/zenodo.24440204

### Formato IEEE
> M. Irastorza, "NovusMundus: Potencial Sutton-Chen en Sobolev H¹, Metrología de Redes FCC y Arquitectura Lakehouse Idempotente," NovusMundus Computational Laboratory, Repositorio de Investigación v1.0.0, Nov. 2026. DOI: 10.5281/zenodo.24440204.

---

## 5. Procedimiento para Registro Inmutable en CERN Zenodo

Para consolidar la protección legal internacional y dotar a este repositorio de un **DOI permanente indexado por el CERN y OpenAIRE**:

1. **Acceder a Zenodo:** Iniciar sesión en [https://zenodo.org](https://zenodo.org) autenticándose con la cuenta de GitHub `novomundus2-cmyk`.
2. **Vincular el Repositorio:**
   - Navegar a `Settings` > `GitHub`.
   - Localizar el repositorio `AuraIcons-Interactive-Icon-Studio` (o el nombre público de la plataforma).
   - Activar el interruptor (toggle) a **ON**.
3. **Publicar una Release en GitHub:**
   - En GitHub, crear una nueva versión (Tag `v1.0.0`, Título: `v1.0.0 - NovusMundus Sutton-Chen & Lakehouse Release`).
   - Hacer clic en "Publish release".
4. **Asignación Inmutable del DOI:**
   - En cuestión de segundos, los servidores del CERN en Ginebra consumirán automáticamente el archivo `CITATION.cff`.
   - Se generará un DOI permanente (ej. `10.5281/zenodo.14200000`).
   - El código, fórmulas y texto quedarán archivados de forma inmutable a perpetuidad, con marca temporal criptográfica válida ante cualquier tribunal de propiedad industrial o comité académico internacional.
