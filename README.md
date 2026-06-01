# Smart Property Finder

A modern real-estate property management platform with a clean **backend / frontend separation**.

---

## Project Structure

```text
smart_property_finder/
├── backend/          <-- Django backend (API + business logic)
│   ├── smart_property_finder/   # Project settings, URLs, WSGI, ASGI
│   ├── properties/              # Property listings app
│   ├── accounts/                # User authentication app
│   ├── manage.py
│   └── requirements.txt
│
├── frontend/         <-- HTML templates + CSS/JS/assets
│   ├── templates/               # All Django HTML templates
│   │   ├── base.html
│   │   ├── properties/
│   │   └── registration/
│   └── static/
│       └── css/
│
└── README.md
```

---

## Quick Start

### 1. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

The backend server starts at `http://127.0.0.1:8000/`.

### 2. Frontend Files

All templates live in `frontend/templates/`.
All static assets (CSS, JS, images) live in `frontend/static/`.

Django is already configured to pick templates and static files from those locations (see `settings.py`).

---

## What's Where

| Concern | Location |
|---------|----------|
| Django settings, URLs, WSGI | `backend/smart_property_finder/` |
| Property models, views, forms | `backend/properties/` |
| Auth models, views, forms | `backend/accounts/` |
| HTML templates | `frontend/templates/` |
| CSS / JS / images | `frontend/static/` |
| Database (SQLite) | `backend/db.sqlite3` |
| Uploaded media | `backend/media/` |

---

## Key Features

- **Property Listings:** Create, edit, delete properties with images
- **Search & Filter:** Keyword, listing type, property type, price, bedrooms, furnished status
- **Image Gallery:** Multiple images per property with carousel
- **Wishlist:** Save favorite properties (authenticated users)
- **Inquiries:** Contact agents directly via property detail pages
- **Admin Dashboard:** Full moderation via Django admin

---

## Technology Stack

- **Backend:** Django (Python)
- **Frontend:** HTML, CSS, Bootstrap 5, JavaScript
- **Database:** SQLite (default, swap to MySQL/Postgres in production)
- **Version Control:** Git
