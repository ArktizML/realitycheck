# 🚀 Goal Tracker App

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

📸 SS soon

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

📸 SS soon

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
- Due date + remaining days
- "NEW" badge (if created within 24h)

---

### Actions:
- 👁 View event details
- ✏ Edit event
- ❌ Mark as failed (with failure note)
- 🔁 Replan failed events
- ✅ Mark as done (button or progress = 100%)

📸 SS soon

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

📸 SS soon

---

## ➕ Event Creation

- Form-based event creation
- Default due date (auto-set if not provided)
- Tag input as string → parsed into DB

📸 SS soon

---

## 📉 Overdue System

- Automatic detection of overdue events
- Highlighted visually
- Counted in navbar
- Dedicated filter

📸 SS soon

---

## 🏆 Hall of Fame

A separate page showing:

- 🎖 User level (milestone system)
- 📈 Progress to next level
- ✅ Completed events list

📸 SS soon

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

## 📸 Screenshots

> Coming soon (SS soon)
