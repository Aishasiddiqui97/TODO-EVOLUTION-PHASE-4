import os
import uuid
from sqlmodel import SQLModel, Session, create_engine, select
from dotenv import load_dotenv

# Import models
import sys
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.models.user import User

def seed_database():
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not found")
        return
        
    engine = create_engine(db_url)
    
    # Create tables if they don't exist (though alembic should have done this)
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        # Mock user from auth/middleware.py
        demo_user_id = "550e8400-e29b-41d4-a716-446655440000"
        
        # Check if user already exists
        statement = select(User).where(User.id == demo_user_id)
        existing_user = session.exec(statement).first()
        
        if not existing_user:
            print(f"Seeding demo user: {demo_user_id}")
            demo_user = User(
                id=demo_user_id,
                email="demo@example.com",
                hashed_password="mock_password_hash" # placeholder
            )
            session.add(demo_user)
            session.commit()
            print("Demo user seeded successfully.")
        else:
            print(f"Demo user {demo_user_id} already exists.")

if __name__ == "__main__":
    seed_database()
