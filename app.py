# ── personal blog — Flask backend ────────────────────────────────────
import sys, os

_venv_sp = os.path.join(os.path.dirname(__file__), 'venv', 'lib',
                        f'python{sys.version_info.major}.{sys.version_info.minor}',
                        'site-packages')
if os.path.isdir(_venv_sp) and _venv_sp not in sys.path:
    sys.path.insert(0, _venv_sp)

from flask import Flask, render_template, request, redirect, url_for, session, abort, flash
from models import (all_articles, get_article, save_article, delete_article,
                    search_articles, distinct_tags, distinct_categories,
                    get_comments, add_comment, delete_comment, CATEGORIES, SECRET)

app = Flask(__name__)
app.secret_key = SECRET

ADMIN_USER = 'admin'
ADMIN_PASS_HASH = __import__('werkzeug.security', fromlist=['generate_password_hash','check_password_hash']).generate_password_hash('admin123')

def login_required():
    if not session.get('logged_in'):
        return redirect(url_for('login', next=request.path))

# ════════════════════════════════════════════════════════════════════
# GUEST
# ════════════════════════════════════════════════════════════════════

@app.route('/')
def index():
    q   = request.args.get('q', '').strip()
    cat = request.args.get('cat', '').strip()
    tag = request.args.get('tag', '').strip()

    if q:
        articles = search_articles(q)
    elif cat:
        articles = [a for a in all_articles() if a.get('category') == cat]
    elif tag:
        articles = [a for a in all_articles() if tag in a.get('tags', [])]
    else:
        articles = all_articles()

    return render_template('index.html',
                           articles=articles,
                           query=q,
                           active_cat=cat,
                           active_tag=tag,
                           categories=distinct_categories(),
                           all_tags=distinct_tags())

@app.route('/article/<art_id>')
def article(art_id):
    article = get_article(art_id)
    if not article:
        abort(404)
    comments = get_comments(art_id)
    return render_template('article.html',
                           article=article,
                           comments=comments)

# ════════════════════════════════════════════════════════════════════
# COMMENTS
# ════════════════════════════════════════════════════════════════════

@app.route('/article/<art_id>/comment', methods=['POST'])
def post_comment(art_id):
    article = get_article(art_id)
    if not article:
        abort(404)
    author = (request.form.get('author') or 'Anonymous').strip()[:60]
    body   = (request.form.get('body')   or '').strip()
    if body:
        add_comment(art_id, author, body, ip=request.remote_addr)
    return redirect(url_for('article', art_id=art_id) + '#comments')

@app.route('/comment/<cmt_id>/delete', methods=['POST'])
def delete_comment_route(cmt_id):
    if login_required() is not None:
        return login_required()
    delete_comment(cmt_id)
    return redirect(request.referrer or url_for('index'))

# ════════════════════════════════════════════════════════════════════
# ADMIN — AUTH
# ════════════════════════════════════════════════════════════════════

@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if (request.form.get('username') == ADMIN_USER
                and __import__('werkzeug.security', fromlist=['check_password_hash'])
                .check_password_hash(ADMIN_PASS_HASH, request.form.get('password', ''))):
            session['logged_in'] = True
            return redirect(request.args.get('next') or url_for('dashboard'))
        flash('Invalid credentials', 'error')
    return render_template('login.html')

@app.route('/admin/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

# ════════════════════════════════════════════════════════════════════
# ADMIN — DASHBOARD
# ════════════════════════════════════════════════════════════════════

@app.route('/admin')
def dashboard():
    if login_required() is not None:
        return login_required()
    return render_template('admin/dashboard.html',
                           articles=all_articles(),
                           categories=CATEGORIES)

@app.route('/admin/add', methods=['GET', 'POST'])
def add_article():
    if login_required() is not None:
        return login_required()
    if request.method == 'POST':
        art_id = save_article(
            None,
            request.form['title'],
            request.form['content'],
            request.form.get('date'),
            category = request.form.get('category', ''),
            tags     = [t.strip() for t in request.form.get('tags', '').split(',') if t.strip()],
        )
        return redirect(url_for('article', art_id=art_id))
    return render_template('admin/edit.html',
                           article=None,
                           action='Add',
                           categories=CATEGORIES)

@app.route('/admin/edit/<art_id>', methods=['GET', 'POST'])
def edit_article(art_id):
    if login_required() is not None:
        return login_required()
    article = get_article(art_id)
    if not article:
        abort(404)
    if request.method == 'POST':
        save_article(
            art_id,
            request.form['title'],
            request.form['content'],
            request.form.get('date'),
            category = request.form.get('category', ''),
            tags     = [t.strip() for t in request.form.get('tags', '').split(',') if t.strip()],
        )
        return redirect(url_for('article', art_id=art_id))
    return render_template('admin/edit.html',
                           article=article,
                           action='Edit',
                           categories=CATEGORIES)

@app.route('/admin/delete/<art_id>', methods=['POST'])
def delete_article_route(art_id):
    if login_required() is not None:
        return login_required()
    delete_article(art_id)
    return redirect(url_for('dashboard'))

# ════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8001)
