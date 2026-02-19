import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import engine, Base
from app.models.user import User
from app.models.alert import Alert
from app.core.security import get_password_hash
import bcrypt

def create_all_tables():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created successfully")

def create_demo_users():
    """Create all demo users for the hackathon"""
    db = Session(bind=engine)
    
    demo_users = [
        {
            "email": "admin@barclays.com",
            "password": "Admin@123",
            "full_name": "System Administrator",
            "role": "admin",
            "department": "Compliance"
        },
        {
            "email": "analyst@barclays.com",
            "password": "password123",
            "full_name": "John Analyst",
            "role": "analyst",
            "department": "AML Compliance"
        },
        {
            "email": "supervisor@barclays.com",
            "password": "password123",
            "full_name": "Jane Supervisor",
            "role": "supervisor",
            "department": "AML Compliance"
        }
    ]
    
    print("\nCreating demo users...")
    for user_data in demo_users:
        # Check if user already exists
        existing = db.query(User).filter(User.email == user_data["email"]).first()
        
        if existing:
            print(f"  ⚠️  User already exists: {user_data['email']}")
            # Update password to ensure it's correct
            existing.hashed_password = get_password_hash(user_data["password"])
            db.commit()
            print(f"  ✓ Password updated for: {user_data['email']}")
        else:
            # Create new user
            user = User(
                email=user_data["email"],
                hashed_password=get_password_hash(user_data["password"]),
                full_name=user_data["full_name"],
                role=user_data["role"],
                department=user_data["department"],
                is_active=True
            )
            db.add(user)
            db.commit()
            print(f"  ✓ Created user: {user_data['email']}")
    
    db.close()
    
    print("\n" + "=" * 60)
    print("DEMO CREDENTIALS - Ready for Hackathon")
    print("=" * 60)
    print("\n1. ADMIN ACCOUNT:")
    print("   Email: admin@barclays.com")
    print("   Password: Admin@123")
    print("   Access: Full system access")
    
    print("\n2. ANALYST ACCOUNT:")
    print("   Email: analyst@barclays.com")
    print("   Password: password123")
    print("   Access: Generate SARs, view reports")
    
    print("\n3. SUPERVISOR ACCOUNT:")
    print("   Email: supervisor@barclays.com")
    print("   Password: password123")
    print("   Access: Approve/reject SARs")
    
    print("\n" + "=" * 60)
    print("✓ All demo users created successfully!")
    print("=" * 60)

if __name__ == "__main__":
    print("=" * 60)
    print("AML Intelligence Platform - Demo User Setup")
    print("=" * 60)
    
    try:
        create_all_tables()
        create_demo_users()
        print("\n✓ Setup completed successfully!")
        print("\nYou can now login at: http://localhost:3000")
    except Exception as e:
        print(f"\n✗ Error during setup: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
