# AI Research & Product Intelligence Bot (Gmail Edition)

Scrapes 5 AI sources, summarizes (optional Gemini), logs to **Google Sheets**, and emails a digest via **Gmail**.
Runs **twice daily** on **GitHub Actions** (free).

**Schedule (PKT):** 09:00 and 17:00 (04:00 & 12:00 UTC)  
**Digest size:** Top 3  
**Sheet tab:** `sheet 1`  
**Default Sheet ID:** `10JPJ33f64h6Wi8aTWi4XWaSFeFZYLn2Gyfx8_p6pzgg`

## Sources (5)
- arXiv — cs.AI — https://rss.arxiv.org/rss/cs.AI
- arXiv — cs.LG — https://rss.arxiv.org/rss/cs.LG
- Google Research Blog — https://research.google/blog/rss/
- Google DeepMind Blog — https://deepmind.google/blog/rss.xml
- IAPP Daily Dashboard — https://iapp.org/rss/daily-dashboard/

## Setup
1) Create a **Google Cloud service account** + JSON key; share your sheet with that email (Editor).  
2) Create a **Gmail App Password** (Google Account → Security → App passwords).  
3) Add GitHub Secrets: `GCP_SERVICE_ACCOUNT_JSON`, `GMAIL_USER`, `GMAIL_APP_PASSWORD`, `GMAIL_TO` (+ optional `GEMINI_API_KEY`, `SHEET_ID`, `SHEET_TAB`).  
4) Push this repo, then run the workflow in **Actions**.

Columns required in the Sheet (exact order):  
`Type | Source | Title | Author/Company | Date | ExecutiveSummary | BusinessInsight | RelevanceScore | Link | CanonicalLink | PrimaryOrSecondary | DedupeKey | Status`
