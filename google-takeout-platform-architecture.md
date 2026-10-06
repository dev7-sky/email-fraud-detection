# Google Takeout Parser & Analytics Platform
## Complete System Architecture — IFSO Delhi Police (Internship Project)

---

## Table of Contents
1. Project Overview
2. Recommended Tech Stack
3. System Architecture
4. Folder Structure
5. Database Schema
6. Parser Architecture
7. Dashboard Design
8. Risk & Investigation Engine
9. MVP Roadmap
10. Advanced Version Roadmap
11. Step-by-Step Implementation Plan
12. Resume Presentation Guide

---

## 1. Project Overview

This platform ingests an entire Google Takeout export (folder or ZIP), automatically
discovers and parses all data, runs forensic analytics, flags risk keywords, and
produces investigation-grade reports — without manual file selection.

**Target users:** Digital forensics analysts, cybercrime investigators (IFSO).
**Data scale:** Handles exports from 10 MB to 50 GB.
**Deployment:** Local desktop app (air-gapped safe) or internal web server.

---

## 2. Recommended Tech Stack

### Backend
| Component         | Choice              | Why |
|-------------------|---------------------|-----|
| Language          | Python 3.11+        | Best ecosystem for forensics, data, and parsing |
| Web Framework     | FastAPI             | Async, fast, auto-docs, easy REST APIs |
| Database          | SQLite (MVP) → PostgreSQL (prod) | SQLite = zero setup for internship; Postgres for scale |
| ORM               | SQLAlchemy 2.0      | Works with both DBs, powerful querying |
| Task Queue        | Celery + Redis      | Background parsing of large exports |
| Parsing           | orjson, lxml, ijson | Fast JSON/XML/HTML streaming parsing |
| NLP / Keywords    | rapidfuzz           | Fuzzy keyword matching |
| Geo               | geopy               | Reverse geocoding of location data |

### Frontend
**Recommendation: Streamlit for MVP → React + FastAPI for advanced**

**Streamlit (MVP)**
- Zero frontend code needed
- Python-only
- Built-in charts, tables, filters
- Deploy in 1 command
- Perfect for internship demo

**React + Recharts (Advanced)**
- Professional SPA
- Real-time updates via WebSocket
- Better for production

### Export / Reports
| Feature   | Library          |
|-----------|------------------|
| Excel     | openpyxl         |
| PDF       | reportlab / weasyprint |
| CSV       | Python stdlib csv |
| Charts in PDF | matplotlib  |

---

## 3. System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                           │
│              (Streamlit MVP / React Advanced)                   │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTP / WebSocket
┌──────────────────────────▼──────────────────────────────────────┐
│                      FastAPI Backend                            │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────────┐ │
│  │  Ingestion  │  │   Analytics  │  │   Investigation API    │ │
│  │   Router    │  │    Engine    │  │   (Risk / Keywords)    │ │
│  └──────┬──────┘  └──────┬───────┘  └──────────┬─────────────┘ │
└─────────│────────────────│─────────────────────│───────────────┘
          │                │                     │
┌─────────▼────────────────▼─────────────────────▼───────────────┐
│                     Parser Engine                               │
│  ┌──────────────┐  ┌────────────────┐  ┌──────────────────┐    │
│  │  Discovery   │  │ Plugin Parsers │  │  Normalizer      │    │
│  │  (Scanner)   │  │ (per service)  │  │  (common schema) │    │
│  └──────────────┘  └────────────────┘  └──────────────────┘    │
└─────────────────────────────┬───────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────┐
│                        Database Layer                           │
│                   SQLite / PostgreSQL                           │
│   sessions │ records │ flags │ analytics_cache │ exports        │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow
```
ZIP / Folder
    │
    ▼
[1] Discovery Scanner
    Recursively finds all files
    Identifies data type by path + content
    Deduplicates by hash
    │
    ▼
[2] Parser Plugins (one per service)
    Reads raw file → normalized record
    Handles schema variants
    Stores unknown fields as JSON blob
    │
    ▼
[3] Database Ingestion
    Bulk insert with conflict handling
    Indexes for fast querying
    │
    ▼
[4] Analytics Engine
    Runs aggregations (top domains, hourly heatmaps, etc.)
    Caches results
    │
    ▼
[5] Risk Engine
    Scans all text fields for keywords
    Scores and categorizes
    │
    ▼
[6] Dashboard / Reports
    Live querying
    Export to CSV / Excel / PDF
```

