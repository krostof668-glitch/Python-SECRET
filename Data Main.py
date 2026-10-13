import logging
import sys
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# 1. CONFIGURE SERVER LOGGING 
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s', handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger("server_data")

# 2. DATABASE CONFIGURATION
# Using SQLite for local setup; switch to 'postgresql://user:pass@localhost/db' seamlessly later.
DATABASE_URL = "sqlite:///server_storage.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create a thread-safe Session factory 
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 3. SCHEMA DEFINITIONS (One-to-Many Relationship Example)
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    
    # Establish relationship linking a user to multiple inventory/profile assets
    items = relationship("UserItem", back_populates="owner", cascade="all, delete-orphan")

class UserItem(Base):
    __tablename__ = "user_items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    owner = relationship("User", back_populates="items")

# Build the tables instantly on disk if they do not exist
Base.metadata.create_all(bind=engine)


# 4. CRUD CONTROLLER ENGINE
class DataManager:
    @staticmethod
    def create_user(username: str, email: str):
        """CREATE: Inserts a new user record safely."""
        with SessionLocal() as db:
            new_user = User(username=username, email=email)
            try:
                db.add(new_user)
                db.commit()
                db.refresh(new_user)
                logger.info(f"Database: Saved new user '{username}' with ID {new_user.id}")
                return new_user.id
            except Exception as e:
                db.rollback()
                logger.error(f"Database write failure: {e}")
                return None

    @staticmethod
    def get_user_by_username(username: str):
        """READ: Queries a user and fetches all relational children."""
        with SessionLocal() as db:
            user = db.query(User).filter(User.username == username).first()
            if user:
                # Eagerly map items details before closing the context session
                return {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "items": [{"id": i.id, "title": i.title} for i in user.items]
                }
            return None

    @staticmethod
    def add_item_to_user(user_id: int, title: str, description: str):
        """CREATE (Relational): Attaches a data asset to a specific user constraint."""
        with SessionLocal() as db:
            new_item = UserItem(title=title, description=description, owner_id=user_id)
            db.add(new_item)
            db.commit()
            logger.info(f"Database: Added item '{title}' to User ID {user_id}")

    @staticmethod
    def update_user_email(username: str, new_email: str):
        """UPDATE: Modifies an existing data field."""
        with SessionLocal() as db:
            user = db.query(User).filter(User.username == username).first()
            if user:
                user.email = new_email
                db.commit()
                logger.info(f"Database: Updated email for '{username}' to '{new_email}'")
                return True
            return False

    @staticmethod
    def delete_user(username: str):
        """DELETE: Triggers a cascading deletion of a user and their sub-items."""
        with SessionLocal() as db:
            user = db.query(User).filter(User.username == username).first()
            if user:
                db.delete(user)
                db.commit()
                logger.info(f"Database: Purged user '{username}' and associated dependencies.")
                return True
            return False


# 5. SIMULATING REAL-WORLD DATA OPERATIONS
if __name__ == "__main__":
    print("--- Running Data Lifecycle Operations ---")

    # Step 1: Provision a clean record
    user_id = DataManager.create_user(username="dev_core", email="initial@server.com")
    
    # Step 2: Inject dependent structural records 
    if user_id:
        DataManager.add_item_to_user(user_id=user_id, title="API Access Key", description="Production key")
        DataManager.add_item_to_user(user_id=user_id, title="Profile Config", description="Dark theme settings")

    # Step 3: Read back structural states
    profile = DataManager.get_user_by_username("dev_core")
    print(f"\nRetrieved Data Record:\n{profile}\n")

    # Step 4: Perform data mutations
    DataManager.update_user_email("dev_core", "updated_active@server.com")

    # Step 5: Clean up record states
    DataManager.delete_user("dev_core")
