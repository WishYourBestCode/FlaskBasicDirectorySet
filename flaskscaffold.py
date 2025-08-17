#!/usr/bin/env python3
"""
Run this file with:
    python flask_scaffold.py
It will auto-create a basic Flask project called `MyFlaskApp`.
"""

from pathlib import Path
from textwrap import dedent

def write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def main():
    root = Path("MyFlaskApp").resolve()
    pkg = root / "app"
    print(f"Creating Flask project at {root} ...")
    root.mkdir(parents=True, exist_ok=True)

    # Basic files
    write(root / "requirements.txt", dedent("""\
        Flask>=3.0
        Flask-SQLAlchemy>=3.1
        Flask-Migrate>=4.0
        SQLAlchemy>=2.0
    """))

    write(root / "run.py", dedent("""\
        from app import create_app
        app = create_app()

        if __name__ == "__main__":
            app.run(debug=True)
    """))

    write(root / "wsgi.py", dedent("""\
        from app import create_app
        app = create_app()
    """))

    write(root / "config.py", dedent("""\
        import os

        class Config:
            SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key')
            SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
            SQLALCHEMY_TRACK_MODIFICATIONS = False
    """))

    # App package
    write(pkg / "__init__.py", dedent("""\
        from flask import Flask
        from .extensions import db, migrate

        def create_app():
            app = Flask(__name__)
            app.config.from_object('config.Config')

            db.init_app(app)
            migrate.init_app(app, db)

            from .routes import main_bp
            app.register_blueprint(main_bp)

            return app
    """))

    write(pkg / "extensions.py", dedent("""\
        from flask_sqlalchemy import SQLAlchemy
        from flask_migrate import Migrate

        db = SQLAlchemy()
        migrate = Migrate()
    """))

    write(pkg / "routes.py", dedent("""\
        from flask import Blueprint, render_template

        main_bp = Blueprint("main", __name__)

        @main_bp.route("/")
        def index():
            return render_template("index.html", title="Home")
    """))

    write(pkg / "templates" / "base.html", dedent("""\
        <!doctype html>
        <html>
        <head>
          <title>{{ title }}</title>
          <link rel="stylesheet" href="{{ url_for('static', filename='css/main.css') }}">
        </head>
        <body>
          <header><h1>{{ title }}</h1></header>
          <main>{% block content %}{% endblock %}</main>
        </body>
        </html>
    """))

    write(pkg / "templates" / "index.html", dedent("""\
        {% extends "base.html" %}
        {% block content %}
          <p>Hello from Flask! 🎉</p>
        {% endblock %}
    """))

    write(pkg / "static" / "css" / "main.css", "body { font-family: Arial; margin: 2rem; }")

    print("✅ Done! Next steps:")
    print("  cd MyFlaskApp")
    print("  python -m venv .venv")
    print("  .venv\\Scripts\\activate   # Windows")
    print("  pip install -r requirements.txt")
    print("  python run.py  # visit http://127.0.0.1:5000")

if __name__ == "__main__":
    main()