---

## 4. Folder Structure

```
takeout-analyzer/
│
├── README.md
├── requirements.txt
├── .env.example
├── run.py                         # Entry point
│
├── backend/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app
│   ├── config.py                  # Settings, paths, env vars
│   │
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── scanner.py             # Folder/ZIP walker, file classifier
│   │   ├── deduplicator.py        # SHA-256 hash tracking
│   │   └── session_manager.py     # Tracks parse sessions
│   │
│   ├── parsers/
│   │   ├── __init__.py
│   │   ├── base_parser.py         # Abstract base class all parsers extend
│   │   ├── registry.py            # Auto-registers all parsers
│   │   │
│   │   ├── browser/
│   │   │   ├── chrome_history.py  # "Browser History" key
│   │   │   ├── bookmarks.py       # JSON + HTML bookmarks
│   │   │   └── autofill.py        # "Autofill" key
│   │   │
│   │   ├── search/
│   │   │   ├── search_history.py  # Search History.json
│   │   │   └── my_activity.py     # MyActivity.json (generic)
│   │   │
│   │   ├── youtube/
│   │   │   ├── watch_history.py
│   │   │   └── search_history.py
│   │   │
│   │   ├── location/
│   │   │   ├── records.py         # Records.json (location history)
│   │   │   └── semantic_history.py
│   │   │
│   │   ├── gmail/
│   │   │   └── mbox_parser.py
│   │   │
│   │   ├── drive/
│   │   │   └── metadata.py
│   │   │
│   │   ├── photos/
│   │   │   └── metadata.py
│   │   │
│   │   ├── contacts/
│   │   │   └── contacts_parser.py  # vCard + CSV
│   │   │
│   │   ├── calendar/
│   │   │   └── ics_parser.py
│   │   │
│   │   ├── assistant/
│   │   │   └── activity.py
│   │   │
│   │   └── generic/
│   │       ├── json_parser.py      # Fallback for unknown JSONs
│   │       └── csv_parser.py
│   │
│   ├── analytics/
│   │   ├── __init__.py
│   │   ├── engine.py              # Orchestrates all analytics
│   │   ├── browser_analytics.py
│   │   ├── search_analytics.py
│   │   ├── youtube_analytics.py
│   │   ├── location_analytics.py
│   │   ├── temporal_analytics.py  # Hourly/daily/monthly heatmaps
│   │   └── correlation.py         # Cross-service insights
│   │
│   ├── investigation/
│   │   ├── __init__.py
│   │   ├── risk_engine.py         # Keyword flagging + scoring
│   │   ├── keyword_config.py      # Default + custom keyword categories
│   │   ├── domain_checker.py      # Suspicious domain detection
│   │   └── report_builder.py      # Investigation report generator
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py              # SQLAlchemy models
│   │   ├── connection.py          # DB engine + session factory
│   │   └── migrations/            # Alembic migrations
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── ingestion.py       # POST /upload, GET /sessions
│   │   │   ├── analytics.py       # GET /analytics/*
│   │   │   ├── investigation.py   # GET /flags, POST /keywords
│   │   │   ├── search.py          # GET /search?q=
│   │   │   └── export.py          # GET /export/{format}
│   │   └── schemas.py             # Pydantic request/response schemas
│   │
│   └── utils/
│       ├── __init__.py
│       ├── timestamp.py           # Chrome epoch, ISO, Unix conversions
│       ├── domain_extractor.py
│       └── logging_config.py
│
├── frontend/                      # Streamlit MVP
│   ├── app.py                     # Main Streamlit entry
│   ├── pages/
│   │   ├── 01_upload.py
│   │   ├── 02_overview.py
│   │   ├── 03_browsing.py
│   │   ├── 04_search.py
│   │   ├── 05_youtube.py
│   │   ├── 06_location.py
│   │   ├── 07_investigation.py
│   │   └── 08_export.py
│   └── components/
│       ├── charts.py              # Reusable Plotly charts
│       ├── tables.py
│       └── heatmaps.py
│
├── data/
│   ├── db/                        # SQLite files
│   ├── uploads/                   # Temp storage for uploaded ZIPs
│   ├── exports/                   # Generated reports
│   └── keywords/
│       └── default_keywords.json
│
└── tests/
    ├── test_parsers/
    ├── test_analytics/
    └── test_investigation/
```

