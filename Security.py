import datetime
import logging
import sys
import bcrypt
import jwt
from pydantic import BaseModel, EmailStr, Field, ValidationError
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# -------------------------------------------------------------
# 0. SERVER LOGGING SETUP
# -------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("server_security")

# Secret key used to sign JSON Web Tokens (Keep this hidden in production environment variables!)
JWT_SECRET_KEY = "SUPER_SECRET_SERVER_SIGNING_KEY_DO_NOT_SHARE"
JWT_ALGORITHM = "HS256"

# -------------------------------------------------------------
# 1. DATA LAYER: DATABASE & ORM SETUP (SQLAlchemy)
# -------------------------------------------------------------
DATABASE_URL = "sqlite:///server_data.db"  # Creates a local database file
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Model representing how data is structured on disk
class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)

# Build the database tables immediately
Base.metadata.create_all(bind=engine)


# -------------------------------------------------------------
# 2. SECURITY LAYER: INPUT VALIDATION (Pydantic)
# -------------------------------------------------------------
# Validates client data payloads arriving at the server gate
class UserRegistrationSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    email: EmailStr  # Automatically enforces strict email formatting rules
    password: str = Field(..., min_length=8)


# -------------------------------------------------------------
# 3. SECURITY LAYER: CRYPTOGRAPHY & TOKENS (Bcrypt & PyJWT)
# -------------------------------------------------------------
class SecurityManager:
    @staticmethod
    def hash_password(password: str) -> str:
        """Salts and hashes a plain text password for safe storage."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Checks if an inbound password matches the stored database hash."""
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.decode('utf-8'))

    @staticmethod
    def generate_jwt_token(username: str) -> str:
        """Creates a signed, time-limited token confirming authentication status."""
        payload = {
            "sub": username,
            "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=2),
            "iat": datetime.datetime.now(datetime.timezone.utc)
        }
        return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    @staticmethod
    def verify_jwt_token(token: str) -> dict | None:
        """Decodes and cryptographically validates an inbound user token."""
        try:
            return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        except jwt.ExpiredSignatureError:
            logger.warning("Rejected Request: Token has expired.")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Rejected Request: Token signature or payload is invalid.")
            return None


# -------------------------------------------------------------
# 4. SIMULATING SERVER API ACTIONS
# -------------------------------------------------------------
def register_user(raw_payload: dict):
    """Simulates a user attempting to sign up via a POST request."""
    db = SessionLocal()
    try:
        # Step A: Enforce strict input boundary validation
        valid_data = UserRegistrationSchema(**raw_payload)
        
        # Step B: Securely transform sensitive data
        secured_password = SecurityManager.hash_password(valid_data.password)
        
        # Step C: Write cleanly to database via ORM object mapping
        new_user = UserModel(
            username=valid_data.username,
            email=valid_data.email,
            hashed_password=secured_password
        )
        db.add(new_user)
        db.commit()
        logger.info(f"Database: Successfully registered user '{valid_data.username}' safely.")
    
    except ValidationError as e:
        logger.error(f"Validation Failure on Registration: {e.json()}")
    except Exception as e:
        db.rollback()
        logger.error(f"Server Error during registration: {str(e)}")
    finally:
        db.close()

def login_user(username, password) -> str | None:
    """Simulates a user attempting to authenticate."""
    db = SessionLocal()
    user = db.query(UserModel).filter(UserModel.username == username).first()
    db.close()

    if user and SecurityManager.verify_password(password, user.hashed_password):
        token = SecurityManager.generate_jwt_token(username)
        logger.info(f"Authentication: Handed session token to valid user '{username}'.")
        return token
    
    logger.warning(f"Authentication Failure: Unauthorized access attempt for user '{username}'.")
    return None


# -------------------------------------------------------------
# RUNNING THE SIMULATION
# -------------------------------------------------------------
if __name__ == "__main__":
    print("--- 1. Handling Malformed Registration Payload ---")
    bad_client_data = {"username": "al", "email": "not-an-email", "password": "short"}
    register_user(bad_client_data)

    print("\n--- 2. Handling Valid Registration Payload ---")
    good_client_data = {"username": "alice_dev", "email": "alice@example.com", "password": "super_secure_password123"}
    register_user(good_client_data)

    print("\n--- 3. Handling User Login & Session Generation ---")
    session_token = login_user("alice_dev", "super_secure_password123")
    print(f"Generated Client Token: {session_token}")

    print("\n--- 4. Accessing a Protected Endpoint using the Token ---")
    if session_token:
        # Client requests data and hands the server their token
        decoded_payload = SecurityManager.verify_jwt_token(session_token)
        if decoded_payload:
            print(f"Access Granted! Hello {decoded_payload['sub']}. Here is your server dashboard data.")
