# Personal Blog

A lightweight, filesystem-backed blog built with **Flask 3.1 + Jinja2 + vanilla HTML/CSS**.

No database, no JavaScript framework — articles live as JSON on disk and are rendered server-side.

---

## Features

### Guest section
| Page | Route | Description |
|------|-------|-------------|
| Home | `/` | Chronological list of all published articles |
| Article | `/article/<id>` | Full article content + publication date |

### Admin section (session auth)
| Page | Route | Description |
|------|-------|-------------|
| Login | `/admin/login` | Session-based login (hardcoded: `admin / admin123`) |
| Dashboard | `/admin` | Article list with Add / Edit / Delete actions |
| Add Article | `/admin/add` | New article form (title, HTML content, date) |
| Edit Article | `/admin/edit/<id>` | Edit existing article |
| Delete | `POST /admin/delete/<id>` | Confirm-and-delete with toast feedback |

---

## Run locally

```bash
cd /home/spoidy/workspace/blog
PYTHONPATH=/home/spoidy/workspace/blog/venv/lib/python3.12/site-packages \
  /home/spoidy/workspace/blog/venv/bin/python run.py
```

Then open:
- **Blog** → http://localhost:8001
- **Admin login** → http://localhost:8001/admin/login  (`admin` / `admin123`)

Press `Ctrl+C` to stop. Debug mode (`debug=True`) reloads on file changes.

---

## File tree

```
blog/
├── app.py             — Flask routes + session auth
├── models.py          — JSON read/write, slugify, CRUD helpers
├── run.py             — venv bootstrap + entry point
├── requirements.txt   — Flask (for reference)
├── data/
│   └── articles.json  — article storage (auto-created)
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── article.html
│   ├── login.html
│   ├── admin/
│   │   ├── dashboard.html
│   │   └── edit.html  (reused by Add + Edit)
├── static/
│   └── style.css      — dark editorial theme
└── README.md
```

---

## Roadmap

https://roadmap.sh/projects/personal-blog