---

## 5. Database Schema

```sql
-- Parse Sessions (one per upload)
CREATE TABLE sessions (
    id          TEXT PRIMARY KEY,         -- UUID
    case_ref    TEXT,                     -- e.g. IFSO/2024/CYB/1042
    created_at  DATETIME,
    source_path TEXT,
    source_hash TEXT,
    status      TEXT,                     -- pending | parsing | complete | error
    total_files INTEGER DEFAULT 0,
    total_records INTEGER DEFAULT 0
);

-- File Inventory (tracks every file processed)
CREATE TABLE source_files (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id  TEXT REFERENCES sessions(id),
    file_path   TEXT,
    file_name   TEXT,
    file_hash   TEXT UNIQUE,              -- SHA-256, prevents double-counting
    parser_used TEXT,
    records_extracted INTEGER DEFAULT 0,
    parse_status TEXT,
    error_msg   TEXT
);

-- Unified Activity Records (all services, normalized)
CREATE TABLE records (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id  TEXT REFERENCES sessions(id),
    service     TEXT,    -- chrome | search | youtube | location | gmail | drive | photos
    record_type TEXT,    -- visit | search | watch | location_point | email | file
    timestamp   DATETIME,
    title       TEXT,
    url         TEXT,
    domain      TEXT,
    query       TEXT,
    channel     TEXT,
    lat         REAL,
    lng         REAL,
    accuracy    REAL,
    source_app  TEXT,
    raw_data    JSON,    -- Store ALL original fields here, nothing discarded
    file_id     INTEGER REFERENCES source_files(id)
);
CREATE INDEX idx_records_session   ON records(session_id);
CREATE INDEX idx_records_service   ON records(service);
CREATE INDEX idx_records_timestamp ON records(timestamp);
CREATE INDEX idx_records_domain    ON records(domain);

-- Risk Flags
CREATE TABLE flags (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id  TEXT REFERENCES sessions(id),
    record_id   INTEGER REFERENCES records(id),
    category    TEXT,    -- violence | drugs | cybercrime | fraud | sexual_crimes
    keyword     TEXT,
    matched_text TEXT,
    severity    INTEGER, -- 1=low 2=medium 3=high
    context     TEXT,    -- surrounding text snippet
    flagged_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    reviewed    BOOLEAN DEFAULT FALSE,
    notes       TEXT     -- analyst notes
);
CREATE INDEX idx_flags_session  ON flags(session_id);
CREATE INDEX idx_flags_category ON flags(category);
CREATE INDEX idx_flags_severity ON flags(severity);

-- Keyword Configuration
CREATE TABLE keyword_categories (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    name     TEXT UNIQUE,
    severity INTEGER DEFAULT 2,
    enabled  BOOLEAN DEFAULT TRUE
);
CREATE TABLE keywords (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER REFERENCES keyword_categories(id),
    keyword     TEXT,
    is_phrase   BOOLEAN DEFAULT FALSE,
    fuzzy       BOOLEAN DEFAULT TRUE,
    enabled     BOOLEAN DEFAULT TRUE,
    added_at    DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Analytics Cache (pre-computed aggregations)
CREATE TABLE analytics_cache (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT REFERENCES sessions(id),
    cache_key  TEXT,     -- e.g. top_domains | hourly_activity
    data       JSON,
    computed_at DATETIME
);
CREATE UNIQUE INDEX idx_cache ON analytics_cache(session_id, cache_key);

-- Exported Reports
CREATE TABLE exports (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT REFERENCES sessions(id),
    format     TEXT,     -- csv | excel | pdf | json
    file_path  TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 6. Parser Architecture

### Base Parser (all parsers extend this)
```python
# backend/parsers/base_parser.py
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterator
from dataclasses import dataclass

@dataclass
class ParsedRecord:
    service: str
    record_type: str
    timestamp: str | None
    title: str | None = None
    url: str | None = None
    domain: str | None = None
    query: str | None = None
    channel: str | None = None
    lat: float | None = None
    lng: float | None = None
    raw_data: dict = None   # ALL original fields preserved

