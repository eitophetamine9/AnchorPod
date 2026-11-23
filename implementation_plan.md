# AnchorPod: Final Project Incremental Audit & Implementation Plan

**Course**: CSIT327 — Information Management 2  
**Instructor**: Joemarie C. Amparo  
**Project**: AnchorPod (Student Wellness & Anonymous 5-Member Micro-Community)  
**Architecture**: Django Vertical Slices (Package-by-Feature) + Supabase Cloud PostgreSQL  
**Current Branch**: `main`  
**Latest Commit**: `fd2ac6f` (`feat(pods): refine SQL joins and subqueries view with client-facing presentation`)

---

## 1. Executive Summary & Current Project Health

AnchorPod is currently in a healthy, production-grade state. All 14 physical ERD tables are active and migrated in hosted Supabase PostgreSQL, all vertical slices are registered, and unit test suites across all apps are passing cleanly (12/12 in `pods`, 11/11 in `nudges`, 7/7 in `home`, etc.).

Recently completed milestones:
1. **Foundational Architecture**: Auth, Profiles with Pillow avatar cropping, User Settings with DB persistence, Daily Check-Ins, 5-member Pods with simulated peers, and Self-Care Habit checklist.
2. **November 16 Monitoring Features**:
   - Interactive Pod Matching & Onboarding (`/pod/match/`)
   - Encouragement Vault & Nudge Archive (`/nudges/vault/`)
   - Custom Branded 404 & 500 Error Pages (`404.html`, `500.html`)
3. **SQL Joins & Subqueries Guided Implementation**:
   - Live Relational Roster (Multi-table `INNER JOIN` & `LEFT OUTER JOIN` via `select_related`)
   - Daily Check-In Status (Nested `WHERE user_id IN (SELECT ...)` via `Subquery`)
   - Automated clean SQL indentation via `sqlparse`
   - Supabase PostgreSQL schema verification queries

---

## 2. Comprehensive Feature Audit & Gap Analysis

Based on the approved Physical ERD, the project `README.md` roadmap, and standard Information Management final project evaluation criteria, here is the audit of what is complete versus what is missing or can be extended:

| Feature / Module | Status | Tables Utilized | Notes / Gap Analysis |
| :--- | :---: | :--- | :--- |
| **User Authentication & Registration** | Complete | `auth_user`, `profile_profile`, `user_settings` | Campus email validation, auto profile creation. |
| **Profile & Avatar Processing** | Complete | `profile_profile` | Center-square cropping, EXIF rotation, anonymous initials. |
| **User Settings & Theme Persistence** | Complete | `user_settings_usersettings` | Dark mode, notification flags, dirty state banner. |
| **Daily Attendance & Streak Tracker** | Complete | `home_dailycheckin`, `pod_streak`, `pod_daily_summary` | Dynamic streak increments, 7-day calendar, progress ring. |
| **Interactive Self-Care Goals Engine** | Mostly Complete | `goal_selfcaregoal`, `goal_dailycompletion` | Create, toggle checkoffs, and delete work via AJAX. *Missing: habit editing and category tabs.* |
| **Anonymous Nudge System** | Complete | `nudge_template`, `nudge_nudge` | Anti-bullying pre-approved templates, modals, notifications. |
| **Encouragement Vault (Archive)** | Complete | `nudge_nudge`, `nudge_template`, `profile_profile` | Chronological archive, sender badges, empty states. |
| **Pod Allocation & Roster** | Complete | `pod_pod`, `pod_membership` | 5-member capacity enforcement, automated demo peer seeding. |
| **Pod Matching & Schedule Alignment** | Complete | `pod_matching_preference`, `pod_pod`, `pod_membership` | Matchmaking workflow, timezone selection, pod reassignment. |
| **SQL Joins & Subqueries Inspector** | Complete | `pod_membership`, `auth_user`, `profile_profile`, `home_dailycheckin` | Live ORM query execution, formatted SQL, Supabase sync. |
| **Custom Branded Error Pages** | Complete | Static / Handlers | 404 and 500 handlers bound in `anchorpod/urls.py`. |
| **Dead Pod Reshuffle Worker** | **Missing** | `pod_reshuffle_log`, `pod_membership`, `pod_pod` | Listed in README roadmap. Currently, reshuffle is only triggered manually during preference update; no automated/scheduled inactive member rotation exists. |
| **Pod Journey History / Reshuffle Log View** | **Missing** | `pod_reshuffle_log` | Records are written to `pod_reshuffle_log`, but there is no student or admin UI to view transition history. |
| **Student Habit Consistency Report (Export)** | **Missing** | `home_dailycheckin`, `goal_dailycompletion`, `pod_streak` | Common academic requirement: exporting attendance/habits to CSV or printable summary. |
| **Account Password Change** | **Missing** | `auth_user` | User settings lacks a standard password change view. |
| **Demo Data Seeding Command** | **Missing** | All tables | Management command (`manage.py seed_data`) to quickly populate sample data on fresh setups. |

