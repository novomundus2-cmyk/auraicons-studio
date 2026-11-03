# Ecosistema de Agentes EKC (ElektriKubercisC)
> **Creador, Fundador & Propietario Supremo**: Mikel Irastorza (EFA)  
> **Significado de EKC**: **ElektriKubercisC** (Kubernetes, C POSIX, Eléctrico, Oro Industrial y Código Determinista)  
> **Total de Agentes con Base de Datos Dedicada**: 16

---

## Estructura de Agentes y Bases de Datos Bíblicas

| Directorio | Nombre Bíblico | Rol Operativo | Base de Datos SQLite | Tabla de Dominio |
| :--- | :--- | :--- | :--- | :--- |
| `EKC - Jesús el Nazareno` | **Jesús el Nazareno** | CEO Supremo & Orquestador General | `jesus_el_nazareno.db` | `cluster_orchestration_directives` |
| `EKC - San Miguel Arcángel` | **San Miguel Arcángel** | Guardián Supremo Anti-Hacking & Ciberseguridad Defensiva | `san_miguel_arcangel.db` | `zero_trust_threat_radar` |
| `EKC - Hiram` | **Hiram** | Arquitecto de Producto, Ergonomía & Experiencia de Usuario (UX) | `hiram.db` | `ux_design_tokens` |
| `EKC - Aholiab` | **Aholiab** | Maestro Artesano de Frontend UI, React & Accesibilidad WCAG | `aholiab.db` | `ui_component_registry` |
| `EKC - Miguelín` | **Miguelín** | Sistema Visual, Acabados Metálicos Oro & CSS Artesanal | `miguelin.db` | `visual_gold_palette` |
| `EKC - Bezalel` | **Bezalel** | Maestro de Metales, Mecanizado CNC & Tolerancias CAD | `bezalel.db` | `cad_tolerances_mechanical` |
| `EKC - Daniel` | **Daniel** | Arquitecto Backend, Motores Distribuidos & Servidores | `daniel.db` | `posix_microservices` |
| `EKC - Josué` | **Josué** | Conquistador de Datos, Cloud SQL, BigQuery & Databricks | `josue.db` | `cloud_sql_migrations` |
| `EKC - Natán` | **Natán** | Auditor Crítico, Verificación Adversarial Independiente & QA | `natan.db` | `adversarial_test_suites` |
| `EKC - David` | **David** | Estratega de Métricas, Algoritmos Financieros & PnL | `david.db` | `welford_streaming_aggregations` |
| `EKC - Esdras` | **Esdras** | Escriba Mayor, Catalogación Semántica & Bóvedas de Código | `esdras.db` | `clean_code_patterns` |
| `EKC - Nehemías` | **Nehemías** | Reconstructor de Murallas, DevOps, Kubernetes (K8s) & CI/CD | `nehemias.db` | `kubernetes_pod_manifests` |
| `EKC - Caleb` | **Caleb** | Explorador Valiente, Scouting Tecnológico & Benchmarks | `caleb.db` | `hardware_apple_silicon_metrics` |
| `EKC - José` | **José** | Administrador de Recursos, FinOps & Almacenamiento Eficiente | `jose.db` | `finops_energy_ledgers` |
| `EKC - Lucas` | **Lucas** | Médico de Sistemas, Telemetría, Logs & Salud Operativa | `lucas.db` | `system_vital_diagnostics` |
| `EKC - Gamaliel` | **Gamaliel** | Doctor de la Ley, Gobernanza Formal & Reglas Firestore | `gamaliel.db` | `cel_security_rules` |

---

## Invariantes de Gobernanza
1. Cada agente cuenta con una carpeta física rotulada `EKC - [Nombre Bíblico]`.
2. Cada agente dispone de su propia base de datos SQLite aislada en modo `WAL` (`journal_mode=WAL`), con claves foráneas activadas y sellado criptográfico SHA-256 en cada evento.
3. El presidente y propietario supremo es **Mikel Irastorza (EFA)**, quien mantiene la autoridad irrenunciable y la decisión final sobre cualquier mutación a producción.
4. **San Miguel Arcángel (CISO Aegis)** protege todo el perímetro contra ataques cibernéticos e inyecciones.
