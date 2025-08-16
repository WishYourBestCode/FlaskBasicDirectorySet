#!/usr/bin/env python3
"""
Flask project scaffolder.
Usage examples:
  python flask_scaffold.py MyApp
  python flask_scaffold.py MyApp --with-api --init-git
  python flask_scaffold.py MyApp --venv .venv
  python flask_scaffold.py MyApp --force
"""
from __future__ import annotations
import argparse, os, subprocess, sys
from pathlib import Path
from textwrap import dedent

def write(path: Path, content: str, *, overwrite: bool=False):
    if path.exists() and not overwrite:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def make_tree(root: Path, name: str, with_api: bool):
    pkg = "app"

    # --- files ---
    init_py = dedent(f"""\
    from flask import Flask
    from .extensions import db, migrate  # add more extensions as you need

    def create_app():
        app = Flask(__name__)
        app.config.from_object('config.Config')

        # init extensions
        db.init_app(app)
        migrate.init_app(app, db)

        # register blueprints
        from .routes import main_bp
        app.register_blueprint(main_bp)

        {"from .api import api_bp\n        app.register_blueprint(api_bp, url_prefix='/api')" if with_api else ""}

        return app
    """)

    extensions_py = dedent("""\
    from flask_sqlalchemy import SQLAlchemy
    from flask_migrate import Migrate

    db = SQLAlchemy()
    migrate = Migrate()
    """)

    routes_py = dedent("""\
    from flask import Blueprint, render_template

    main_bp = Blueprint('main', __name__)

    @main_bp.route('/')
    def index():
        return render_template('index.html', title='Home')
    """)

    models_py = dedent("""\
    from .extensions import db

    class Example(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(120), nullable=False)
    """)

    forms_py = dedent("""\
    # Optional WTForms go here (only if you use Flask-WTF)
    """)

    base_html = dedent("""\
    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8"/>
      <meta name="viewport" content="width=device-width, initial-scale=1"/>
      <title>{{ title or "Flask App" }}</title>
      <link rel="stylesheet" href="{{ url_for('static', filename='css/main.css') }}">
    </head>
    <body>
      <header><h1>{{ title or "Flask App" }}</h1></header>
      <main>{% block content %}{% endblock %}</main>
      <script src="{{ url_for('static', filename='js/main.js') }}"></script>
    </body>
    </html>
    """)

    index_html = dedent("""\
    {% extends 'base.html' %}
    {% block content %}
      <p>Hello from Flask! 🎉</p>
    {% endblock %}
    """)

    css_main = "body{font-family:system-ui,Segoe UI,Roboto,Helvetica,Arial,sans-serif;margin:2rem;}"
    js_main = "console.log('Flask scaffold ready');"

    api_init = dedent("""\
    from flask import Blueprint, jsonify

    api_bp = Blueprint('api', __name__)

    @api_bp.get('/health')
    def health():
        return jsonify(status='ok')
    """)
    wsgi_py = dedent("""\
    from app import create_app
    app = create_app()
    """)

    run_py = dedent("""\
    from app import create_app
    app = create_app()

    if __name__ == '__main__':
        app.run(debug=True)
    """)

    config_py = dedent("""\
    import os

    class Config:
        SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-me')
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
        SQLALCHEMY_TRACK_MODIFICATIONS = False
    """)

    reqs = dedent("""\
    Flask>=3.0
    Flask-SQLAlchemy>=3.1
    Flask-Migrate>=4.0
    SQLAlchemy>=2.0
    """)

    test_basic = dedent("""\
    from app import create_app

    def test_index():
        app = create_app()
        with app.test_client() as c:
            r = c.get('/')
            assert r.status_code == 200
    """)

    readme = dedent(f"""\
    # {name}

    Minimal Flask app scaffold.

    ## Quickstart
    ```bash
    python -m venv .venv
    . .venv/bin/activate  # Windows: .\\.venv\\Scripts\\activate
    pip install -r requirements.txt
    flask --app wsgi:app db upgrade  # creates DB (no migrations yet but sets up env)
    python run.py
    ```
    """)

    gitignore = dedent("""\
    __pycache__/
    .venv/
    *.pyc
    *.sqlite3
    instance/
    .env
    .DS_Store
    *.log
    migrations/versions/__pycache__/
    """)

    # --- write structure ---
    write(root / "requirements.txt", reqs)
    write(root / "README.md", readme)
    write(root / ".gitignore", gitignore)
    write(root / "run.py", run_py)
    write(root / "wsgi.py", wsgi_py)
    write(root / "config.py", config_py)

    # packages
    write(root / pkg / "__init__.py", init_py)
    write(root / pkg / "extensions.py", extensions_py)
    write(root / pkg / "routes.py", routes_py)
    write(root / pkg / "models.py", models_py)
    write(root / pkg / "forms.py", forms_py)
    write(root / pkg / "templates" / "base.html", base_html)
    write(root / pkg / "templates" / "index.html", index_html)
    write(root / pkg / "static" / "css" / "main.css", css_main)
    write(root / pkg / "static" / "js" / "main.js", js_main)
    if with_api:
        write(root / pkg / "api" / "__init__.py", api_init)

    # migrations + tests
    (root / "migrations").mkdir(parents=True, exist_ok=True)
    write(root / "tests" / "test_basic.py", test_basic)

def init_git(root: Path):
    try:
        subprocess.run(["git", "init"], cwd=root, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(["git", "add", "-A"], cwd=root, check=True)
        subprocess.run(["git", "commit", "-m", "chore: initial flask scaffold"], cwd=root, check=True)
        print("Initialized git repository.")
    except Exception as e:
        print(f"[warn] git init failed: {e}")

def make_venv(root: Path, venv_path: Path):
    try:
        subprocess.run([sys.executable, "-m", "venv", str(venv_path)], cwd=root, check=True)
        print(f"Created virtualenv at {venv_path}")
    except Exception as e:
        print(f"[warn] venv creation failed: {e}")

def main():
    ap = argparse.ArgumentParser(description="Create a basic full-stack Flask directory scaffold.")
    ap.add_argument("name", help="Project folder name (will be created)")
    ap.add_argument("--with-api", action="store_true", help="Add /api blueprint with /api/health")
    ap.add_argument("--init-git", action="store_true", help="Initialize a git repo and make first commit")
    ap.add_argument("--venv", metavar="PATH", help="Create a virtualenv at PATH (e.g., .venv)")
    ap.add_argument("--force", action="store_true", help="Overwrite existing files if they exist")
    args = ap.parse_args()

    root = Path(args.name).resolve()
    root.mkdir(parents=True, exist_ok=True)
    make_tree(root, args.name, with_api=args.with_api)

    if args.venv:
        make_venv(root, root / args.venv)

    if args.init_git:
        init_git(root)

    print(f"✅ Flask scaffold created at: {root}")
    print("Next steps:")
    print(f"  cd {root}")
    if args.venv:
        print(f"  # activate venv: source {args.venv}/bin/activate  (Windows: {args.venv}\\Scripts\\activate)")
    print("  pip install -r requirements.txt")
    print("  flask --app wsgi:app db init  # set up migrations repo")
    print("  flask --app wsgi:app db migrate -m 'init'")
    print("  flask --app wsgi:app db upgrade")
    print("  python run.py  # visit http://127.0.0.1:5000")

if __name__ == "__main__":
    main()
