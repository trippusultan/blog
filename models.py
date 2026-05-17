# ── data layer ────────────────────────────────────────────────────────
import json, os, uuid, datetime, re

DATA   = os.path.join(os.path.dirname(__file__), 'data', 'articles.json')
SECRET = os.environ.get('BLOG_SECRET', 'change-me-admin')

def _load():
    if not os.path.exists(DATA):
        return []
    with open(DATA) as f:
        return json.load(f)

def _save(articles):
    with open(DATA, 'w') as f:
        json.dump(articles, f, indent=2)

def slugify(text):
    return re.sub(r'[^a-z0-9-]+', '-', text.lower().strip()).strip('-')

def all_articles():
    arts = _load()
    arts.sort(key=lambda a: a['date'], reverse=True)
    return arts

def get_article(art_id):
    return next((a for a in _load() if a['id'] == art_id), None)

def save_article(art_id, title, content, date):
    arts = _load()
    if art_id:
        arts = [a for a in arts if a['id'] != art_id]
        art_id = art_id
    else:
        art_id = slugify(title) or str(uuid.uuid4())[:8]
        # ensure uniqueness
        existing = {a['id'] for a in arts}
        if art_id in existing:
            art_id = f"{art_id}-{uuid.uuid4().hex[:6]}"
    arts.append({
        'id':      art_id,
        'title':   title,
        'content': content,
        'date':    date or datetime.date.today().isoformat(),
    })
    _save(arts)
    return art_id

def delete_article(art_id):
    arts = [a for a in _load() if a['id'] != art_id]
    _save(arts)
