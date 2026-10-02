# AnchorPod — Complete Project Context & Current State Summary

> **Instructions for the Next AI Instance**:
> Read this document to understand the full background, architecture, database setup, and current status of **AnchorPod**. You are continuing work on this codebase. Adhere strictly to the established **CSIT327 Vertical Slicing Architecture**, keep tests passing, and maintain clean Supabase PostgreSQL synchronization.

---

## 1. Project Overview & Business Domain

* **Project Name**: AnchorPod
* **Course**: CSIT327 (Django Web Development + Supabase PostgreSQL Integration)
* **Instructor**: Joemarie Comeros Amparo
* **Core Problem**: Academic burnout isolates university students, making basic daily self-care difficult.
* **Core Solution**: An anonymous group accountability web application. Students are grouped into pods of 5 based on preferred check-in schedules. The backend tracks collective pod streaks, displays a shared daily progress ring, provides daily self-care goal checklists, and allows anonymous pre-set positive "nudges" (preventing cyberbullying by disallowing free-text chat).

---

## 2. Architectural Paradigm: Django Vertical Slicing

The project was migrated from a legacy monolithic `core/` package into **Vertical Slicing (Package-by-Feature)** as mandated by the course syllabus:

```text
AnchorPod/
├── manage.py
├── models.py                     # Consolidated master Django models (Submission File)
├── requirements.txt              # django, psycopg[binary], dj-database-url, python-dotenv, Pillow
├── .env                          # Holds live Supabase DATABASE_URL and SECRET_KEY (git-ignored)
├── anchorpod/
│   ├── settings.py               # Configured with dj_database_url, media paths, INSTALLED_APPS
│   ├── urls.py                   # Root URLconf routing to feature apps + static media serving
│   ├── asgi.py
│   └── wsgi.py
├── apps/                         # ALL Python application code partitioned by business feature
│   ├── login/                    # Login & Logout authentication slice
│   ├── register/                 # Student registration & account initialization slice
│   ├── home/                     # Main dashboard, daily attendance & check-ins
│   ├── profile/                  # Anonymous identity, avatar image, bio, goals
│   ├── user_settings/            # Dark mode & notification preference toggles
│   ├── pods/                     # 5-member pods, matching engine, streaks & summaries
│   ├── goals/                    # Granular self-care habit items & daily completion logs
│   └── nudges/                   # Pre-approved positive encouragement messaging
├── templates/                    # HTML partitioned strictly by feature
│   ├── base.html                 # Global shell, navigation bar, mini-avatar, theme script
│   ├── login/login.html
│   ├── register/register.html
│   ├── home/home.html
│   ├── profile/profile.html
│   └── user_settings/settings.html
├── static/                       # Static assets partitioned strictly by type and feature
│   ├── css/ (site.css, login/, register/, home/, profile/, user_settings/)
│   ├── js/  (login/, register/, home/, profile/, user_settings/)
│   └── images/
└── media/                        # User-uploaded content (auto-cropped avatars under media/profile/)
```

---

## 3. Technology Stack & Database Configuration

* **Backend**: Python 3.14 + Django 6.x
* **Database Driver**: `psycopg` (v3) + `dj-database-url`
* **Production Database**: Hosted **Supabase PostgreSQL** via Session Pooler:
  * Host: `aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres` (Tokyo Region)
  * Configured via `DATABASE_URL` in `.env` with SSL enabled.
* **Image Processing**: `Pillow` (v12.3.0) for server-side auto-rotation (EXIF), 1:1 center-square cropping, and Lanczos downscaling to max 400×400 px.
* **Design & Theme**: Vanilla CSS with custom color tokens (warm paper background, coral accents `#ef8360`, teal accents, and `#121818` solid dark theme).

---

## 4. Full Physical ERD Mapping (14 Database Tables)

All 14 entities identified in the approved Physical ERD are mapped to Django models with explicit `db_table` names matching the database schema:

