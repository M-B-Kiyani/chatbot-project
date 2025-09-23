from sqlalchemy import create_engine, text
import os

engine = create_engine(os.getenv("DATABASE_URL"))
with engine.connect() as conn:
    result = conn.execute(text("SELECT 1"))
    print("DB OK:", result.scalar())