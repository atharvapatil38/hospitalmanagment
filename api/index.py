import os
import sys

# Ensure root directory is in sys.path for serverless resolution
basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if basedir not in sys.path:
    sys.path.insert(0, basedir)

from app import create_app
from app.extensions import db
from app.models.user import User

env = os.environ.get('FLASK_ENV', 'production')
app = create_app(env)

# Auto-initialize database on cold-start if unpopulated
with app.app_context():
    try:
        db.create_all()
        if User.query.first() is None:
            from seed import seed_database
            seed_database(target_app=app, drop_first=False)
    except Exception as e:
        print(f"[CarePlus Vercel] DB auto-init note: {e}")

# Expose app for Vercel WSGI
if __name__ == '__main__':
    app.run()