---

## 3. Prioritized Incremental Feature Candidates

If you want to add further features for the final project submission, here are the top 4 recommended incremental features ranked by impact and alignment with the course rubric:

### Priority 1: Automated Inactive Member Reshuffle Routine (`pod_reshuffle_log`)
* **What it does**: Implements the unfinished roadmap feature from the README. A service function and Django management command (`python manage.py run_pod_reshuffle`) that:
  1. Identifies pod members with no check-in for 3+ consecutive days.
  2. Flags their membership as `inactive` or `reassigned`.
  3. Records the transition in `pod_reshuffle_log` with reason `"Inactivity auto-rotation (3+ days)"`.
  4. Fills the vacancy with an active student seeking a pod or an active simulated peer.
* **Database Value**: 100% closes out the intended purpose of the `pod_reshuffle_log` table.
* **Estimated effort**: Low–Medium (1 service function, 1 management command, unit tests).

### Priority 2: Pod Journey History / Reshuffle Log Interface (`/pod/history/`)
* **What it does**: A dedicated history section or modal in **My Pod** displaying the student's journey timeline:
  - Date joined the current pod.
  - Previous pod reallocations and schedule shifts from `pod_reshuffle_log`.
  - Milestones reached (e.g. 7-day collective pod streak).
* **Database Value**: Directly queries `pod_reshuffle_log` via foreign keys to display historical audit records.
* **Estimated effort**: Low (1 view, 1 template partial or page, 1 test).

### Priority 3: Habit Consistency CSV / Report Export (`/goals/export/`)
* **What it does**: Adds an **"Export Consistency Report"** button on the Dashboard or Goals section:
  - Generates a downloadable CSV report of the student's check-in dates, daily habits completed, and pod streak milestones.
  - Uses Django's streaming `csv.writer` response.
* **Database Value**: Demonstrates aggregated reporting and file generation from PostgreSQL data.
* **Estimated effort**: Low (1 view endpoint, 1 test, 1 UI button).

### Priority 4: Goal Category Filtering & Inline Editing (`apps/goals`)
* **What it does**:
  - Adds interactive category filter pills (`All`, `Physical`, `Mindfulness`, `Academic`) on the home dashboard habit list.
  - Allows editing the title of an existing custom habit without having to delete and re-create it.
* **Database Value**: Completes the full CRUD cycle for `SelfCareGoal`.
* **Estimated effort**: Low (1 update view, small JavaScript filter enhancement).

---

## 4. Current Status Checklist

- [x] All 14 physical tables migrated and working in Supabase PostgreSQL
- [x] Vertical slice packaging across 8 feature apps
- [x] Authentication & Profile management
- [x] 5-member Pod allocation, matching engine, and streaks
- [x] Goal tracking with asynchronous checkoffs
- [x] Anonymous pre-approved nudges & Encouragement Vault
- [x] SQL Joins & Subqueries inspection page with clean indentation
- [x] Custom 404 & 500 error pages
- [x] Dead Pod Reshuffle Worker (`apps.pods.services.run_pod_reshuffle`)
- [x] Pod Journey History View (`/pod/history/`)
- [x] Habit Consistency CSV Report Export (`/goals/export/`)
- [x] Goal Category Filter / Inline Edit (`apps/goals`)
- [x] Performance Optimization Middleware (`anchorpod.middleware.UserPrefetchMiddleware`)
- [x] Optimistic UI Instant Habit Checkoffs (`static/js/home/home.js`)
