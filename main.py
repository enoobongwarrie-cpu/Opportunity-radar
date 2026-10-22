from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, HttpUrl
from pathlib import Path
import sqlite3, os

ROOT = Path(__file__).parent
DB_PATH = os.getenv("DATABASE_PATH", str(ROOT / "opportunities.db"))
app = FastAPI(title="Opportunity Radar MVP", version="0.1.0")
app.mount("/static", StaticFiles(directory=str(ROOT / "static")), name="static")

def db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with db() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS opportunities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL, company TEXT NOT NULL, category TEXT NOT NULL,
            location TEXT NOT NULL, pay TEXT, work_type TEXT NOT NULL,
            eligibility TEXT NOT NULL, description TEXT NOT NULL,
            url TEXT NOT NULL, verified_on TEXT NOT NULL, is_active INTEGER NOT NULL DEFAULT 1
        )""")
        con.execute("""CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_label TEXT NOT NULL, opportunity_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'Interested', notes TEXT DEFAULT '',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(opportunity_id) REFERENCES opportunities(id)
        )""")
        count = con.execute("SELECT COUNT(*) FROM opportunities").fetchone()[0]
        if count == 0:
            seed = [
              ("Search Engine Evaluator — English (Nigeria)", "RWS TrainAI", "AI evaluation", "Nigeria (remote)", "Up to $6/hour (listing states)", "Contract / part-time", "Nigeria residency; English; computer and internet; client test", "Evaluate search results and provide quality feedback. Availability and pay can change; confirm on the official listing.", "https://jobs.lever.co/rws/483109df-dff9-4f8e-9b2a-d51572725adc", "2026-10-21"),
              ("Yoruba AI Product Evaluator", "Productive Playhouse", "AI evaluation", "Remote; check Nigeria eligibility", "Not confirmed", "Project-based contract", "Expert Yoruba and strong English; identity checks may apply", "Talent-pool / project listing. Confirm current availability, eligibility, and exact terms before applying.", "https://productiveplayhouse.applytojob.com/apply/tu2ykQmoM6", "2026-10-21"),
              ("Browse AI evaluation roles in Nigeria", "Himalayas", "AI evaluation", "Nigeria / remote listings", "Varies by listing", "Mixed", "Eligibility varies by employer and individual role", "Search results page, not a guarantee that every listed role accepts applicants in Nigeria.", "https://himalayas.app/jobs/countries/nigeria/ai-evaluation", "2026-10-21"),
              ("Browse remote AI training roles in Nigeria", "OpenTrain AI", "AI evaluation", "Nigeria / remote listings", "Varies by listing", "Mixed", "Check each role's country list, requirements and payment terms", "Aggregated opportunities. Always verify a role at the employer's official site before sharing personal information.", "https://www.opentrain.ai/jobs/country/nigeria/", "2026-10-21")
            ]
            con.executemany("""INSERT INTO opportunities
              (title,company,category,location,pay,work_type,eligibility,description,url,verified_on)
              VALUES (?,?,?,?,?,?,?,?,?,?)""", seed)
init_db()

class ApplicationIn(BaseModel):
    user_label: str
    opportunity_id: int
    status: str = "Interested"
    notes: str = ""

@app.get("/", response_class=HTMLResponse)
def home():
    return (ROOT / "static" / "index.html").read_text(encoding="utf-8")

@app.get("/api/health")
def health():
    return {"status":"ok","app":"Opportunity Radar MVP","version":"0.1.0"}

@app.get("/api/opportunities")
def opportunities(q: str = "", category: str = "All"):
    with db() as con:
        sql = "SELECT * FROM opportunities WHERE is_active=1"
        params = []
        if q.strip():
            sql += " AND (title LIKE ? OR company LIKE ? OR description LIKE ? OR eligibility LIKE ?)"
            term = f"%{q.strip()}%"
            params += [term, term, term, term]
        if category != "All":
            sql += " AND category=?"
            params.append(category)
        sql += " ORDER BY id DESC"
        rows = con.execute(sql, params).fetchall()
    return [dict(r) for r in rows]

@app.post("/api/applications")
def add_application(item: ApplicationIn):
    if not item.user_label.strip():
        raise HTTPException(400, "Enter a name or private label for your tracker.")
    with db() as con:
        exists = con.execute("SELECT id FROM opportunities WHERE id=? AND is_active=1", (item.opportunity_id,)).fetchone()
        if not exists:
            raise HTTPException(404, "Opportunity not found.")
        cur = con.execute("INSERT INTO applications (user_label, opportunity_id, status, notes) VALUES (?,?,?,?)",
                          (item.user_label.strip()[:80], item.opportunity_id, item.status[:40], item.notes[:1000]))
        return {"id":cur.lastrowid,"saved":True}

@app.get("/api/applications")
def list_applications(user_label: str):
    with db() as con:
        rows = con.execute("""SELECT a.*, o.title, o.company FROM applications a
                              JOIN opportunities o ON o.id=a.opportunity_id
                              WHERE a.user_label=? ORDER BY a.id DESC""", (user_label,)).fetchall()
    return [dict(r) for r in rows]

@app.get("/api/categories")
def categories():
    with db() as con:
        rows = con.execute("SELECT DISTINCT category FROM opportunities WHERE is_active=1 ORDER BY category").fetchall()
    return ["All"] + [r["category"] for r in rows]
