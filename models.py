# ── data layer ────────────────────────────────────────────────────────
import json, os, uuid, datetime, re

DATA_DIR  = os.path.join(os.path.dirname(__file__), 'data')
ARTICLES  = os.path.join(DATA_DIR, 'articles.json')
COMMENTS  = os.path.join(DATA_DIR, 'comments.json')
SECRET    = os.environ.get('BLOG_SECRET', 'change-me-admin')

CATEGORIES = ['Technology', 'Tutorial', 'Thoughts', 'Personal', 'Links']
TAG_POOL   = ['flask', 'python', 'web', 'tutorial', 'beginner', 'career',
              'backend', 'frontend', 'devops', 'ai', 'javascript', 'rust',
              'linux', 'wsl', 'productivity', 'open-source']

# ── JSON helpers ──────────────────────────────────────────────────────

def _load(path):
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return json.load(f)

def _save(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

# ── articles ──────────────────────────────────────────────────────────

def _load_arts():
    if not os.path.exists(ARTICLES):
        _migrate_articles()
    return _load(ARTICLES)

def _save_arts(arts):
    _save(ARTICLES, arts)

def slugify(text):
    return re.sub(r'[^a-z0-9-]+', '-', text.lower().strip()).strip('-')

def all_articles():
    arts = _load_arts()
    for a in arts:
        a.setdefault('category', '')
        a.setdefault('tags', [])
    arts.sort(key=lambda a: a['date'], reverse=True)
    return arts

def get_article(art_id):
    arts = all_articles()
    return next((a for a in arts if a['id'] == art_id), None)

def save_article(art_id, title, content, date, **kwargs):
    arts = all_articles()
    kwargs.setdefault('category', '')
    kwargs.setdefault('tags', [])
    if art_id:
        arts = [a for a in arts if a['id'] != art_id]
        old = next((a for a in _load_arts() if a['id'] == art_id), {})
        art_id = art_id
    else:
        art_id = slugify(title) or str(uuid.uuid4())[:8]
        existing = {a['id'] for a in arts}
        if art_id in existing:
            art_id = f"{art_id}-{uuid.uuid4().hex[:6]}"
    arts.append({
        'id':      art_id,
        'title':   title,
        'content': content,
        'date':    date or datetime.date.today().isoformat(),
        **kwargs,
    })
    _save_arts(arts)
    return art_id

def delete_article(art_id):
    arts = [a for a in _load_arts() if a['id'] != art_id]
    _save_arts(arts)

# ── SEARCH ────────────────────────────────────────────────────────────

def search_articles(query):
    q = query.lower().strip()
    if not q:
        return all_articles()
    return [a for a in all_articles()
            if q in a['title'].lower() or q in a.get('content','').lower()]

def distinct_tags():
    tags = set()
    for a in all_articles():
        tags.update(a.get('tags', []))
    return sorted(tags)

def distinct_categories():
    cats = set()
    for a in all_articles():
        if a.get('category'):
            cats.add(a['category'])
    return sorted(cats)

# ── COMMENTS ─────────────────────────────────────────────────────────

def _load_comments():
    return _load(COMMENTS)

def _save_comments(comments):
    _save(COMMENTS, comments)

def get_comments(art_id):
    return [c for c in _load_comments() if c['article_id'] == art_id]

def add_comment(art_id, author, body, ip=''):
    comments = _load_comments()
    cmt = {
        'id':         str(uuid.uuid4())[:8],
        'article_id': art_id,
        'author':     author,
        'body':       body,
        'ip':         ip,
        'date':      datetime.datetime.utcnow().isoformat() + 'Z',
    }
    comments.append(cmt)
    _save_comments(comments)
    return cmt

def delete_comment(cmt_id):
    comments = [c for c in _load_comments() if c['id'] != cmt_id]
    _save_comments(comments)

# ── migrations ───────────────────────────────────────────────────────

def _migrate_articles():
    """Backfill existing articles without category / tags."""
    arts = _load(ARTICLES) if os.path.exists(ARTICLES) else []
    for a in arts:
        a.setdefault('category', '')
        a.setdefault('tags', [])
    _save_arts(arts)
