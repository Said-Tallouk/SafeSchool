# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Backend (Django)
```bash
python manage.py runserver          # Start dev server at http://localhost:8000
python manage.py makemigrations     # Generate migrations after model changes
python manage.py migrate            # Apply migrations
python manage.py createsuperuser    # Create admin user
python manage.py test_email         # Custom command: verify Gmail SMTP config
```

### Frontend (Vue 3 + Vite)
```bash
cd frontend
npm install
npm run dev     # http://localhost:5173 (proxies /api and /media to :8000)
npm run build   # Output to frontend/dist/
```

Run both concurrently during development (Django on :8000, Vite on :5173).

### No automated tests exist in this project.

## Architecture

**SafeSchool v2** is a school safety incident-reporting platform for Moroccan schools (Arabic UI). Django REST Framework backend + Vue 3 SPA frontend.

### Backend: Django apps

- **`accounts/`** — Custom `AbstractUser` (`accounts.User`) with `role` field (`directeur`, `conseiller`, `etudiant`), plus `telephone`, `classe`, `photo`, `identifiant`, `must_change_password` fields. Handles login, register, JWT issue, 3-step password reset (forgot → verify 6-digit code → reset), and profile update. Auth endpoints at `/api/auth/`.
- **`api/`** — All core models and REST endpoints at `/api/`. Two custom DRF permission classes (`IsDirecteur`, `IsConseiller`) are defined here; other views do inline `request.user.role` checks.
- **`core/`** — Empty placeholder app (no URLs, no models in use).

### Models (api/models.py)

| Model | Key fields / notes |
|---|---|
| `Counselor` | OneToOne → User; enforced limits: max 1 male, max 2 female (checked in view, not model) |
| `Report` | FK student + FK counselor; `numero_dossier` auto-incremented on first save; `is_anonymous` hides student name |
| `Appointment` | OneToOne → Report; statuses: مقترح / مقبول / مرفوض. Counselor can overwrite by deleting + recreating |
| `StudentSchedule` | OneToOne → Report; student uploads a file after appointment rejection so counselor can reschedule |
| `SessionReport` | OneToOne → Report; counselor fills this to mark case resolved (sets status → تم الحل) |
| `Annonce` | Published/unpublished announcements; unauthenticated users only see `publie=True` |
| `Activite` | School activities (planifiee / en_cours / terminee / annulee) |
| `Photo` | Gallery images grouped by category (professeurs / activites / accueil) with optional subject tag |
| `Notification` | Push notifications per user; created server-side by `push_notif()` helper |
| `SiteContent` | Key-value CMS; POST accepts a list for bulk upsert |

### Report Status Workflow
```
جديد (New) → قيد المعالجة (Processing) → موعد محدد (Appointment Set) → تم الحل (Resolved)
```
Rejection of an appointment sends the status back to قيد المعالجة.

### Frontend: Role-based SPA

- **Layouts**: `DirecteurLayout`, `ConseillerLayout`, `EtudiantLayout`, `PublicLayout` — each wraps its role's routes
- **Route namespaces**: `/directeur/*`, `/conseiller/*`, `/etudiant/*`, plus public pages under `/`
- **Route guard** (`src/router/index.js`): reads `localStorage['user']`; redirects unauthenticated users to `/login`, role mismatches to the correct dashboard, and students with `must_change_password=true` to `/etudiant/change-password`
- **Pinia stores**: `auth` (user/tokens), `reports` (list + stats), `counselors`, `notifications`
- **Axios** (`src/api/index.js`): attaches `Bearer` token; on 401 attempts a single token refresh via `/api/auth/token/refresh/`, then clears localStorage and redirects to `/` on failure
- **PDF export**: `src/utils/pdf.js` uses html2canvas for report printing

### Key Non-Obvious Behaviors

- **Stats polling**: `App.vue` calls `/api/stats/` every 30 seconds to drive toast notifications for new reports/assignments — intentional.
- **Student usernames**: formatted as `{identifiant}@safeschool.ma`; bulk-imported students get `must_change_password=True` and a generated 10-char password.
- **Student bulk import**: `POST /api/students/import/` accepts CSV or Excel; validates niveau (1APIC/2APIC/3APIC) and classe number (1–10); supports `replace_all=1` to wipe all students first.
- **Appointment re-creation**: existing appointment is deleted before a new one is saved — there is always at most one per report.
- **Email**: Gmail SMTP via App Password (port 465, SSL). All sends use `fail_silently=True`; failures log to stderr and do not block the response. The `safe_send_mail()` wrapper returns `True/False`.
- **Media URLs**: serializers call `request.build_absolute_uri()` for media fields; Vite proxies `/media/` to Django in dev.
- **Photo deletion**: `PhotoDetailView.delete` calls `photo.image.delete(save=False)` to remove the physical file before deleting the DB record.

## Configuration

`.env` file required at project root:
```
SECRET_KEY=...
EMAIL_SENDER=...@gmail.com
EMAIL_PASSWORD=...        # Google App Password (16 chars), not the regular password
DB_NAME=safeschool        # MySQL database name
DB_USER=root
DB_PASSWORD=
DB_HOST=127.0.0.1
DB_PORT=3306
```

Key `settings.py` values: MySQL via `pymysql`, `DEBUG=True`, `ALLOWED_HOSTS=['*']`, JWT access token 8h / refresh 7d, `TIME_ZONE='Africa/Casablanca'`, `LANGUAGE_CODE='ar'`.

CORS is whitelisted for Vite dev ports 5173–5176. Vite also proxies `/api` and `/media` to `http://127.0.0.1:8000`.
