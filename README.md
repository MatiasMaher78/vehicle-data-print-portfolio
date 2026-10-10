# Vehicle Data Print — Automotive Homologation Platform (Portfolio Version)

A full-stack web application that automates the extraction, processing, and documentation of technical vehicle data for automotive homologation — replacing a manual, multi-hour workflow with a guided, review-and-export process.

> **Portfolio version notice**: this is a sanitized version of a production system built for real automotive homologation work. Source-specific scraping logic, data transformation rules, and real data sources have been simplified or omitted to protect proprietary implementation details. See [What's simplified in this version](#whats-simplified-in-this-version) below for specifics.

---

## What it does

Homologating a vehicle — certifying that it meets applicable technical regulations — requires collecting detailed specifications from multiple official sources, reconciling discrepancies between them, and producing a formatted document in the target country's language.

This platform automates that workflow:

1. The user submits up to 3 URLs, one per data source, for a given vehicle.
2. The backend scrapes all 3 sources concurrently.
3. Each source's raw data is transformed into a shared canonical schema of **97 structured technical fields** (dimensions, engine, emissions, consumption, etc.).
4. The 3 sets of values are merged using field-level priority rules, with conflicts resolved automatically where possible.
5. The user reviews and edits the merged result in a clean, categorized interface before anything is finalized — a human always has the final say.
6. A professional `.docx` document is generated from a language-specific template and made available for download.

**Real-world impact**: in production, this reduced the manual workflow from roughly 40-50 minutes down to about 15 minutes per vehicle. During its validation period it was used daily by real automotive homologation technicians — ~3 users processing an estimated ~125 vehicles/month. It was not continued commercially after that period.

### Key capabilities

- Processes data from **3 specialized sources** concurrently
- Manages **97 structured technical fields** per vehicle (dimensions, engine, emissions, consumption, etc.)
- Generates export documents in **10 languages**: English, German, Portuguese, Italian, French, Dutch, Swedish, Romanian, Polish, and Czech
- Supports **hybrid and electric vehicles**, with dedicated logic for fuel-type detection and electric-range fields
- Keeps a **per-user download history**, with the ability to flag records as "Under review"
- Authenticated access — each user only sees their own activity

---

## Technical overview

### Architecture

```
React Frontend (TypeScript)
        |
        | REST API (JWT-authenticated)
        v
FastAPI Backend (Python)
   |         |          |
   v         v          v
Scraping  Transform   DOCX Export
Service   Service     Service
   |                    |
   v                    v
3 Data             Supabase Storage
Sources            (DOCX templates)
        |
        v
   Supabase
   PostgreSQL
   (users + downloads)
```

**Request flow:**
1. An authenticated user submits up to 3 URLs plus a transmission option.
2. The backend validates each URL server-side (HTTPS-only, allowlisted domain, SSRF protections — see [Security notes](#security-notes)) and scrapes the 3 sources concurrently.
3. Each source is parsed and transformed into the internal schema (97 canonical keys).
4. The 3 results are merged with field-level priority rules.
5. The frontend receives a structured table — the user can review and edit any field.
6. On export: the backend renders a language-specific DOCX template via Jinja2, logs the download, and streams the file back.

### Stack

#### Backend

| Technology | Role |
|---|---|
| **Python 3.11+** | Primary language |
| **FastAPI** | REST API framework (async, auto-generated docs) |
| **Uvicorn** | ASGI server |
| **Supabase (Python client)** | Auth (JWT) + PostgreSQL |
| **BeautifulSoup4** | HTML parsing for the scrapers |
| **Requests** | HTTP client for scraping |
| **Pandas** | Data manipulation and merging |
| **python-docx / docxtpl** | DOCX generation with Jinja2 templating |
| **Pydantic** | Request/response schema validation |
| **python-decouple** | Environment variable management |

#### Frontend

| Technology | Role |
|---|---|
| **React 19** | UI framework |
| **TypeScript 5.8** | Typed JavaScript |
| **Vite 6** | Bundler and dev server |
| **React Router DOM 7** | Client-side routing, protected routes |
| **Axios** | HTTP client with auth interceptors |
| **Tailwind CSS 3** | Utility-first styling |
| **Lucide React / Heroicons** | Icon libraries |
| **react-toastify** | Toast notifications |

#### Infrastructure & data

| Technology | Role |
|---|---|
| **Supabase** | Auth (JWT), PostgreSQL database, file storage |
| **PostgreSQL** | Per-user download history persistence |
| **Supabase Storage** | Stores the per-language DOCX templates (**not included in this repository** — the export endpoint downloads them at request time; see [DOCX templates](#docx-templates)) |

### API endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/auth/login` | Authenticates, returns a JWT |
| `GET` | `/api/v1/auth/users/me` | Returns the current user |
| `POST` | `/api/v1/process-vehicle` | Scraping + transformation + merge |
| `POST` | `/api/v1/export-document` | Generates and streams the DOCX |
| `GET` | `/api/v1/profile/` | User profile + download history |
| `PATCH` | `/api/v1/downloads/{id}/status` | Updates a download's status |

All endpoints except login require a `Bearer` JWT.

### Data model

**`public.downloads`** (PostgreSQL via Supabase)

| Column | Type | Description |
|---|---|---|
| `id` | UUID | Primary key |
| `user_id` | UUID | References `auth.users` |
| `cds_identifier` | text | Vehicle identifier |
| `template_language` | text | Language used for export |
| `exported_data_snapshot` | jsonb | Full data snapshot at export time |
| `status` | text | `Ok` or `Under review` |
| `downloaded_at` | timestamptz | Download timestamp (automatic) |

### Project structure

```
vehicle-data-print-portfolio/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI app, CORS config
│   │   ├── api/v1/
│   │   │   ├── auth.py              # Login + /users/me
│   │   │   ├── processing.py        # /process-vehicle
│   │   │   ├── export.py            # /export-document
│   │   │   ├── profile.py           # User profile
│   │   │   └── downloads.py         # Status updates
│   │   ├── scraping/
│   │   │   ├── scraping_site_1.py   # Example scraper (simplified, see notice below)
│   │   │   ├── scraping_site_2.py   # Example scraper (simplified, see notice below)
│   │   │   └── scraping_site_3.py   # Example scraper (simplified, see notice below)
│   │   ├── data_transformation/
│   │   │   ├── master_keys.py       # 97 canonical field definitions
│   │   │   ├── key_map.py           # Source key -> canonical key mapping
│   │   │   ├── transform_site1.py   # Demo stub (see notice below)
│   │   │   ├── transform_site2.py   # Demo stub (see notice below)
│   │   │   └── transform_site3.py   # Demo stub (see notice below)
│   │   └── services/
│   │       ├── scraping_service.py       # Async orchestration
│   │       ├── transform_service.py      # Merge logic (simplified, see notice below)
│   │       ├── docx_service.py           # Template rendering
│   │       └── url_validation_service.py # Server-side URL/SSRF validation
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── pages/
    │   │   ├── VehicleHomologationPage.tsx
    │   │   ├── LoginPage.tsx
    │   │   └── UserProfilePage.tsx
    │   ├── contexts/AuthContext.tsx
    │   ├── services/api.ts
    │   ├── constants/
    │   │   ├── vehicleFormSections.tsx
    │   │   └── localization.ts
    │   └── types/vehicleSpecs.ts
    └── package.json
```

### Implementation notes

- **Concurrent scraping**: the 3 sources are queried in parallel with `asyncio`, minimizing total wait time.
- **Priority-based merge logic**: each of the 97 fields has an explicit source priority; the production system also includes field-specific override rules and emissions-format handling that vary by regulatory standard (simplified in this version, see below).
- **Server-side URL validation**: every submitted URL is validated against an HTTPS-only, domain-allowlisted policy with SSRF protections (rejecting private/loopback/link-local/metadata addresses) and validates the full redirect chain before scraping.
- **Template rendering**: DOCX files are stored in Supabase Storage, fetched at export time, and rendered with `docxtpl` (Jinja2 engine). Dynamic variables include electric-vehicle remarks, regulatory compliance notes, and the 97 data fields.
- **Auth flow**: users log in with a username (not email); the backend resolves the associated email from Supabase metadata, authenticates against Supabase Auth, and returns a JWT. The frontend stores it in `localStorage` and injects it via Axios interceptors.
- **Client-side persistence**: form state, extracted data, and submitted URLs persist in `localStorage` so in-progress work survives a page reload.

---

## What's simplified in this version

This repository is a sanitized copy of a production codebase built for real automotive homologation work. To protect proprietary implementation details and the identity of the real third-party data sources, the following were simplified or omitted:

- **Source-specific scraping logic** (`backend/app/scraping/scraping_site_*.py`): the real selectors and parsing rules — reverse-engineered from each source's actual page structure over time — were replaced with example scrapers that demonstrate the same architecture (`BaseScraper` subclass + BeautifulSoup + pandas) against a generic, hypothetical HTML structure.
- **Source-specific transformation logic** (`backend/app/data_transformation/transform_site*.py`): the real cleaning/normalization rules were replaced with stubs that keep the same class/method interface but return example data shaped like real output, so the pipeline remains runnable end-to-end as a demo.
- **Field-level merge/priority rules** (`backend/app/services/transform_service.py`): the real system applies field-specific overrides and regulatory-standard-dependent post-processing; this version uses a single, uniform priority rule across all fields.
- **Real data source identities**: the 3 actual source domains have been replaced with placeholder domains (`source1.example.com`, `source2.example.com`, `source3.example.com`) throughout the code, UI labels, and placeholder examples. The real source logos were also replaced with generic icons.

The **97-field canonical schema** itself (`master_keys.py`, `key_map.py`) mirrors the structure of a standard European Certificate of Conformity and is not proprietary — it's kept intact to demonstrate the domain modeling.

### DOCX templates

The per-language `.docx` templates are **not included in this repository**. In production, `docx_service.py` downloads them at request time from a Supabase Storage bucket. Running the export endpoint in this portfolio version requires pointing `DOCX_TEMPLATE_BUCKET` at your own bucket with templates that use the Jinja2 markers defined in `marker_map.py`.

---

## Security notes

- Server-side URL validation enforces HTTPS, a domain allowlist, and blocks private/loopback/link-local/metadata IP ranges (SSRF mitigation), including validation of the full redirect chain.
- JWT-based authentication via Supabase Auth; all data endpoints require a valid bearer token.
- Per-user data isolation: download history and status updates are scoped to the authenticated user's ID.
- No secrets are present in this repository — see `.env.example` for the required environment variables.

---

## Running locally

This portfolio version runs the same way as the production app, with the caveat that the scraping and transformation logic are simplified demo stubs (see above) — the pipeline is runnable end-to-end, but the extracted values are placeholders rather than real vehicle data.

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
# Create a .env with SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_KEY
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Interactive API docs are available at `http://localhost:8000/docs` (Swagger UI, auto-generated by FastAPI).

You'll need your own Supabase project (Auth + PostgreSQL `downloads` table + Storage bucket for templates) to run the full flow end-to-end; see `.env.example` for the required variables.
