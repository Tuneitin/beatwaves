# BeatWave API

Music distribution backend for African artists — built with FastAPI + PostgreSQL, payments via Hubtel MoMo (Ghana).

---

## Features

| Feature | Endpoint prefix |
|---|---|
| Auth (register/login/JWT) | `/auth` |
| Track upload & distribution | `/tracks` |
| Royalties & earnings | `/royalties` |
| MoMo payments & withdrawals | `/payments` |
| Fan store & direct sales | `/sales` |
| File serving (audio, artwork) | `/files` |

---

## Local Setup

### 1. Clone and install

```bash
cd beatwaves
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env — the app works without Hubtel keys in dev (uses mock payments)
```

### 3. Run

```bash
uvicorn app.main:app --reload
```

Visit **http://localhost:8000/docs** for the interactive API docs (Swagger UI).

---

## Deploy to Render (free tier)

### Step 1 — Push to GitHub
```bash
git init
git add .
git commit -m "Initial BeatWave backend"
git remote add origin https://github.com/YOUR_USERNAME/beatwave
git push -u origin main
```

### Step 2 — Create Render services
1. Go to [render.com](https://render.com) and sign up
2. Click **New → Blueprint** and connect your GitHub repo
3. Render reads `render.yaml` and auto-creates:
   - A **PostgreSQL database** (`beatwave-db`)
   - A **Web service** (`beatwave-api`) with the DB URL injected
4. Add your Hubtel keys in Render's Environment tab

Your API will be live at: `https://beatwave-api.onrender.com`

### Step 3 — Add Hubtel MoMo keys
1. Register at [hubtel.com](https://hubtel.com)
2. Get your `Client ID` and `Client Secret` from the dashboard
3. Add to Render environment variables:
   - `HUBTEL_CLIENT_ID`
   - `HUBTEL_CLIENT_SECRET`

> **Without Hubtel keys**, the app runs in mock mode — payments succeed instantly without real money moving. Good for testing.

---

## API Quick Reference

### Register
```bash
POST /auth/register
{"email": "kofi@example.com", "password": "secret", "artist_name": "Kofi Asante"}
```

### Login
```bash
POST /auth/login
{"email": "kofi@example.com", "password": "secret"}
# Returns: {"access_token": "...", "user": {...}}
```

### Upload a track
```bash
POST /tracks/
# Form data (multipart):
# title, genre, release_date, platforms (comma-separated), track_file, artwork_file
```

### Withdraw royalties via MoMo
```bash
POST /payments/withdraw
Authorization: Bearer <token>
{"amount_ghs": 500, "momo_number": "+233551234567", "momo_network": "mtn"}
```

### Create a fan sale listing
```bash
POST /sales/
Authorization: Bearer <token>
{"track_id": 1, "sale_type": "digital_download", "price_ghs": 15}
```

---

## Project Structure

```
.
├── app/
│   ├── core/
│   │   ├── config.py       # Settings (env vars)
│   │   ├── database.py     # SQLAlchemy setup
│   │   └── security.py     # JWT auth
│   ├── models/             # Database tables
│   │   ├── user.py
│   │   ├── track.py
│   │   ├── royalty.py
│   │   ├── transaction.py
│   │   └── sale.py
│   ├── routers/            # API endpoints
│   │   ├── auth.py
│   │   ├── tracks.py
│   │   ├── royalties.py
│   │   ├── payments.py
│   │   └── sales.py
│   ├── schemas/            # Pydantic validation
│   ├── services/
│   │   ├── momo.py         # Hubtel MoMo integration
│   │   └── file_upload.py  # Audio/artwork uploads
│   └── main.py
├── uploads/                # Local file storage
├── requirements.txt
├── render.yaml             # Render deployment config
└── .env.example
```

---

## MoMo Networks Supported

| Network | Code |
|---|---|
| MTN Mobile Money | `mtn` |
| Vodafone Cash | `vodafone` |
| AirtelTigo Money | `airteltigo` |

---

## Subscription Plans

| Plan | Price/month | Releases | Platforms | Fan Store |
|---|---|---|---|---|
| Starter | GH₵ 0 | 1 | 3 | No |
| Pro | GH₵ 99 | Unlimited | All | Yes |
| Label | GH₵ 350 | Unlimited (multi-artist) | All | Yes + splits |
