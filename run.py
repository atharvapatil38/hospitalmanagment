import os
from app import create_app
from app.extensions import db

env_name = os.environ.get('FLASK_ENV', 'development')
app = create_app(env_name)

@app.cli.command("seed-db")
def seed_db_command():
    """Command-line utility to seed realistic demonstration hospital data."""
    from seed import seed_database
    seed_database()
    print("Database successfully populated with realistic hospital records.")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() in ['true', '1', 'yes']
    print(f"================================================================")
    print(f"[CarePlus] Hospital Management System (HMS)")
    print(f"Server starting at http://127.0.0.1:{port}")
    print(f"Default Admin Login: admin@careplus.com | Password: Admin@123")
    print(f"================================================================")
    app.run(host='0.0.0.0', port=port, debug=debug)