class BaseParser(ABC):
    # Each parser declares what filenames / path patterns it handles
    FILENAME_PATTERNS: list[str] = []
    CONTENT_SIGNATURES: list[str] = []  # JSON keys to detect content type

    @classmethod
    def can_handle(cls, filepath: Path, peek: dict | None = None) -> bool:
        name = filepath.name.lower()
        if any(pat in name for pat in cls.FILENAME_PATTERNS):
            return True
        if peek and cls.CONTENT_SIGNATURES:
            return any(sig in peek for sig in cls.CONTENT_SIGNATURES)
        return False

    @abstractmethod
    def parse(self, filepath: Path) -> Iterator[ParsedRecord]:
        """Yield normalized ParsedRecord objects one at a time (streaming)."""
        ...

    def safe_get(self, d: dict, *keys, default=None):
        """Safely navigate nested dict."""
        for k in keys:
            if not isinstance(d, dict): return default
            d = d.get(k, default)
        return d
```

### Parser Registry (auto-discovers all parsers)
```python
# backend/parsers/registry.py
import importlib, pkgutil
from pathlib import Path
from .base_parser import BaseParser

class ParserRegistry:
    _parsers: list[type[BaseParser]] = []

    @classmethod
    def discover(cls):
        """Auto-import all parser modules."""
        import backend.parsers as pkg
        for _, modname, _ in pkgutil.walk_packages(pkg.__path__, pkg.__name__+'.'):
            importlib.import_module(modname)
        cls._parsers = BaseParser.__subclasses__()

    @classmethod
    def find_parser(cls, filepath: Path, peek: dict | None = None):
        for parser_cls in cls._parsers:
            if parser_cls.can_handle(filepath, peek):
                return parser_cls()
        return None  # Falls back to generic parser
```

### Example: Chrome History Parser
```python
# backend/parsers/browser/chrome_history.py
import orjson
from pathlib import Path
from typing import Iterator
from ..base_parser import BaseParser, ParsedRecord
from backend.utils.timestamp import chrome_usec_to_iso
from backend.utils.domain_extractor import extract_domain

class ChromeHistoryParser(BaseParser):
    FILENAME_PATTERNS = ['history']
    CONTENT_SIGNATURES = ['Browser History']

    def parse(self, filepath: Path) -> Iterator[ParsedRecord]:
        with open(filepath, 'rb') as f:
            data = orjson.loads(f.read())

        entries = (
            data.get('Browser History') or
            data.get('history') or
            (data if isinstance(data, list) else [])
        )

        for item in entries:
            ts = chrome_usec_to_iso(item.get('time_usec'))
            url = item.get('url', '')
            yield ParsedRecord(
                service     = 'chrome',
                record_type = 'visit',
                timestamp   = ts,
                title       = item.get('title', ''),
                url         = url,
                domain      = extract_domain(url),
                raw_data    = item   # preserves favicon_url, client_id, etc.
            )
```

### Example: Autofill Parser
```python
# backend/parsers/browser/autofill.py
import orjson
from pathlib import Path
from typing import Iterator
from ..base_parser import BaseParser, ParsedRecord
from backend.utils.timestamp import chrome_usec_to_iso

class AutofillParser(BaseParser):
    FILENAME_PATTERNS = ['addressesandmore', 'autofill']
    CONTENT_SIGNATURES = ['Autofill']

    def parse(self, filepath: Path) -> Iterator[ParsedRecord]:
        with open(filepath, 'rb') as f:
            data = orjson.loads(f.read())
        for item in data.get('Autofill', []):
            raw_ts = item.get('usage_timestamp', [])
            ts_val = raw_ts[0] if isinstance(raw_ts, list) and raw_ts else raw_ts
            yield ParsedRecord(
                service     = 'autofill',
                record_type = 'form_entry',
                timestamp   = chrome_usec_to_iso(ts_val) if ts_val else None,
                query       = item.get('name', ''),    # field name
                title       = item.get('value', ''),   # typed value
                raw_data    = item
            )
```

### Scanner (the brain of discovery)
```python
# backend/ingestion/scanner.py
import hashlib, zipfile
from pathlib import Path
from typing import Iterator

SUPPORTED_EXTENSIONS = {'.json', '.html', '.htm', '.csv', '.mbox', '.ics', '.vcf', '.xml'}

