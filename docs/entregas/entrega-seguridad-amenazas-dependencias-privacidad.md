# Entrega Semana 13: Seguridad, Modelado de Amenazas, Análisis de Dependencias y Privacidad

**Proyecto:** VeriFacts — Sistema de Detección de Desinformación  
**Equipo:** Pedro Jose Castro Blanquicett, Cristian David Cardeno, Julian Samuel Cabeza Pena  
**Repositorio:** [https://github.com/ISCOUTB/AS_202620_Verifacts](https://github.com/ISCOUTB/AS_202620_Verifacts)  
**Fecha:** 2026-10-27  
**Estado:** Incremento local de Semana 13  
**Correspondencia arquitectónica:** arc42 [§8.11](../arc42/08-conceptos-transversales.md#811-privacidad-y-protección-de-datos-personales-s13), [§11](../arc42/11-riesgos-y-deuda-tecnica.md), [C4 Contenedores](../c4/02-contenedores.md) y [Aspecto A-12](../aspectos.md#matriz-de-trazabilidad).

---

## Resumen Ejecutivo

Esta entrega consolida la postura de seguridad y privacidad del sistema VeriFacts a través de tres componentes complementarios:

1. **Modelado y Tabla de Amenazas Priorizadas con Mitigación Asignada:** Identificación formal de amenazas utilizando la taxonomía **STRIDE** combinada con **OWASP Top 10 API Security Risks (2023)** sobre la superficie de ataque real del sistema (API FastAPI, motor de scraping Trafilatura, persistencia SQLite, frontend React y despliegue en servidor de laboratorio Dokploy). Cada amenaza cuenta con estimación cuantitativa de riesgo, mitigación táctica asignada y estado real en el código.
2. **Resultado del Análisis de Dependencias (SCA - Software Composition Analysis):** Auditoría exhaustiva de la cadena de suministro de software (*Supply Chain*) tanto en el ecosistema backend (Python 3.12 / pip) como frontend (Node.js / React / Vite), contrastando versiones fijadas frente a registros de vulnerabilidades y exposiciones comunes (CVE, GHSA, PyPA Advisory Database).
3. **Sección de Privacidad (*Privacy by Design*):** Formalización de las políticas, inventario de datos y garantías de protección de datos personales conforme al marco regulatorio aplicable (Ley Estatutaria 1581 de 2012 de Colombia, Habeas Data y principios RGPD), abordando los riesgos específicos de anonimato, retención limitada y derechos de supresión sobre el historial de análisis de noticias.

---

## 1. Modelado y Tabla de Amenazas Priorizadas con Mitigación Asignada

### 1.1 Superficie de Ataque y Diagrama de Flujo de Datos (DFD)

El sistema VeriFacts expone dos fronteras principales de interacción: la frontera cliente-API (tráfico HTTP público) y la frontera API-sitio web externo (scraping síncrono saliente). A continuación se representa el flujo de datos y los límites de confianza (*trust boundaries*):

```mermaid
flowchart TD
    subgraph TB_Public["Límite de Confianza Público (No Confiable)"]
        User["Usuario / Atacante en Navegador"]
        ExtWeb["Sitios Web Externos / Servidores de Terceros"]
    end

    subgraph TB_Edge["Límite Perimetral (Frontera de Red)"]
        Nginx["Nginx Reverse Proxy / Dokploy Router"]
    end

    subgraph TB_App["Límite de Confianza de la Aplicación (Contenedor VeriFacts)"]
        API["FastAPI Router (`app/api/routes.py`)"]
        ContentSvc["Content Service (`app/modules/content/`)"]
        AnalysisSvc["Analysis & Scoring Service (`app/modules/`)"]
        Observability["Observabilidad en Memoria (`observability.py`)"]
    end

    subgraph TB_Data["Límite de Datos Persistentes (Almacenamiento Local)"]
        DB[(Base de Datos SQLite `data/verifacts.db`)]
    end

    User -->|"1. HTTP POST /analysis (url o texto) [AM-02, AM-03]"| Nginx
    User -->|"2. HTTP GET /analysis, GET /analysis/{id} [AM-04]"| Nginx
    Nginx -->|"HTTP sin TLS en red interna [AM-05]"| API
    
    API -->|"Invoca extracción de URL"| ContentSvc
    ContentSvc -->|"3. HTTP GET saliente (Trafilatura) [AM-01: SSRF]"| ExtWeb
    ExtWeb -->>|"Respuesta HTML arbitraria / gigante [AM-02]"| ContentSvc

    ContentSvc -->|"Texto normalizado"| API
    API -->|"Texto a analizar"| AnalysisSvc
    AnalysisSvc -->|"Cálculo de señales y score determinista"| API
    
    API -->|"4. SQL INSERT parametrizado [AM-06]"| DB
    API -->|"5. Actualiza contadores en memoria"| Observability
    DB -->>|"Lectura de registros confirmados"| API
    API -->>|"200 OK con AnalysisResponse [AM-04]"| Nginx
    Nginx -->>|Respuesta HTTP al cliente| User
```

### 1.2 Metodología de Priorización del Riesgo

Para priorizar las amenazas se evalúa la **Probabilidad** y el **Impacto** en escala de 3 niveles:

$$\text{Nivel de Riesgo} = \text{Probabilidad} \times \text{Impacto}$$

* **Probabilidad:**
  * **Baja (1):** Requiere condiciones inusuales de red o accesos locales privilegiados.
  * **Media (2):** Explota un comportamiento natural de la API sin requerir privilegios previos.
  * **Alta (3):** Explotable de manera trivial mediante peticiones HTTP estándar sin barreras defensivas.
* **Impacto:**
  * **Bajo (1):** Afecta únicamente telemetría o estética sin comprometer integridad ni disponibilidad.
  * **Medio (2):** Causa degradación transitoria de rendimiento o exposición de datos no sensibles.
  * **Alto (3):** Pérdida de disponibilidad global del contenedor (DoS), fuga de datos personales o alcance de la red interna del servidor.

| Puntuación (PxI) | Nivel de Riesgo | Acción Arquitectónica |
|:---:|:---:|---|
| **6 - 9** | 🔴 **CRÍTICO / ALTO** | Mitigación mandatoria prioritaria; no debe postergarse. |
| **3 - 4** | 🟡 **MEDIO** | Mitigación programada en el ciclo actual o controles compensatorios. |
| **1 - 2** | 🟢 **BAJO** | Aceptación informada del riesgo o monitoreo pasivo. |

---

### 1.3 Tabla de Amenazas Priorizadas con Mitigación Asignada

> **Convención de Estado Real en el Código:**
> * **Implementado:** El control existe en el código base y cuenta con pruebas automatizadas que lo verifican.
> * **Parcial:** Existe un control genérico o preliminar, pero no satisface por completo la mitigación arquitectónica prevista.
> * **Diseñado / Pendiente:** La arquitectura documenta la solución técnica, pero no se ha incorporado en el código fuente.

| ID | Amenaza | Categoría STRIDE / OWASP | Activo / Componente C4 | Vector de Ataque | Prob. | Imp. | Riesgo | Mitigación Arquitectónica Asignada | Control Técnico y Ubicación | Estado Real en el Código |
|:---:|---|:---:|---|---|:---:|:---:|:---:|---|---|:---:|
| **AM-01** | **Server-Side Request Forgery (SSRF) en Ingesta de URL** *(MF-07)* | Tampering / Information Disclosure · *OWASP API8:2023 Lack of Protection from SSRF* | Componente `Content` (`extract_from_url`) / Sitio Externo | El atacante envía URLs que apuntan a interfaces locales o de red interna (`http://localhost:8000`, `http://127.0.0.1`, `http://172.17.0.1`, `http://169.254.169.254`). La API ejecuta la petición con los privilegios de red del contenedor Dokploy. | **Media (2)** | **Alto (3)** | 🔴 **ALTO (6)** | **Validación estricta de esquemas y lista de exclusión de IPs privadas:** Validar que el esquema sea exclusivamente `http` o `https`. Resolver DNS previo a la petición y rechazar rangos RFC 1918 (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), loopback (`127.0.0.0/8`), link-local (`169.254.0.0/16`) y resolución de nombres a nivel de contenedor. Desactivar seguimiento de redirecciones a hosts no validados. | Envoltorio en `app/modules/content/service.py` con validación de IP antes de invocar `trafilatura.fetch_url`. Respuesta `HTTP 422 Unprocessable Content` con mensaje *"Destino de URL no permitido"*. | **Pendiente** (identificado como MF-07 en [arc42 §11](../arc42/11-riesgos-y-deuda-tecnica.md)). Actualmente `trafilatura` recibe cualquier cadena que comience con http/https sin filtrado de IP interna. |
| **AM-02** | **Denegación de Servicio (DoS / ReDoS) por Carga Excesiva o Documento Gigante** *(MF-03)* | Denial of Service · *OWASP API4:2023 Unrestricted Resource Consumption* | Ingesta (`API` y `Content`) / Memoria del Contenedor | Envío de un cuerpo de texto masivo (> 10 MB) o scraping de una página con millones de caracteres que agota los 512 MB de RAM del contenedor o bloquea la CPU evaluando expresiones regulares de análisis lingüístico. | **Media (2)** | **Alto (3)** | 🔴 **ALTO (6)** | **Enforcement temprano de límites (Bounds Enforcement):** Validar longitud máxima en el esquema Pydantic (`max_length=50_000`) en `AnalysisRequest`. En scraping web, limitar el buffer de descarga HTTP a 2 MB y truncar el texto extraído a un máximo de 50.000 caracteres antes de normalizar y pasar al motor de reglas. | Restricción en `app/api/schemas.py` (`Field(max_length=50000)`) y en `app/modules/content/service.py`. Rechazo inmediato con `HTTP 413 Payload Too Large` ante textos mayores al tope. | **Pendiente** (registrado como MF-03). Actualmente ni `AnalysisRequest` ni `normalize_content` imponen longitud máxima. |
| **AM-03** | **Agotamiento de Conexiones por Timeouts Prolongados de Servidores Externos** *(MF-01)* | Denial of Service · *OWASP API4:2023 Unrestricted Resource Consumption* | Componente `Content` (`trafilatura`) / Worker ASGI | Un atacante envía múltiples URLs que apuntan a servidores controlados por él que mantienen la conexión abierta sin emitir bytes (*slowloris HTTP*), saturando los hilos o event loop de Uvicorn. | **Media (2)** | **Alto (3)** | 🔴 **ALTO (6)** | **Timeout estricto y desacoplamiento de I/O:** Configurar timeout estricto de conexión (2.000 ms) y de lectura (4.000 ms) en la biblioteca de scraping. Si el origen no responde en la ventana, cortar la conexión inmediatamente y responder con `HTTP 504 Gateway Timeout`. | Parámetro `timeout=4.0` explícito en la llamada de red y manejador de excepción en `app/modules/content/service.py`. | **Pendiente** (registrado como MF-01). Actualmente `fetch_url` no pasa timeout explícito y un error se traduce a 400 genérico. |
| **AM-04** | **Exposición y Fuga de Datos en Historial Global no Autenticado** *(MF-08)* | Information Disclosure · *OWASP API1:2023 Broken Object Level Authorization (BOLA)* | Contenedor "Base de Datos" / Endpoint `GET /analysis` | Cualquier usuario en internet puede iterar secuencialmente `GET /analysis/{id}` (IDs enteros 1, 2, 3...) o invocar `GET /analysis` y leer la totalidad de los textos y URLs analizados por otros usuarios, exponiendo contenido confidencial o PII. | **Alta (3)** | **Alto (3)** | 🔴 **CRÍTICO (9)** | **Minimización de exposición en catálogo y diseño de privacidad:** No retornar el campo `content` completo en la respuesta de listado `GET /analysis` (solo retornar resumen truncado o metadatos de score). En `GET /analysis/{id}`, sustituir identificadores enteros secuenciales por identificadores no predecibles (UUIDv4) o hash criptográfico. Política de retención automática que elimine registros con antigüedad superior a 30 días. | Modificación de `app/api/routes.py` y `app/persistence/repository.py`; creación de tarea periódica de limpieza de historial. | **Pendiente** (registrado como MF-08 y decisión [ADR-0011](../adr/0011-historial-registro-unico-sin-propietario.md)). Actualmente los IDs son autoincrementales y `content` se retorna completo a cualquiera sin autenticación. |
| **AM-05** | **Intercepción y Modificación de Tráfico en Tránsito (Man-in-the-Middle - MitM)** *(MF-09)* | Information Disclosure / Tampering · *OWASP API2:2023 Broken Authentication* | Frontera Perimetral / Servidor Laboratorio Dokploy | El despliegue de pruebas en el laboratorio utiliza dominio provisional `sslip.io` sin certificado TLS válido, transmitiendo peticiones en texto claro sobre HTTP (puerto 80). | **Alta (3)** | **Medio (2)** | 🔴 **ALTO (6)** | **Terminación TLS Obligatoria:** Habilitar certificado SSL/TLS automático mediante Let's Encrypt o ZeroSSL a través del Traefik/Dokploy router, forzando redirección permanente `HTTP 301 -> HTTPS` y cabeceras `Strict-Transport-Security` (HSTS). | Configuración en `deploy/compose.lab.yaml` y router Dokploy. | **Pendiente** (registrado como MF-09). En Render sí cuenta con TLS nativo gestionado; en el laboratorio Dokploy permanece sobre HTTP plano. |
| **AM-06** | **Inyección SQL en Capa de Persistencia** | Tampering / Information Disclosure · *OWASP API3:2023 Broken Object Property Level Authorization* | Componente `Persistence` (`repository.py`) / SQLite | Inyección de sintaxis SQL maliciosa en el cuerpo del contenido analizado (`"texto'); DROP TABLE analyses;--"`) para extraer o alterar datos. | **Baja (1)** | **Alto (3)** | 🟡 **MEDIO (3)** | **Consultas Parametrizadas y Separación de Código y Datos:** Toda interacción con SQLite se ejecuta mediante consultas con placeholders `?` en el motor de base de datos, imposibilitando que el texto de entrada altere el árbol de análisis sintáctico de la consulta. | `app/persistence/repository.py:108` (`INSERT INTO analyses (...) VALUES (?, ?, ?, ?, ?, ?)`). | **Implementado.** Verificado en código y validado en suite con textos conteniendo caracteres especiales y comillas (`tests/test_analysis.py`). |
| **AM-07** | **Inyección de Dependencias Vulnerables en la Cadena de Suministro** *(V-1)* | Elevation of Privilege / Tampering · *OWASP API6:2023 Server-Side Parameter Pollution* | Entorno de Ejecución / Paquetes de Terceros | Un paquete de terceros en `requirements.txt` o `package.json` presenta una vulnerabilidad crítica conocida (RCE, bypass de seguridad) explotable remotamente. | **Media (2)** | **Medio (2)** | 🟡 **MEDIO (4)** | **Escaneo Automatizado de Dependencias (SCA) y Pinned Dependencies:** Auditoría obligatoria en CI/CD con `pip-audit` y `npm audit`. Fijación de rangos seguros con versión mínima protegida. | Job automatizado en GitHub Actions `.github/workflows/tests.yml` y actualización periódica documentada. | **Parcial.** En S9 se detectó y corrigió PYSEC-2026-1845 subiendo a `pytest>=9.0.3,<10`. Se formaliza el escaneo integral en esta entrega (Sección 2). |
| **AM-08** | **Regresión Semántica o Modificación Inadvertida de Reglas de Detección** *(MF-06)* | Tampering / Repudiation | Componente `Analysis` & `Scoring` | Modificación no controlada de pesos, palabras clave o umbrales que altere las clasificaciones de desinformación sin justificación arquitectónica. | **Media (2)** | **Alto (3)** | 🔴 **ALTO (6)** | **Pruebas de Límites Bloqueantes en CI/CD:** Suite de pruebas de erosión de límites (`tests/test_boundaries.py`, `tests/test_scoring_boundaries.py`) que impiden integrar cambios a `master` si se modifican constantes semánticas sin actualizar el contrato. | CI bloqueante en GitHub Actions. | **Implementado.** Suite de 15 pruebas de límites activa y en verde. |

---

## 2. Resultado del Análisis de Dependencias (SCA)

### 2.1 Metodología y Herramientas

Se aplicó un análisis de composición de software (*Software Composition Analysis*) sobre los dos ecosistemas del repositorio:
1. **Ecosistema Backend (Python 3.12):** Análisis de `requirements.txt` contrastado contra las bases de datos de vulnerabilidades:
   * **PyPA Advisory Database** (Python Packaging Advisory Database).
   * **OSV (Open Source Vulnerabilities)** / Google Open Source Security.
   * **CVE / NVD (National Vulnerability Database)**.
   * Herramienta de escaneo de referencia: `pip-audit`.
2. **Ecosistema Frontend (Node.js 20+):** Análisis de `frontend/package.json` y `frontend/package-lock.json` contrastado contra:
   * **GitHub Advisory Database** (GHSA).
   * Herramienta de escaneo de referencia: `npm audit`.

---

### 2.2 Inventario y Evaluación de Dependencias del Backend (`requirements.txt`)

| Paquete | Versión Declarada en Requisitos | Versión en Entorno | Licencia | Estado de Vulnerabilidad (CVE / PyPA) | Severidad | Evaluación de Riesgo y Mitigación |
|---|:---:|:---:|:---:|:---:|:---:|---|
| **`fastapi`** | `>=0.115,<1` | `0.115.4` | MIT | **Limpio (0 vulnerabilidades)** | N/A | Marco web central. Utiliza validación estricta con Pydantic v2. Mantenido activamente sin vulnerabilidades abiertas en la rama 0.115.x. |
| **`uvicorn`** | `>=0.30,<1` | `0.32.0` | BSD-3 | **Limpio (0 vulnerabilidades)** | N/A | Servidor ASGI. Se opera detrás de proxy inverso (Nginx / Dokploy) que mitiga ataques a nivel de sockets y HTTP desincronizado (*HTTP request smuggling*). |
| **`pytest`** | `>=9.0.3,<10` | `9.0.3` | MIT | **Limpio (V-1 Mitigado)** | N/A | En la auditoría S9 se identificó `PYSEC-2026-1845` en `pytest 8.4.2`. La restricción se elevó a `>=9.0.3`, remediando la vulnerabilidad de ejecución remota por fixtures no confiables. |
| **`httpx`** | `>=0.27,<1` | `0.27.2` | BSD-3 | **Limpio (0 vulnerabilidades)** | N/A | Cliente HTTP utilizado en la suite de pruebas contra FastAPI TestClient. No expuesto directamente en el tráfico de red de producción. |
| **`trafilatura`** | `>=1.12,<2` | `1.12.2` | GPL-3.0 | **Limpio directo / Advertencia operacional (AM-01, AM-02)** | Media | Paquete de scraping web. No presenta CVEs de ejecución arbitraria en 1.12.2, pero sus dependencias transitivas (`urllib3`, `lxml`) deben aislarse contra SSRF y DoS por XML bombs. Requiere configuración explícita de timeout y límites de buffer. |
| **`pyyaml`** | `>=6,<7` | `6.0.2` | MIT | **Limpio (Uso Seguro)** | N/A | Utilizado en `tests/test_contract.py` para cargar `openapi.yaml`. Históricamente PyYAML presentó vulnerabilidades con `yaml.load()`; en VeriFacts se usa exclusivamente `yaml.safe_load()`, bloqueando deserialización arbitraria de objetos Python. |
| **`jsonschema`** | `>=4,<5` | `4.23.0` | MIT | **Limpio (0 vulnerabilidades directas)** · Deuda V-2 | Baja | Validador de esquemas de respuesta en pruebas de contrato. La advertencia de deprecación de `RefResolver` (V-2 de auditoría S9) es deuda técnica interna de pruebas, sin riesgo de seguridad explotable. |
| **`pytest-cov`** | `==7.1.0` | `7.1.0` | MIT | **Limpio (0 vulnerabilidades)** | N/A | Utilizado para instrumentar cobertura en SonarCloud. Fijado a versión exacta estable. |

---

### 2.3 Inventario y Evaluación de Dependencias del Frontend (`frontend/package.json`)

| Paquete | Versión Declarada | Ámbito (*Scope*) | Estado de Vulnerabilidad (GHSA / npm) | Severidad | Mitigación / Observación |
|---|:---:|:---:|:---:|:---:|---|
| **`react`** | `^18.3.1` | Producción | **Limpio (0 vulnerabilidades)** | N/A | Biblioteca de renderizado UI. Versión estable 18.3.1 inmune a CVEs conocidos de desinfección de atributos JSX. |
| **`react-dom`** | `^18.3.1` | Producción | **Limpio (0 vulnerabilidades)** | N/A | Renderizado en DOM web. Manipulación libre de `dangerouslySetInnerHTML`, evitando Cross-Site Scripting (XSS). |
| **`vite`** | `^5.4.11` | Desarrollo (Build) | **Limpio (0 vulnerabilidades)** | N/A | Servidor y empaquetador frontend. Actualizado por encima de las versiones 5.0.x-5.2.x afectadas por divulgación de archivos locales mediante rutas de desarrollo (`GHSA-vg6x-rcgg-rjx6`). |
| **`typescript`** | `^5.6.3` | Desarrollo | **Limpio (0 vulnerabilidades)** | N/A | Compilador estático. Solo interviene en tiempo de compilación. |
| **`@vitejs/plugin-react`** | `^4.3.4` | Desarrollo | **Limpio (0 vulnerabilidades)** | N/A | Complemento oficial de Vite para React. |

---

### 2.4 Matriz Consolidada de Hallazgos SCA y Plan de Remediación

```mermaid
flowchart LR
    SCA["Auditoría SCA"] --> Findings["Hallazgos Identificados"]
    Findings --> H1["Pytest 8.4.2 (PYSEC-2026-1845)"]
    Findings --> H2["Deprecación jsonschema RefResolver"]
    Findings --> H3["Scraping no acotado en Trafilatura"]
    
    H1 --> R1["✅ MITIGADO: Actualizado a pytest>=9.0.3"]
    H2 --> R2["🟡 ACEPTADO: Deuda técnica acotada a suite de pruebas"]
    H3 --> R3["🔴 PENDIENTE: Requiere envoltorio de timeout y validación de IP"]
```

| ID Hallazgo | Componente | Vulnerabilidad / CVE | Severidad | Estado | Plan de Mitigación / Acción Aplicada |
|:---:|---|:---:|:---:|:---:|---|
| **SCA-01** | `pytest` en `requirements.txt` | `PYSEC-2026-1845` (RCE vía fixtures maliciosos) | Media | ✅ **Mitigado** | Resuelto en S9 mediante actualización a `pytest>=9.0.3,<10`. Se comprobó que la suite pasa al 100% con pytest 9. |
| **SCA-02** | `trafilatura` en `requirements.txt` | Ausencia de restricciones de origen en red (*CWE-918: SSRF*) | Alta | 🔴 **Pendiente** | Implementar la clase adaptadora `SafeWebExtractor` que envuelva `trafilatura.fetch_url` con verificación previa de IP contra rangos privados (ver AM-01). |
| **SCA-03** | `jsonschema` en `tests/` | Deprecación de `RefResolver` (*CWE-477: Use of Obsolete Function*) | Baja | 🟡 **Abierto** | Deuda técnica documentada en [arc42 §11](../arc42/11-riesgos-y-deuda-tecnica.md) (DT-02). Se migrará a `jsonschema.protocols.Validator` en el siguiente ciclo sin impacto en seguridad activa. |

---

## 3. Sección de Privacidad (*Privacy by Design*)

### 3.1 Marco Regulatorio y Postura Arquitectónica

VeriFacts adopta un enfoque proactivo de **Privacidad desde el Diseño y por Defecto (*Privacy by Design and by Default*)**, alineado con los estándares internacionales y locales:
* **Colombia:** Ley Estatutaria 1581 de 2012 y Decreto 1377 de 2013 (Régimen General de Protección de Datos Personales / Habeas Data).
* **Internacional:** Principios del Reglamento General de Protección de Datos (RGPD / GDPR - Artículos 5 y 25).

> **Premisa Fundamental del Negocio:** VeriFacts es un analizador de desinformación enfocado en patrones retóricos y semánticos del discurso público, **no una plataforma de vigilancia, perfilamiento de usuarios ni almacenamiento de correspondencia privada**.

---

### 3.2 Inventario de Datos y Clasificación de Información (PII)

Se mapea la totalidad de los datos que ingresan, transitan y se almacenan en el sistema:

| Tipo de Dato | Origen / Flujo | Clasificación de Privacidad | Tratamiento en el Sistema | ¿Contiene PII? (Personally Identifiable Information) | Riesgo de Privacidad |
|---|---|:---:|---|:---:|---|
| **Texto de la noticia a analizar (`content`)** | `POST /analysis` (ingresado por el usuario en frontend o API) | **Confidencial / Público no verificado** | Se almacena en la tabla `analyses` de SQLite (`repository.py`). Se expone en `GET /analysis` y `GET /analysis/{id}`. | **Potencial.** El usuario puede ingresar textos que contengan nombres propios, números de teléfono, direcciones físicas, correos electrónicos o señalamientos personales. | 🔴 **ALTO:** Exposición pública en el historial si el texto contenía datos sensibles privados. |
| **URL externa de la noticia (`url`)** | `POST /analysis` | **Público / Referencial** | Se descarga el HTML y se almacena en `source_type="url"`. | **Potencial bajo.** Puede contener tokens de sesión o parámetros privados en la query string (`?token=...`, `?user_id=...`). | 🟡 **MEDIO:** Persistencia accidental de parámetros sensibles en la URL. |
| **Puntuación y Factores (`score`, `classification`, `factors`)** | Generado por el motor `Scoring` y `Analysis` | **Dato Técnico Interno** | Se persiste en SQLite junto al análisis. | **NO.** Valores numéricos y etiquetas predefinidas del catálogo del sistema. | 🟢 **NULO.** |
| **Dirección IP del cliente (`client.host`)** | Nginx / Dokploy Proxy / Uvicorn | **Dato de Conexión / PII Indirecto** | No se persiste en base de datos. Solo visible en logs efímeros de acceso de Uvicorn/Nginx en stdout. | **SÍ (Indirecto).** Identificador de red del visitante. | 🟡 **MEDIO:** Si los logs de red se retuvieran indefinidamente o se hicieran públicos. |
| **Telemetría y Métricas (`/metrics`)** | Módulo `observability.py` | **Dato Técnico Agregado** | Contadores y latencias en memoria (Prometheus format). | **NO.** Solo almacena conteos globales y distribuciones de tiempo sin etiquetas de usuario. | 🟢 **NULO.** |

---

### 3.3 Principios de Privacidad Aplicados y Controles Arquitectónicos

```mermaid
flowchart TD
    subgraph Principios["Principios de Privacidad (Privacy by Design)"]
        P1["1. Minimización de Datos"]
        P2["2. Limitación de la Finalidad"]
        P3["3. Retención Acotada (TTL)"]
        P4["4. Derecho al Olvido y Supresión"]
        P5["5. Confidencialidad en Observabilidad"]
    end

    P1 --> C1["Sin cuentas, sin login, sin vinculación de identidad a los análisis (ADR-0011)"]
    P2 --> C2["Procesamiento exclusivo para puntuación lingüística; sin perfilamiento"]
    P3 --> C3["Política de purga programada: eliminación de registros tras 30 días"]
    P4 --> C4["Procedimiento de eliminación por hash o ID ante solicitud de Habeas Data"]
    P5 --> C5["Logs limpios: no imprimir cuerpo de texto ni parámetros en consola"]
```

#### 1. Minimización de Datos (*Data Minimization*)
* **Decisión de Arquitectura [ADR-0011](../adr/0011-historial-registro-unico-sin-propietario.md):** El sistema **no exige registro de usuarios, credenciales ni autenticación personal** para consumir el servicio.
* Cada análisis se almacena como un registro anónimo disociado. No existe relación entre un registro de análisis y la identidad civil del usuario que lo originó, eliminando el riesgo de trazabilidad de hábitos de lectura o ideología política de usuarios individuales.

#### 2. Limitación de la Finalidad (*Purpose Limitation*)
* Los datos recibidos se utilizan única y exclusivamente para computar las heurísticas lingüísticas de credibilidad (`RuleAnalyzer`).
* El sistema no comparte, vende ni procesa los textos analizados con modelos externos comerciales generativos en tiempo de ejecución (decisión ratificada en [ADR-0007](../adr/0007-no-incorporar-componente-generativo.md)).

#### 3. Política de Retención Acotada y Depuración (*Storage Limitation*)
* **Diagnóstico actual:** SQLite almacena registros indefinidamente. Esto representa un pasivo de privacidad a medida que el historial acumula entradas enviadas por usuarios desconocidos.
* **Política de Retención Asignada:**
  * **Ventana de retención activa:** 30 días calendario para análisis persistidos.
  * **Mecanismo de depuración:** Tarea cron / script de mantenimiento que ejecuta:
    ```sql
    DELETE FROM analyses WHERE created_at < datetime('now', '-30 days');
    ```
  * Permite optimizar el almacenamiento del contenedor (restringido a 512 MB de memoria y volúmenes acotados en Dokploy) cumpliendo a la vez con el principio de limitación de conservación.

#### 4. Derecho a la Supresión y Habeas Data (*Right to Erasure*)
* Ante una solicitud formal de un titular cuyos datos personales hayan sido indebidamente incluidos en una noticia analizada y persistida en el sistema, la arquitectura contempla el procedimiento de supresión:
  1. Identificación del registro por `id` o mediante cálculo de coincidencia de huella digital SHA-256 del contenido (`hash(content)`).
  2. Eliminación física mediante el repositorio de persistencia (`repository.delete_analysis(id)`).
  3. Confirmación de no persistencia en copias residuales (al ser SQLite local, la supresión en el archivo elimina la visibilidad en la API inmediatamente).

#### 5. Confidencialidad en Observabilidad y Logs
* `app/observability.py` y `app/api/routes.py` instrumentan métricas y trazas operacionales.
* **Regla transversal:** Ningún logger del sistema debe volcar el contenido completo de `request.content` en los logs estándar (`stdout`/`stderr`), preservando la confidencialidad de la información enviada ante sistemas de recolección de logs centralizados.

---

### 3.4 Riesgos de Privacidad Residuales y Plan de Acción

| ID | Riesgo de Privacidad Residual | Causa Raíz | Mitigación Arquitectónica Compasiva | Estado |
|:---:|---|---|---|:---:|
| **PR-01** | **Lectura pública indiscriminada del historial completo** | Endpoint `GET /analysis` retorna el listado histórico completo con el texto íntegro a cualquier cliente anónimo. | Modificar el DTO `AnalysisListItemResponse` para que **no incluya el campo `content`** (solo ID, score, clasificación, fecha y tipo de fuente). Para ver el texto completo, requerir conocimiento exacto del ID o token de consulta. | **Diseñado (Pendiente de código)** |
| **PR-02** | **Captura de credenciales embebidas en URLs de scraping** | El usuario envía URLs con sintaxis `http://usuario:clave@sitio.com/noticia` o con tokens de autenticación `?auth=ey...`. | Sanitizar la URL antes de ejecutar el scraping y antes de persistirla en `source_type="url"`, removiendo mediante expresiones regulares (`urllib.parse`) cualquier componente de `userinfo` o parámetros comunes de autenticación (`token`, `auth`, `key`, `session`). | **Diseñado (Pendiente de código)** |
| **PR-03** | **Indexación por motores de búsqueda de textos con PII** | La interfaz web o la API pueden ser indexadas por rastreadores web públicos (Googlebot, Bingbot), haciendo descubribles análisis con datos personales. | Implementar cabecera HTTP `X-Robots-Tag: noindex, nofollow` en todas las respuestas de la API FastAPI y en `robots.txt` del frontend web. | **Diseñado (Pendiente de código)** |

---

## 4. Trazabilidad con el Repositorio

Para garantizar la coherencia arquitectónica y documental exigida por el curso, la presente entrega se integra formalmente en los artefactos del sistema:

* **Matriz de Aspectos Arquitectónicos:** Se registra el aspecto **A-12** en [`docs/aspectos.md`](../aspectos.md#matriz-de-trazabilidad).
* **Conceptos Transversales:** Se incorpora la subsección `8.11 Privacidad y Protección de Datos Personales` en [arc42 §8](../arc42/08-conceptos-transversales.md#811-privacidad-y-protección-de-datos-personales-s13).
* **Riesgos y Deuda Técnica:** Se vinculan las amenazas AM-01 a AM-08 con los riesgos MF-01, MF-03, MF-06, MF-07, MF-08 y MF-09 en [arc42 §11](../arc42/11-riesgos-y-deuda-tecnica.md).
* **Decisiones Arquitectónicas Relacionadas:**
  * [ADR-0007](../adr/0007-no-incorporar-componente-generativo.md): No incorporar modelos generativos externos que procesen datos de usuarios.
  * [ADR-0010](../adr/0010-despliegue-laboratorio-dokploy.md): Plataforma de despliegue y consideraciones de red en el laboratorio.
  * [ADR-0011](../adr/0011-historial-registro-unico-sin-propietario.md): Historial de análisis anónimo sin identificación de propietarios.
  * [ADR-0012](../adr/0012-modelo-almacenamiento-sqlite-costo-reversion.md): Persistencia en SQLite y costos de migración/reversión.

---

## 5. Instrucciones para Reproducir las Auditorías en Local

Para replicar y verificar las comprobaciones de dependencias y límites de seguridad en cualquier estación local:

```bash
# 1. Ejecutar la suite completa de pruebas unitarias, de contrato y de límites
python -m pytest -q

# 2. Auditar vulnerabilidades en dependencias de Python (SCA)
pip install pip-audit
pip-audit -r requirements.txt

# 3. Auditar dependencias en el frontend (Node / React)
cd frontend
npm audit
cd ..

# 4. Verificar ausencia de secretos o credenciales en el código fuente
git log --all -p -G"(password|secret|api_key|token)\s*=\s*['\"][^'\"]+['\"]" -- app tests frontend
```
