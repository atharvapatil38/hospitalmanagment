# 🚀 CarePlus Hospital Management System (HMS) - Vercel Deployment Guide

This guide will walk you through deploying **CarePlus HMS** to [Vercel](https://vercel.com/) with zero hassle.

---

## 📁 What Has Been Prepared

1. **`vercel.json`**: Configures the `@vercel/python` serverless runtime, static asset caching for `/static/*` via Vercel Edge CDN, and WSGI routing to `api/index.py`.
2. **`api/index.py`**: Serverless WSGI entrypoint with auto-initialization that sets up database tables and demo seed data automatically on cold start.
3. **`.vercelignore`**: Prevents unnecessary local environments (`.venv`), tests, and caches from bloating the deployment bundle.
4. **`config.py`**: Smart database URI resolver supporting:
   - External PostgreSQL (Neon, Supabase, Vercel Postgres, AWS RDS) via `DATABASE_URL` or `POSTGRES_URL`.
   - Automatic `postgres://` to `postgresql://` string normalization required by SQLAlchemy 2.0+.
   - Fallback to ephemeral `/tmp/careplus.db` in serverless environments for instant zero-configuration previews.

---

## 🌟 Method 1: Deploy via GitHub & Vercel Dashboard (Recommended)

### Step 1: Push Code to GitHub
```bash
git init
git add .
git commit -m "Ready for Vercel deployment"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/careplus-hms.git
git push -u origin main
```

### Step 2: Import Project on Vercel
1. Go to [vercel.com](https://vercel.com/) and log in.
2. Click **Add New...** -> **Project**.
3. Select your `careplus-hms` repository from GitHub.
4. Framework Preset: Leave as **Other**.
5. Root Directory: `./` (leave default).

### Step 3: Configure Environment Variables (Optional but Recommended)
Under **Environment Variables**, you can add:
- `SECRET_KEY`: Any random secure string (e.g. `careplus-secret-prod-2026!`)
- `FLASK_ENV`: `production`
- `DATABASE_URL`: *(Recommended for production)* Your external PostgreSQL database connection URI from **Neon**, **Supabase**, or **Vercel Postgres**. *(If omitted, the app will run with pre-seeded demonstration data using the serverless SQLite fallback).*

### Step 4: Deploy!
- Click **Deploy**.
- Vercel will build and launch your hospital management system with a live public URL (e.g., `https://careplus-hms.vercel.app`).

---

## ⚡ Method 2: Deploy via Vercel CLI

1. **Install Vercel CLI globally**:
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy from project root**:
   ```bash
   vercel
   ```
   Follow the prompts in your terminal:
   - Set up and deploy? `Y`
   - Which scope? `[Your Account]`
   - Link to existing project? `N`
   - What's your project's name? `careplus-hms`
   - In which directory is your code located? `./`
   - Want to modify settings? `N`

4. **Deploy to Production**:
   ```bash
   vercel --prod
   ```

---

## 🗄️ Recommended Free Cloud PostgreSQL Databases

For persistent production storage across serverless requests, create a free database and set the `DATABASE_URL` environment variable in Vercel:

| Provider | Free Tier | Setup Time | URL Format |
| :--- | :--- | :--- | :--- |
| **[Neon.tech](https://neon.tech/)** | 0.5 GB Storage (Serverless Postgres) | ~1 min | `postgresql://user:password@ep-xyz.neon.tech/neondb?sslmode=require` |
| **[Supabase](https://supabase.com/)** | 500 MB PostgreSQL | ~2 mins | `postgresql://postgres:password@db.xyz.supabase.co:5432/postgres` |
| **[Vercel Postgres](https://vercel.com/docs/storage/vercel-postgres)** | Integrated in Vercel | ~1 min | `POSTGRES_URL` (Auto-configured by Vercel) |

---

## 🔑 Pre-Configured Demo Logins

Once deployed, you can immediately log in with any of these pre-configured accounts:

| Role | Email | Password |
| :--- | :--- | :--- |
| **Super Admin** | `admin@careplus.com` | `Admin@123` |
| **Hospital Admin** | `hospital.admin@careplus.com` | `Admin@123` |
| **Doctor** | `doctor@careplus.com` | `Doctor@123` |
| **Nurse** | `nurse@careplus.com` | `Nurse@123` |
| **Receptionist** | `reception@careplus.com` | `Reception@123` |
| **Pharmacist** | `pharmacy@careplus.com` | `Pharmacy@123` |
| **Lab Technician** | `lab@careplus.com` | `Lab@123` |
| **Accountant** | `accountant@careplus.com` | `Accountant@123` |