class TakeoutScanner:
    def __init__(self):
        self.seen_hashes: set[str] = set()

    def scan(self, source: Path) -> Iterator[Path]:
        """Yield unique, supported files from folder or ZIP."""
        if zipfile.is_zipfile(source):
            yield from self._scan_zip(source)
        else:
            yield from self._scan_folder(source)

    def _scan_folder(self, folder: Path) -> Iterator[Path]:
        for f in folder.rglob('*'):
            if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS:
                if self._is_unique(f):
                    yield f

    def _scan_zip(self, zippath: Path) -> Iterator[Path]:
        import tempfile
        with zipfile.ZipFile(zippath) as z:
            tmpdir = Path(tempfile.mkdtemp())
            z.extractall(tmpdir)
            yield from self._scan_folder(tmpdir)

    def _is_unique(self, filepath: Path) -> bool:
        h = hashlib.sha256(filepath.read_bytes()).hexdigest()
        if h in self.seen_hashes:
            return False
        self.seen_hashes.add(h)
        return True
```

---

## 7. Dashboard Design

### Streamlit MVP Layout
```
┌─────────────────────────────────────────────────┐
│  🔍 Google Takeout Analyzer   [Case: IFSO/...]  │
├──────────┬──────────────────────────────────────┤
│          │                                      │
│ Sidebar  │  Main Content Area                   │
│          │                                      │
│ 📂 Upload│  [Overview Cards Row]                │
│ 📊 Over  │  ┌────────┐ ┌────────┐ ┌──────────┐ │
│ 🌐 Browse│  │ 45,231 │ │  12    │ │ 2yr span │ │
│ 🔍 Search│  │records │ │service │ │ of data  │ │
│ 📺 YT    │  └────────┘ └────────┘ └──────────┘ │
│ 📍 Maps  │                                      │
│ ⚠️ Risk  │  [Top Domains Bar Chart]             │
│ 📤 Export│  [Hourly Heatmap]                    │
│          │  [Timeline Scatter]                  │
│ ─────────│                                      │
│ Case Ref │  [Data Table with search + filter]   │
│ [  ...  ]│                                      │
└──────────┴──────────────────────────────────────┘
```

### Key Streamlit Pages

**Upload Page**
- Folder picker (st.file_uploader with directory=True) or ZIP upload
- Progress bar during parsing
- File inventory table (name, records extracted, status)

**Overview Page**
- KPI cards: total records, services, date range, data size
- Plotly bar: top 10 domains
- Plotly heatmap: activity by hour × day of week
- Plotly line: monthly record count over time

**Browsing Analytics**
- Top 20 domains (horizontal bar)
- Hourly activity heatmap
- Domain category breakdown (social/news/shopping/etc.)
- Suspicious domain flags highlighted in red
- Full paginated table with search

**Search Analytics**
- Word cloud (wordcloud library)
- Top 30 queries (bar chart)
- Search frequency over time (line chart)
- Topic auto-categorization

**Investigation / Risk Page**
- Summary: N flags across M categories
- Severity breakdown (pie chart)
- Flagged keyword timeline
- Full flags table with filter by category/severity
- One-click "Generate Report" button

---

## 8. Risk & Investigation Engine

### Keyword Configuration
```python
# backend/investigation/keyword_config.py
DEFAULT_KEYWORDS = {
    "violence": {
        "severity": 3,
        "keywords": ["kill", "murder", "assassination", "bomb", "weapon",
                     "attack", "gun", "rifle", "ammunition", "explosive",
                     "shooting", "stabbing", "terror", "massacre"]
    },
    "sexual_crimes": {
        "severity": 3,
        "keywords": ["rape", "sexual assault", "child exploitation",
                     "trafficking", "grooming", "csam"]
    },
    "drugs": {
        "severity": 2,
        "keywords": ["cocaine", "heroin", "meth", "methamphetamine",
                     "fentanyl", "mdma", "dark web drugs", "drug dealer",
                     "buy drugs online"]
    },
    "fraud": {
        "severity": 2,
        "keywords": ["credit card fraud", "phishing", "identity theft",
                     "money laundering", "fake documents", "carding",
                     "bank account hack"]
    },
    "cybercrime": {
        "severity": 2,
        "keywords": ["malware", "ransomware", "keylogger", "exploit",
                     "botnet", "credential theft", "sql injection",
                     "remote access trojan", "rat", "ddos", "zero day",
                     "vulnerability exploit", "reverse shell"]
    },
    "suspicious_domains": {
        "severity": 2,
        "keywords": ["onion", "tor browser", "dark web", "protonmail",
                     "localbitcoins", "mixers", "crypto tumbler",
                     "anonymous email"]
    }
}
```

### Risk Engine
```python
# backend/investigation/risk_engine.py
from rapidfuzz import fuzz
from .keyword_config import DEFAULT_KEYWORDS

