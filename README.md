# 🚀 RealityCheck - Goal Tracker App

A productivity-focused web application built with **FastAPI** that helps users manage goals, track progress, and stay consistent using a simple motivational system.

---

## 🧠 Overview

This app allows users to:
- create and manage goals (events)
- track progress (0–100%)
- monitor deadlines and overdue tasks
- analyze performance through stats and a level system

It’s designed as a **portfolio project** to demonstrate backend logic, database relationships, and UX thinking.

---

## 🔐 Authentication

- User registration & login
- JWT-based authentication
- Session handling for protected routes

<img width="957" height="422" alt="{B7DC0384-9DC1-4E0A-A83C-F6002C06DE92}" src="https://github.com/user-attachments/assets/4a5a590c-2966-457c-95ec-6262e7d43ed5" />


---

## 🏠 Main Dashboard

After logging in, the user lands on the main dashboard.

### Navbar includes:
- 🕒 Current time, date, and weekday
- 📊 Success rate (%)
- 🏆 Hall of Fame button
- 📌 Event counters:
  - Planned
  - Done
  - Failed
  - Replanned
  - Overdue
- 👤 Logged in user info
- 🎖 Rank + badge
- 🚪 Logout button

<img width="957" height="438" alt="{6B28206E-B514-4686-B2B5-BECA2B27299B}" src="https://github.com/user-attachments/assets/abf3f436-f90b-4d8b-8410-dc5029f85cf1" />


---

## 📋 Events System

### Event features:
- Title
- Description
- Tags (many-to-many)
- Progress bar (0–100%)
- Status:
  - `planned`
  - `replanned`
  - `done`
  - `failed`
  - `overdue`
- Due date + remaining days
- "NEW" badge (if created within 24h)

<img width="224" height="285" alt="{2929E9E2-2EAB-46B9-B5CB-B8066708C571}" src="https://github.com/user-attachments/assets/667e2672-8001-4aa2-aef9-57f254e9328d" />


---

### Actions:
- 👁 View event details
- ✏ Edit event
- ❌ Mark as failed (with failure note)
- 🔁 Replan failed events
- ✅ Mark as done (button or progress = 100%)

<img width="376" height="387" alt="{5FB71010-2419-42A6-90F1-2C613121E07E}" src="https://github.com/user-attachments/assets/5bd0aa70-1145-42c5-9814-fac8887a055a" />


---

## 🧩 Filtering & Sorting

### Filtering:
- Planned
- Done
- Failed
- Replanned
- Overdue
- All

### Sorting:
- Newest
- Oldest

<img width="920" height="93" alt="{4419BEFF-BBBA-4C43-80E4-E2E67181E47C}" src="https://github.com/user-attachments/assets/580f98ff-32fc-48eb-b805-87b2019b99b6" />


---

## ➕ Event Creation

- Form-based event creation
- Default due date (auto-set if not provided)
- Tag input as string → parsed into DB

<img width="960" height="439" alt="{90CE6A44-F7E7-482A-BDA2-E4C6E47710AF}" src="https://github.com/user-attachments/assets/0101c2e6-e7a1-47c1-895a-ea8acd9aa8c0" />


---

## 📉 Overdue System

- Automatic detection of overdue events
- Highlighted visually
- Counted in navbar
- Dedicated filter

<img width="272" height="292" alt="{B6361EB2-3F35-4394-90FD-4B80B9692108}" src="https://github.com/user-attachments/assets/e953c47d-15d5-4fce-b010-8436576f5616" />


---

## 🏆 Hall of Fame

A separate page showing:

- 🎖 User level (milestone system)
- 📈 Progress to next level
- ✅ Completed events list

<img width="958" height="435" alt="{D65FC0C3-0EE2-4860-B9CF-B5A4F745DABD}" src="https://github.com/user-attachments/assets/25f3eb39-af9b-4d73-9fc1-975cea06cdb9" />


---

## 📊 Progress & Motivation System

- Progress tracking per event
- Automatic status changes
- Success rate calculation
- Level system based on completed events

---

## 🗂 Event History Tracking

- Tracks changes in:
  - Progress
  - Status
- Stored in database for future extensibility

---

## 🛠 Tech Stack

### Backend
- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic

### Frontend
- Jinja2 Templates
- HTML5
- CSS (custom dark theme)

---

## ⚙️ How to Run

```bash
git clone https://github.com/ArktizML/realitycheck
cd https://github.com/ArktizML/realitycheck

python -m venv venv
venv\Scripts\activate   # Windows

pip install -r requirements.txt

alembic upgrade head

uvicorn app.main:app --reload
```
## 🎨 UI Style

- Dark theme
- Minimalist layout
- Midnight purple accents
- Card-based event system

---

## 📌 Project Purpose

This project was built to:
- practice backend development with FastAPI
- understand relational databases (many-to-many)
- implement real-world logic (status, progress, deadlines)
- demonstrate readiness for a **junior Python developer role**

---

## 🚧 Future Improvements

- Docker support
- Code refactor (modular services)
- Improved UI feedback (animations, tooltips)
- Extended analytics

---
