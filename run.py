import os
from dotenv import load_dotenv
from app import create_app, db
from app.models import User, UserRole, Event

# Load environment variables from .env if it exists
load_dotenv()

app = create_app()

# Create a context processor for the shell
@app.shell_context_processor
def make_shell_context():
    return {
        'db': db, 
        'User': User, 
        'UserRole': UserRole, 
        'Event': Event
    }

# Create the first admin user if no users exist
def create_initial_admin():
    with app.app_context():
        if User.query.count() == 0:
            admin_user = User(
                username='admin',
                email='admin@example.com',
                password='admin123',  # This should be changed after first login
                role=UserRole.ADMIN
            )
            db.session.add(admin_user)
            db.session.commit()
            print('Created initial admin user')

if __name__ == '__main__':
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
        # Create initial admin user
        create_initial_admin()
    
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5001)), debug=True)