| Table Name in Supabase | Django Model | App Location | Purpose / Relationships |
| :--- | :--- | :--- | :--- |
| **`auth_user`** | `User` | `django.contrib.auth` | Student university email (`UNIQUE`), password hash, account flags. |
| **`profile_profile`** | `Profile` | `apps.profile` | `user` (`1:1`), nickname, bio, avatar color, profile image path, goals JSONB. |
| **`user_settings_usersettings`** | `UserSettings` | `apps.user_settings` | `user` (`1:1`), dark mode boolean, email notifications, nudge opt-in. |
| **`home_dailycheckin`** | `DailyCheckIn` | `apps.home` | `user` (`FK`), check-in calendar date, completed flag. `UNIQUE(user, date)`. |
| **`pod_pod`** | `Pod` | `apps.pods` | Pod name, time slot cadence, capacity (5), status (`forming`, `active`, `archived`). |
| **`pod_membership`** | `PodMembership` | `apps.pods` | `user` (`FK`), `pod` (`FK`), role, membership status (`active`, `inactive`, `reassigned`). |
| **`pod_matching_preference`** | `PodMatchingPreference`| `apps.pods` | `user` (`1:1`), preferred time slot, timezone, queue flag for Python matching engine. |
| **`pod_streak`** | `PodStreak` | `apps.pods` | `pod` (`1:1`), consecutive days all members checked in, longest streak. |
| **`pod_daily_summary`** | `PodDailySummary` | `apps.pods` | `pod` (`FK`), date, checked-in count, total members, streak incremented flag. `UNIQUE(pod, date)`. |
| **`goal_selfcaregoal`** | `SelfCareGoal` | `apps.goals` | `user` (`FK`), title, category (`physical`, `mindfulness`, etc.), active toggle, order. |
| **`goal_dailycompletion`** | `DailyGoalCompletion` | `apps.goals` | `goal` (`FK`), `user` (`FK`), date, completed boolean. `UNIQUE(goal, user, date)`. |
| **`nudge_template`** | `NudgeTemplate` | `apps.nudges` | Pre-approved positive phrases (prevents free-text bullying), category. |
| **`nudge_nudge`** | `Nudge` | `apps.nudges` | `pod` (`FK`), `sender` (`FK`), `recipient` (`FK`), `template` (`FK`), date, is_read. |
| **`pod_reshuffle_log`** | `PodReshuffleLog` | `apps.pods` | `user` (`FK`), `old_pod` (`FK`), `new_pod` (`FK`), reallocation reason. |

---

## 5. Key Bug Fixes & Architectural Decisions Already Solved

1. **Supabase Pooler Resolution**:
   Direct host `db.<ref>.supabase.co:5432` times out on IPv4 networks. The project uses the **Session Pooler** (`postgres.<ref>@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres`), which connects reliably.
2. **Dark Mode Leak Across Tabs**:
   Removed uncommitted `localStorage` mutations from `templates/base.html` that leaked unpersisted theme toggles across tabs. Only saved database preferences in `user_settings_usersettings` dictate the active theme. Added dirty-state tracking, unsaved warning banner, and `beforeunload` navigation interceptors.
3. **Radial Gradient Artifact in Dark Mode**:
   Fixed an unwanted light radial blur in the top right by adding `background: #121818 !important; background-image: none !important;` to `body.dark-theme` and `html.dark-theme` in `static/css/site.css`.
4. **Profile Image Auto-Scaling & Overflow Prevention**:
   Large uploaded images previously blew out the navigation bar due to missing intrinsic constraints. Fixed by:
   - Server-side image processing in `apps/profile/views.py` (`process_profile_image`) using Pillow to auto-orient EXIF, center-crop to 1:1, downscale to max 400×400 px, and compress.
   - Enforcing strict HTML attributes (`width="28" height="28"`), inline style constraints (`object-fit: cover; border-radius: 50%; flex-shrink: 0;`), and `!important` CSS rules on `.mini-nav-avatar` and `.avatar.avatar-img`.
   - Adding cache-busting `?v=1.2` to `site.css` in `templates/base.html`.

---

## 6. Current State & Verification Status

* **Django System Check**: `python manage.py check` $\rightarrow$ **0 issues**.
* **Database Migrations**: All migrations (`goals.0001`, `home.0002`, `pods.0001`, `nudges.0001`, `profile.0002`, `user_settings.0002`) are **applied and verified live in Supabase**.
* **Automated Test Suite**: All **16 tests pass** with `python manage.py test --keepdb` (covering authentication, profile CRUD, avatar upload/downscaling, settings persistence, daily check-ins, and legacy route compatibility).
* **Consolidated Submission File**: `c:\Users\Erick\Documents\AnchorPod\models.py` contains the complete master model definitions ready for classroom submission.

---

## 7. Immediate Next Steps / Roadmap

1. **Submission Phase**: Capture the Supabase Table Editor screenshot showing the resulting tables, and submit alongside `models.py`.
2. **Feature Implementation Phase**:
   - Build UI and views for **`apps/pods`** (displaying pod membership, group streak badge, and the Python pod matching engine algorithm using sets/arrays).
   - Build the modal and dispatch views for **`apps/nudges`** (enabling students to click "Send a nudge" on inactive pod peers to trigger pre-approved template notifications).
   - Expand the daily checklist in **`apps/goals`** to allow interactive daily checkoffs linked to `DailyGoalCompletion`.
