# Deployment Guide

This repository is ready to deploy. The preferred deployment path is **Render**, using the existing `render.yaml`.

## Deploy to Render

1. Go to https://render.com and sign in or create an account.
2. Click **New** → **Blueprint**.
3. Connect your GitHub account and select the repository `Tuneitin/beatwaves`.
4. Render will read `render.yaml` and propose services:
   - `beatwave-api` (web service)
   - `beatwave-db` (PostgreSQL database)
5. Confirm the services and deploy.

## Environment variables

After deployment, add these environment variables in Render (Service → Environment):

- `HUBTEL_CLIENT_ID`
- `HUBTEL_CLIENT_SECRET`
- `SECRET_KEY` (if not generated automatically)
- `FRONTEND_URL` (optional, default is `http://localhost:3000`)

If you do not add Hubtel keys, the app will run in **mock payment mode** and payment requests will succeed without real money movement.

## Verify deployment

Once the service is live, visit:

- `https://<your-render-service-name>.onrender.com/docs`

Use the Swagger UI to test endpoints.

## Local development

To run locally:

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Then open:

- http://127.0.0.1:8000/docs

## Optional alternative platforms

If you want a backup plan, the code also works on:

- Railway (`railway.app`)
- Vercel (`vercel.com`)
- Heroku (`heroku.com`)
- Fly.io (`fly.io`)

For Render, the `render.yaml` file already describes the service and database.