class RiskEngine:
    def __init__(self, custom_keywords: dict = None):
        self.categories = {**DEFAULT_KEYWORDS, **(custom_keywords or {})}

    def scan_record(self, record) -> list[dict]:
        """Scan a single record's text fields for keyword matches."""
        text_fields = ' '.join(filter(None, [
            record.title, record.query, record.url, record.channel
        ])).lower()
        flags = []
        for cat_name, cat in self.categories.items():
            if not cat.get('enabled', True): continue
            for kw in cat['keywords']:
                if self._matches(kw, text_fields):
                    # Get context snippet (50 chars around match)
                    idx = text_fields.find(kw)
                    context = text_fields[max(0,idx-50):idx+len(kw)+50]
                    flags.append({
                        'category': cat_name,
                        'keyword':  kw,
                        'severity': cat['severity'],
                        'context':  context,
                        'record_id': record.id
                    })
        return flags

    def _matches(self, keyword: str, text: str) -> bool:
        if keyword in text: return True  # Exact match
        # Fuzzy match for longer keywords (avoids false positives on short words)
        if len(keyword) > 6:
            return fuzz.partial_ratio(keyword, text) > 85
        return False
```

### Suspicious Domain Checker
```python
# backend/investigation/domain_checker.py
SUSPICIOUS_TLD = {'.onion', '.bit', '.i2p'}
SUSPICIOUS_KEYWORDS = [
    'darkweb', 'deepweb', 'tor2web', 'localbitcoin', 'mixer',
    'tumbler', 'silkroad', '0day', 'carding', 'cvvshop'
]

def score_domain(domain: str) -> dict:
    score = 0
    reasons = []
    if any(domain.endswith(tld) for tld in SUSPICIOUS_TLD):
        score += 50; reasons.append('Dark web TLD')
    if any(kw in domain for kw in SUSPICIOUS_KEYWORDS):
        score += 30; reasons.append('Suspicious keyword in domain')
    return {'domain': domain, 'risk_score': score, 'reasons': reasons}
```

---

## 9. MVP Roadmap (8–10 weeks)

### Week 1–2: Foundation
- [ ] Set up Python project, virtualenv, requirements.txt
- [ ] Implement TakeoutScanner (folder + ZIP walking, deduplication)
- [ ] Implement database models (SQLAlchemy, SQLite)
- [ ] Implement BaseParser + registry
- [ ] Unit tests for scanner and DB

### Week 3–4: Core Parsers
- [ ] ChromeHistoryParser (Browser History key)
- [ ] AutofillParser (Autofill key)
- [ ] ExtensionsParser
- [ ] BookmarksParser (JSON + HTML)
- [ ] YouTubeWatchParser
- [ ] SearchHistoryParser / MyActivityParser
- [ ] Test each parser against real Takeout files

### Week 5: Analytics Engine
- [ ] Top domains / top queries aggregations
- [ ] Hourly + daily heatmap computations
- [ ] Analytics cache layer
- [ ] Temporal trend analysis (monthly counts)

### Week 6: Streamlit Frontend (MVP UI)
- [ ] Upload page with progress bar
- [ ] Overview dashboard (KPI cards + charts)
- [ ] Browse history page
- [ ] Search history page with word frequency

### Week 7: Investigation Engine
- [ ] RiskEngine with default keyword categories
- [ ] Domain risk scorer
- [ ] Investigation dashboard page (flags table, severity chart)
- [ ] Custom keyword editor in UI

### Week 8: Export + Polish
- [ ] CSV export (all data types)
- [ ] Excel export (openpyxl, one sheet per service)
- [ ] PDF investigation report (reportlab)
- [ ] Error handling, logging throughout
- [ ] Final demo preparation

---

## 10. Advanced Version (Post-MVP)

### Phase 2 (Weeks 9–16)
- FastAPI REST backend replacing Streamlit calls
- React + Recharts frontend (professional UI)
- Celery + Redis for background parsing (non-blocking)
- PostgreSQL database for scale
- More parsers: Location/Maps, Gmail MBOX, Drive metadata, Photos EXIF, Calendar ICS
- Leaflet.js interactive map for location history
- WebSocket progress streaming during parse

### Phase 3 (Weeks 17–24)
- Multi-session comparison (compare two suspects)
- Network graph: who-called-whom from contacts + Gmail
- Timeline cross-correlation (was person near location X when search Y happened?)
- ML-based topic clustering of search queries (scikit-learn LDA)
- Encrypted case storage
- Role-based access (analyst vs supervisor)
- Audit log of all analyst actions

---

## 11. Step-by-Step Implementation Plan

### Day 1: Project Setup
```bash
mkdir takeout-analyzer && cd takeout-analyzer
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install fastapi uvicorn sqlalchemy orjson streamlit \
            plotly pandas rapidfuzz openpyxl reportlab \
            python-dotenv loguru pytest

