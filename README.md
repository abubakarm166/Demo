# Operator MVP Demo Deployment

This repository now ships with a **demo-friendly build** of the Operator MVP Django project.
It showcases the product without hitting paid services, requiring authentication, or touching Stripe.

## Key Demo Behaviours
- `/` serves the marketing homepage.
- `/demo` renders the chat interface (same visuals as production, but no login required).
- `/api/coach/` returns an instant canned JSON response:
  ```json
  { "message": "Hi there! This is a demo response." }
  ```
- No sign-up, login, or payment controls are shown anywhere in the UI.
- All OpenAI/Stripe integrations have been removed from the runtime code path.

## Local Quick Start
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` for the homepage and `http://127.0.0.1:8000/demo/` for the chat demo.

## Deploying on a Free Tier (Render Example)
1. Push this repo to GitHub/GitLab.
2. Create a **Render Web Service** and connect the repo.
3. Set the build & start commands:
   - Build: `pip install -r requirements.txt`
   - Start: `gunicorn core.wsgi`
4. Configure environment variables:
   - `DEBUG=false`
   - `DEMO_MODE=true`
   - `ALLOWED_HOSTS=your-app.onrender.com`
   - `CSRF_TRUSTED_ORIGINS=https://your-app.onrender.com`
   - Leave all API keys empty — they’re not needed for the demo.
5. Enable `STATIC_URL` handling (Render does this automatically with Whitenoise).
6. Deploy. After the first successful build, note the public URL and share it as the live demo link.

## Switching Back to Full Mode
Toggle these environment variables and re-deploy:

| Feature           | Demo Setting | Production Setting | Notes |
|-------------------|--------------|--------------------|-------|
| Authentication     | `ENABLE_AUTH=false`  | `ENABLE_AUTH=true` | Restore login/signup templates and URLs. |
| Stripe             | `ENABLE_REAL_PAYMENTS=false` | `ENABLE_REAL_PAYMENTS=true` | Requires Stripe keys and price IDs. |
| OpenAI Chat        | `ENABLE_REAL_CHAT=false` | `ENABLE_REAL_CHAT=true` | Requires `OPENAI_API_KEY`. |

(Additional instructions for reinstating full functionality are kept in the original code comments.)

## Acceptance Checklist
- ✅ `/` homepage loads.
- ✅ `/demo` shows the chat experience.
- ✅ `/api/coach/` responds instantly with mock JSON.
- ✅ UI hides login, signup, and payment actions.
- ✅ No outbound OpenAI or Stripe requests occur.
- ✅ Runs comfortably on Render/Railway free tiers.

## Live Demo URL
_Add the deployed link here once you publish to a hosting provider._

Need help or want to extend the demo? Drop a note in the repo issues — happy to assist.

