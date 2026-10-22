# Opportunity Radar — MVP

A small, deployable starter web app for discovering remote-work opportunities and tracking applications. It is a prototype, not yet a production-grade paid service.

## Included
- Responsive opportunity browser with keyword/category filtering
- Seed listings with direct links to original pages
- API endpoints for opportunities, health status, categories and an application tracker
- SQLite database for local development
- Render deployment configuration

## Run locally
Requires Python 3.10+.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```
Open http://127.0.0.1:8000

## API
- `GET /api/health`
- `GET /api/opportunities?q=nurse&category=AI%20evaluation`
- `GET /api/categories`
- `POST /api/applications` with JSON: `{"user_label":"my-private-label","opportunity_id":1,"status":"Interested","notes":"Check requirements"}`
- `GET /api/applications?user_label=my-private-label`

## Deploy
1. Create a GitHub repository and upload these files.
2. Sign in to Render and create a new Web Service from that repository.
3. Render should detect `render.yaml`, or use build command `pip install -r requirements.txt` and start command `uvicorn main:app --host 0.0.0.0 --port $PORT`.
4. Deploy, then test `/api/health` and the home page.

**Important:** SQLite on an ephemeral free hosting disk may reset on redeploy or restart. Before real users depend on saved applications, switch to a managed PostgreSQL database and set a database URL in the app. The current MVP uses no login, so the tracker is not private or safe for sensitive information. Do not enter passwords, medical information, bank details, or other sensitive data.

## Before charging users
- Add authentication and per-user access controls
- Use managed PostgreSQL and backups
- Add an admin workflow for verifying, expiring and removing listings
- Verify each listing at the original employer site; the sample listings are seed examples and may change or expire
- Add monitoring, rate limits, privacy notice, terms, abuse reporting and error handling
- Integrate a payment provider only after its Nigeria eligibility, fees, settlement and compliance requirements are confirmed
- Test mobile usability, security, backups and recovery

## Revenue experiment (not a guarantee)
Start with a free listing browser. Offer an optional paid service such as nurse-focused CV tailoring or an application review, delivered manually at first. Interview 10–15 target users and seek 3 paid pilot customers before building subscriptions or expensive automation. Never charge applicants just to access a job listing unless the value and terms are transparent.