# Create folder structure
mkdir -p backend/{ingestion,parsers/{browser,search,youtube,location,gmail,generic},analytics,investigation,database,api/routes,utils}
mkdir -p frontend/{pages,components}
mkdir -p data/{db,uploads,exports,keywords}
mkdir -p tests/{test_parsers,test_analytics}
touch backend/__init__.py backend/parsers/__init__.py  # etc.
```

### Day 2: Timestamp Utility (critical foundation)
```python
# backend/utils/timestamp.py
from datetime import datetime, timezone

CHROME_EPOCH_OFFSET_MS = 11644473600000  # ms between 1601 and 1970

def chrome_usec_to_iso(usec: int | None) -> str | None:
    """Convert Chrome microsecond timestamp to ISO 8601."""
    if not usec: return None
    try:
        unix_ms = (usec / 1000) - CHROME_EPOCH_OFFSET_MS
        return datetime.fromtimestamp(unix_ms / 1000, tz=timezone.utc).isoformat()
    except: return None

def to_ist(iso: str) -> str:
    """Convert ISO timestamp to IST display string."""
    from datetime import timedelta
    IST = timezone(timedelta(hours=5, minutes=30))
    return datetime.fromisoformat(iso).astimezone(IST).strftime('%Y-%m-%d %H:%M:%S IST')
```

### Day 3–4: Scanner + Database
Implement TakeoutScanner and SQLAlchemy models as shown above.

### Day 5–7: First 3 parsers
Implement ChromeHistoryParser, AutofillParser, BookmarksParser.
Test against your actual Brave export — confirm record counts match.

### Running the MVP
```bash
# Terminal 1: Run Streamlit
streamlit run frontend/app.py

# Streamlit will open at http://localhost:8501
# Drop your Brave export folder
# Instantly see analytics
```

---

## 12. Resume Presentation Guide

**Project Title:**
> Google Takeout Forensic Analytics Platform | IFSO Delhi Police (Internship 2024)

**Description:**
> Built a full-stack digital forensics tool in Python that automatically ingests,
> parses, and analyzes Google/Brave Takeout exports of 50,000+ records. Includes
> risk keyword detection engine, investigation dashboards, and exportable PDF reports
> for cybercrime investigation use.

**Key skills demonstrated:**
- Python (FastAPI, SQLAlchemy, Streamlit)
- Digital forensics & OSINT tooling
- Database design (SQLite/PostgreSQL)
- Data analytics & visualization (Plotly)
- NLP / fuzzy matching (rapidfuzz)
- Modular, plugin-based software architecture
- Law enforcement-grade investigation workflows

**GitHub README should include:**
- Screenshot of dashboard
- Architecture diagram
- Sample anonymized output
- Clear setup instructions

---

## Quick Start (for your internship demo)

```bash
# 1. Clone and install
git clone https://github.com/yourname/takeout-analyzer
cd takeout-analyzer
pip install -r requirements.txt

# 2. Run
streamlit run frontend/app.py

# 3. Open browser at http://localhost:8501
# 4. Drop your Brave export folder
# 5. Analyze
```

---

*Architecture prepared for IFSO Delhi Police Internship Project*
*Designed for a student developer — realistic scope, impressive output*
