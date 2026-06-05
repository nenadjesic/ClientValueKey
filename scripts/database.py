import os
import uuid
from sqlalchemy import create_engine, Column, String
from sqlalchemy.orm import declarative_base, sessionmaker
import bcrypt

# FORMAT: mysql+pymysql://USER:PASSWORD@HOST:PORT/DATABASE_NAME
# Adjust parameters ('root' and 'my_password') to match your MySQL server
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "mysql+pymysql://root:1234%23ReWq@localhost:3306/uservault_db"
)

engine = create_engine(
    DATABASE_URL, 
    pool_pre_ping=True,  # Automatically refreshes broken connections
    pool_size=10,        # Maximum number of permanent connections
    max_overflow=20      # Temporary additional connections under load
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# SQL Model for Users
class UserModel(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    mobile_number = Column(String(20), nullable=False)
    language = Column(String(10), nullable=False)  # FIXED: String(10) instead of String=10
    culture = Column(String(10), nullable=False)   # FIXED: String(10) instead of String=10
    password_hash = Column(String(255), nullable=False)

# SQL Model for API Keys (Clients)
class ClientModel(Base):
    __tablename__ = "clients"
    
    api_key = Column(String(255), primary_key=True)
    client_name = Column(String(100), nullable=False)

def init_db():
    # Creates tables in the MySQL database if they do not exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        if not db.query(ClientModel).first():
            db.add_all([
                ClientModel(api_key=str(uuid.uuid4()), client_name="First Client"),
                ClientModel(api_key=str(uuid.uuid4()), client_name="Second Client")
            ])
            db.commit()
    finally:
        db.close()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        # Explicitly convert the text string from the request into bytes
        password_bytes = plain_password.encode('utf-8')
        
        # Explicitly convert the text string from MySQL into bytes
        hash_bytes = hashed_password.encode('utf-8')
        
        # Pass pure binary data to bcrypt
        return bcrypt.checkpw(password_bytes, hash_bytes)
    except Exception:
        return False

