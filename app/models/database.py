from sqlalchemy import create_engine, Column, Integer, String, Boolean, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    is_key_user = Column(Boolean, default=False)

class Device(Base):
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True, index=True)
    mac_address = Column(String, unique=True, index=True)
    hit_counter = Column(Integer, default=0)
    max_hits = Column(Integer, default=9)
    order = Column(Integer, default=0)
    name = Column(String, nullable=True)

# Create SQLite database engine
SQLALCHEMY_DATABASE_URL = "sqlite:///./wsmd.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Create tables
Base.metadata.create_all(bind=engine)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create trigger to reset hit_counter when it reaches max_hits
def create_reset_trigger():
    with engine.begin() as conn:
        # Drop the trigger if it exists to avoid errors when restarting the app
        conn.execute(text("DROP TRIGGER IF EXISTS reset_hit_counter"))
        
        # Create the trigger that resets hit_counter to 0 when it reaches max_hits
        conn.execute(text("""
        CREATE TRIGGER reset_hit_counter
        AFTER UPDATE ON devices
        FOR EACH ROW
        WHEN NEW.hit_counter >= NEW.max_hits
        BEGIN
            UPDATE devices SET hit_counter = 0 WHERE id = NEW.id;
        END;
        """))
        # begin() handles the commit automatically

# Create the trigger
create_reset_trigger()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
