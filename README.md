# AnchorPod

> **A community-driven, anonymous accountability platform designed to combat academic burnout and student isolation through shared daily self-care rhythms.**

[![Django](https://img.shields.io/badge/Django-6.0-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.14-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)](https://supabase.com/)
[![Architecture](https://img.shields.io/badge/Architecture-Vertical%20Slicing-blueviolet?style=for-the-badge)](#architecture--vertical-slicing)

---

## Overview

Depression and academic burnout heavily isolate students during demanding semesters, making even basic daily self-care tasks feel completely overwhelming. Standard habit trackers rely purely on solitary intrinsic motivation, which is often the first thing to disappear under intense stress.

**AnchorPod** solves this by grouping students into **anonymous pods of 5**. Rather than facing isolated pressure, students check in daily with small, achievable self-care goals while a backend tracks the pod's collective rhythm. To eliminate cyberbullying, social anxiety, and trauma dumping, the platform completely excludes free-text chat—restricting peer interaction strictly to anonymous, pre-approved positive nudges.

---

## Architecture — Vertical Slicing

This application is built in strict adherence to the **CSIT327 Vertical Slicing Architecture (Package-by-Feature)**. Instead of organizing code horizontally by technical layers (controllers, models, views), every business capability is encapsulated as an independent Django feature app:

```text
AnchorPod/
├── manage.py
├── models.py                     # Consolidated master model definitions (Submission Reference)
├── requirements.txt              # Production & dev dependencies
├── anchorpod/                    # Project-level configuration & routing
│   ├── settings.py               # Configured for vertical apps, dotenv, and Supabase DATABASE_URL
│   ├── urls.py                   # Feature routing & development media serving
│   ├── asgi.py
│   └── wsgi.py
├── apps/                         # Feature Apps (Vertical Slices)
│   ├── login/                    # Authentication, login views, logout views, and test cases
│   ├── register/                 # Account registration & profile initialization slice
│   ├── home/                     # Main dashboard, daily attendance check-in, and streak UI
│   ├── profile/                  # Anonymous identity, circular avatar processing, and bio
│   ├── user_settings/            # Dark mode & notification preference toggles
│   ├── pods/                     # 5-member pods, matching engine, streaks & summaries
│   ├── goals/                    # Granular self-care habit items & daily completion logs
│   └── nudges/                   # Pre-approved positive encouragement messaging
├── templates/                    # HTML partitioned strictly by feature
│   ├── base.html                 # Shared layout, header navigation, mini-avatar, theme script
│   ├── login/login.html
│   ├── register/register.html
│   ├── home/home.html
│   ├── profile/profile.html
│   └── user_settings/settings.html
├── static/                       # Feature-partitioned static assets
│   ├── css/ (site.css, login/, register/, home/, profile/, user_settings/)
│   ├── js/  (login/, register/, home/, profile/, user_settings/)
│   └── images/
└── media/                        # User-uploaded content (auto-cropped avatars under media/profile/)
```

---

## Live & Implemented Features

### 1. Account Authentication (`apps/login`, `apps/register`)
* Student registration enforced with institutional email validation to maintain a closed campus community.
* Secure authentication, session management, and logout with automatic initialization of linked `Profile` and `UserSettings` records.

### 2. Anonymous Pod Profile & Identity (`apps/profile`)
* **Anonymous Pseudonyms**: Students choose anonymous handles (e.g. `Anchor Fox`, `Climate Change`) displayed to pod peers. Real full names remain strictly private.
* **Color Palettes**: Curated accent color swatches for anonymous avatar badges.
* **Profile Picture Upload**:
  * Real-time client-side preview via JavaScript `FileReader`.
  * Server-side image processing via **Pillow**: smartphone EXIF auto-rotation, 1:1 center-square cropping, and Lanczos downscaling to a maximum of 400×400 px (~30–60 KB).
  * Photo removal toggle to seamlessly revert back to anonymous colored initials.

### 3. User Settings & Dark Theme (`apps/user_settings`)
* **Database-Persisted Preferences**: Dark theme and notification preferences stored in Supabase PostgreSQL (eliminates theme leaks across browser tabs).
* **Unsaved Preferences Protection**: Real-time dirty-state tracking with an animated warning banner and `beforeunload` navigation guards to alert students of uncommitted changes.
* **Solid Slate Dark Theme**: Custom dark palette (`#121818`) with warm paper accents and high-contrast typography.

### 4. Daily Attendance Check-In (`apps/home`)
* "Check in with my pod" one-click action logging directly to `home_dailycheckin` with composite unique constraints preventing duplicate daily submissions.
* Adaptive navigation showing the student's mini-avatar thumbnail and active status across all authenticated pages.

### 5. Supabase PostgreSQL Cloud Integration
* Connected to hosted **Supabase PostgreSQL** via AWS Tokyo Session Pooler with SSL encryption.
* All **14 physical ERD tables** migrated and live in the public schema.
* Comprehensive automated test suite with **16 passing unit tests**.

---

## Features in Active Development (Roadmap)

The complete database schema for these features is already created and migrated in Supabase. The business logic and user interfaces are currently in active development:

- [ ] **Pod Matching Engine (`apps/pods`)**:
  * Python matchmaking algorithm utilizing sets and arrays to group solitary students into balanced pods of 5 based on shared activity windows (`pod_matching_preference`).
- [ ] **Collective Streak Calculation (`pod_streak`, `pod_daily_summary`)**:
  * Backend logic that evaluates attendance across all 5 pod members, incrementing the group streak counter only when every member completes their daily check-in.
- [ ] **Anonymous Nudge System (`apps/nudges`)**:
  * Modal interface enabling students to send pre-approved positive encouragement notifications (`nudge_template`) to pod members who have not yet checked in for the day.
- [ ] **Interactive Granular Goals (`apps/goals`)**:
  * Expanding static checklists into dynamic interactive daily goals with per-day completion tracking (`goal_dailycompletion`) via AJAX/Fetch API.
- [ ] **Dead Pod Reshuffle Worker (`pod_reshuffle_log`)**:
  * Background routine to detect abandoned accounts (e.g. 3+ days inactive) and merge active solitary students into healthy pods.

---

## Database Schema (Physical ERD Summary)

The application uses 14 normalized tables hosted on Supabase PostgreSQL:

```text
auth_user (1) ────────── (1) profile_profile
auth_user (1) ────────── (1) user_settings_usersettings
auth_user (1) ────────── (0..1) pod_matching_preference
auth_user (1) ────────── (N) home_dailycheckin
auth_user (1) ────────── (N) pod_membership (N) ────────── (1) pod_pod
auth_user (1) ────────── (N) goal_selfcaregoal (1) ─────── (N) goal_dailycompletion
auth_user (1) ────────── (N) nudge_nudge (N) ───────────── (1) nudge_template
pod_pod   (1) ────────── (1) pod_streak
pod_pod   (1) ────────── (N) pod_daily_summary
pod_pod   (1) ────────── (N) pod_reshuffle_log
```

A complete master models reference is available in [`models.py`](models.py).

---

## Local Development Setup

### Prerequisites
* Python 3.12+ (tested on Python 3.14)
* Git
* A Supabase project or local PostgreSQL instance

### 1. Clone the Repository
```bash
git clone https://github.com/eitophetamine9/AnchorPod.git
cd AnchorPod
```

### 2. Create and Activate Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the project root:
```ini
DATABASE_URL=postgresql://postgres.[PROJECT-REF]:[YOUR_PASSWORD]@[POOLER-HOST]:5432/postgres
SECRET_KEY=your-django-secret-key
DEBUG=True
```

### 5. Run Database Migrations
```bash
python manage.py migrate
```

### 6. Run the Test Suite
```bash
python manage.py test --keepdb
```

### 7. Start the Development Server
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000` in your browser.

---

## Testing

AnchorPod includes automated test cases across all vertical slices:
```bash
# Run all tests
python manage.py test --keepdb

# Run tests for a specific feature app
python manage.py test apps.profile --keepdb
python manage.py test apps.home --keepdb
```

---

## Course & Academic Metadata

* **Course**: CSIT327 — Information Management 2
* **Instructor**: Joemarie C. Amparo
* **Topic**: Django Vertical Slicing Architecture & Supabase Cloud PostgreSQL Integration
* **Student Author**: [eitophetamine9](https://github.com/eitophetamine9)

