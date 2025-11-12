# Operator MVP Demo Deployment

This repository now ships with a **demo-friendly build** of the Operator MVP Django project.  
The goal is to provide a live, zero-risk showcase that looks and behaves like the production product while avoiding real authentication, payments, or API usage.

## What's Included
- Demo mode defaults (mock chat replies, no Stripe checkout, auth disabled).
- Toggleable settings to re-enable full functionality when needed.
- `.env.example` template with all configuration keys.
- Updated `requirements.txt` and Whitenoise-based static serving for hosting.
- Documentation for local setup and deployment.

## Quick Start (Demo Mode)
1. **Clone & install**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```
2. **Configure environment**
   ```bash
   copy .env.example .env
   ```
   (Adjust values as desired; defaults keep demo mode active.)
3. **Run the app**
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```
   Visit `http://127.0.0.1:8000/` to explore the demo.

## Deployment Guide
These instructions assume a platform such as **Render** or **Railway**:

1. Push this repository to a Git host (GitHub, GitLab, etc.).
2. Create a new web service and select the repo.
3. Pick the following build & run commands:
   - Build command: `pip install -r requirements.txt`
   - Run command: `gunicorn core.wsgi`
4. Add environment variables (copy from `.env.example`). For a demo:
   - `DEMO_MODE=true`
   - `ENABLE_AUTH=false`
   - `ENABLE_REAL_PAYMENTS=false`
   - `ENABLE_REAL_CHAT=false`
   - `ALLOWED_HOSTS=your-app.onrender.com`
   - `CSRF_TRUSTED_ORIGINS=https://your-app.onrender.com`
5. Enable persistent storage (optional) if you want the SQLite database to survive restarts.
6. Trigger the first deploy. Once live, collectstatic will run automatically thanks to Whitenoise.

### Switching to the Full Product
Flip the following environment variables:

| Purpose            | Demo Default | Full Product |
|--------------------|--------------|--------------|
| Authentication     | `ENABLE_AUTH=false`  | `ENABLE_AUTH=true` |
| Stripe Checkout    | `ENABLE_REAL_PAYMENTS=false` | `ENABLE_REAL_PAYMENTS=true` *(requires Stripe keys & price IDs)* |
| OpenAI Chat        | `ENABLE_REAL_CHAT=false` | `ENABLE_REAL_CHAT=true` *(requires `OPENAI_API_KEY`)* |
| Demo chat replies  | `DEMO_CHAT_RESPONSES` list | Update or unset for custom copy |

Make sure to add:
- `STRIPE_PUBLIC_KEY`, `STRIPE_SECRET_KEY`, `STRIPE_PRICE_ID_*`
- `OPENAI_API_KEY`
- Email SMTP configuration if password resets or notifications are needed.

## Feature Parity in Demo Mode
- **Chatbot** returns high-quality scripted responses derived from `DEMO_CHAT_RESPONSES`.
- **Pricing cards** render Stripe plan details but skip checkout.
- **Auth flows** are replaced with friendly notices to keep visitors focused on the product tour.

## Testing
Run the built-in Django test suite (coverage depends on existing tests):
```bash
python manage.py test
```

## Live Demo URL
> _Add your deployed link here once the service is live._

---
Need help or want to switch back to production mode? Toggle the environment variables, add your real keys, and redeploy—no code changes required.

