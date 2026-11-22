# Mikel Irastorza — Engineering & Scientific Research Portfolio
### Lead Systems Architect & Research Engineer · España

[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.24440204-10b981.svg?style=for-the-badge)](https://doi.org/10.5281/zenodo.24440204)
[![Research Repository](https://img.shields.io/badge/NovusLattice-Official%20Repo-f59e0b.svg?style=for-the-badge&logo=github)](https://github.com/novomundus2-cmyk/NovusLattice)
[![Interactive Paper](https://img.shields.io/badge/Paper-Live%20Interactive%20Web-3b82f6.svg?style=for-the-badge)](https://novomundus2-cmyk.github.io/NovusLattice/)

---

## 📄 Publicación Científica Principal / Main Scientific Paper

### **NovusLattice: Potencial Empírico de Sutton-Chen en Espacios de Sobolev $H^1(\Omega)$, Metrología de Redes FCC y Mecánica de Medios Continuos Multiescala**
*Autor: **Mikel Irastorza** · Entidad: **Mikel Irastorza** · País: **España** · Año: **2026***

> **Abstract**: Presentamos un marco matemático riguroso que cierra la brecha multiescala entre los potenciales atómicos de muchos cuerpos y la mecánica de medios continuos elastoplásticos. Formulado sobre el potencial de Sutton-Chen para redes cúbicas centradas en las caras (FCC, grupo espacial $Fm\bar{3}m$), demostramos la existencia de minimizadores en espacios de Sobolev $H^1(\Omega)$ y establecemos puentes asintóticos hacia el tensor de tensiones de Cauchy mediante la regla de Cauchy-Born, con validación experimental en nanoestructuras tetraédricas $\text{Au}_{20}$ y metrología industrial ($\pm 0.2\text{ mm}$).

### Descarga Directa de los Papers Académicos (PDF Oficial)

| Idioma / Language | Formato | Documento Oficial |
| :--- | :---: | :--- |
| **Español (ES)** | PDF | [NovusLattice_Paper_ES_Mikel_Irastorza.pdf](NovusLattice_Paper_ES_Mikel_Irastorza.pdf) |
| **English (EN)** | PDF | [NovusLattice_Paper_EN_Mikel_Irastorza.pdf](NovusLattice_Paper_EN_Mikel_Irastorza.pdf) |
| **Français (FR)** | PDF | [NovusLattice_Paper_FR_Mikel_Irastorza.pdf](NovusLattice_Paper_FR_Mikel_Irastorza.pdf) |

### Versión Web Interactiva (Monolingüe 1:1)
- 🌐 [Lectura Interactiva en Español](https://novomundus2-cmyk.github.io/NovusLattice/novuslattice_paper_es.html)
- 🌐 [Interactive Reading in English](https://novomundus2-cmyk.github.io/NovusLattice/novuslattice_paper_en.html)
- 🌐 [Lecture Interactive en Français](https://novomundus2-cmyk.github.io/NovusLattice/novuslattice_paper_fr.html)

---

## 📐 Formulación Matemática Unificada

El funcional variacional de energía de NovusLattice minimiza la densidad de energía de deformación atómica sobre el dominio continuo $\Omega$:

$$\mathbf{E}_{\text{NL}} = \arg\min_{\mathbf{u} \in H^1(\Omega)} \int_\Omega \mathcal{W}_{\text{SC}}(\nabla \mathbf{u}, a) \, d\Omega$$

Donde la energía potencial cohesiva total $U_{\text{total}}$ está regida por la suma de repulsión electrostática de pares y la densidad electrónica de muchos cuerpos (Sutton & Chen 1990):

$$U_{\text{total}} = \varepsilon \sum_i \left[ \frac{1}{2} \sum_{j \neq i} \left( \frac{a}{r_{ij}} \right)^n - c \sqrt{\rho_i} \right], \quad \rho_i = \sum_{j \neq i} \left( \frac{a}{r_{ij}} \right)^m$$

Para oro puro ($\text{Au}$): $n = 10$, $m = 8$, $\varepsilon = 1.2793 \times 10^{-2}\text{ eV}$, $c = 34.408$, $a = 4.08\text{ \AA}$.

---

## 🏛️ Cómo Citar / How to Cite

```bibtex
@article{irastorza2026novuslattice,
  author    = {Irastorza, Mikel},
  title     = {NovusLattice: Sutton-Chen Empirical Potential in Sobolev $H^1(\Omega)$ Spaces, FCC Lattice Metrology, and Multiscale Continuum Mechanics},
  year      = {2026},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.24440204},
  url       = {https://doi.org/10.5281/zenodo.24440204}
}
```

---

## 🛠️ Ecosistema de Ingeniería y Código

- **Repositorio Científico Dedicado**: [github.com/novomundus2-cmyk/NovusLattice](https://github.com/novomundus2-cmyk/NovusLattice) (código de simulación, tests unitarios, benchmarks y fuentes LaTeX).
- **Arquitectura de Datos y Métricas**: Motores de procesamiento continuo, esquemas idempotentes de Lakehouse y computación de alto rendimiento.

---
**Contacto y Autoría**: Mikel Irastorza · España · [GitHub Profile](https://github.com/novomundus2-cmyk)
