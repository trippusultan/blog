# ── personal blog — Flask backend ────────────────────────────────────
import sys, os
# venv site-packages bootstrap (dev / no venv activation needed)
_venv_sp = os.path.join(os.path.dirname(__file__), 'venv', 'lib',
                        f'python{sys.version_info.major}.{sys.version_info.minor}',
                        'site-packages')
if os.path.isdir(_venv_sp) and _venv_sp not in sys.path:
    sys.path.insert(0, _venv_sp)

from flask import Flask, render_template, request, redirect, url_for, session, abort, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import all_articles, get_article, save_article, delete_article, SECRET

app = Flask(__name__)
app.secret_key = SECRET

# ── hardcoded admin credentials ───────────────────────────────────────
ADMIN_USER = 'admin'
ADMIN_PASS_HASH = generate_password_hash('admin123')   # change in production

def login_required():
    if not session.get('logged_in'):
        return redirect(url_for('login', next=request.path))

# ════════════════════════════════════════════════════════════════════
# GUEST SECTION
# ════════════════════════════════════════════════════════════════════

@app.route('/')
def index():
    articles = all_articles()
    return render_template('index.html', articles=articles)

@app.route('/article/<art_id>')
def article(art_id):
    article = get_article(art_id)
    if not article:
        abort(404)
    return render_template('article.html', article=article)

# ════════════════════════════════════════════════════════════════════
# ADMIN — AUTH
# ════════════════════════════════════════════════════════════════════

@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if (request.form.get('username') == ADMIN_USER
                and check_password_hash(ADMIN_PASS_HASH, request.form.get('password', ''))):
            session['logged_in'] = True
            next_url = request.args.get('next') or url_for('dashboard')
            return redirect(next_url)
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
    return render_template('admin/dashboard.html', articles=all_articles())

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
        )
        return redirect(url_for('article', art_id=art_id))
    return render_template('admin/edit.html', article=None, action='Add')

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
        )
        return redirect(url_for('article', art_id=art_id))
    return render_template('admin/edit.html', article=article, action='Edit')

@app.route('/admin/delete/<art_id>', methods=['POST'])
def delete_article_route(art_id):
    if login_required() is not None:
        return login_required()
    delete_article(art_id)
    return redirect(url_for('dashboard'))

# ════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
