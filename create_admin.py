#!/usr/bin/env python3
from app import create_app, db
from app.models.user import User, UserRole

def create_admin():
    app = create_app()
    with app.app_context():
        # Check if admin already exists
        admin = User.query.filter_by(email='admin@eventmanager.com').first()
        if admin:
            print('Admin account already exists:')
            print(f'Email: admin@eventmanager.com')
            print(f'Password: (preserved existing password)')
        else:
            # Create new admin with a different username
            admin = User(
                username='superadmin',
                email='admin@eventmanager.com',
                password='Admin123!',
                role=UserRole.ADMIN
            )
            try:
                db.session.add(admin)
                db.session.commit()
                print('Created new admin account:')
                print(f'Email: admin@eventmanager.com')
                print(f'Password: Admin123!')
            except Exception as e:
                db.session.rollback()
                print(f"Error creating admin: {str(e)}")
                
                # Try with a different username and email
                try:
                    admin2 = User(
                        username='admin2',
                        email='admin2@eventmanager.com',
                        password='Admin123!',
                        role=UserRole.ADMIN
                    )
                    db.session.add(admin2)
                    db.session.commit()
                    print('Created alternate admin account:')
                    print(f'Email: admin2@eventmanager.com')
                    print(f'Password: Admin123!')
                except Exception as e2:
                    db.session.rollback()
                    print(f"Error creating alternate admin: {str(e2)}")

if __name__ == '__main__':
    create_admin() 