from sqlalchemy import MetaData, Table, Column, Integer, String, DateTime

from sqlalchemy import create_engine

import os

metadata = MetaData()

folder_path = 'dbstorage'
if not os.path.exists(folder_path):
    os.makedirs(folder_path)

# Create database instance
DATABASE_URL = f"sqlite:///./{folder_path}/.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

conversations = Table(
    "conversations",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("thread_id", String, nullable=False),  # ID returned by OpenAI API
    Column("default_assistant_id", String, nullable=False),
    Column("created_at", DateTime, nullable=False)
)

conversation_messages = Table(
    "conversation_messages",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("thread_id", String, nullable=False),  # ID returned by OpenAI API
    Column("source", String, nullable=False),
    Column("content", String, nullable=False),
    Column("created_at", DateTime, nullable=False)
)

conversation_runs = Table(
    "runs",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("run_id", String, nullable=False),  # ID returned by OpenAI API
    Column("thread_id", String, nullable=False),  # ID returned by OpenAI API
    Column("assistant_id", String, nullable=False),
    Column("created_at", DateTime, nullable=False)
)

run_steps = Table(
    "run_details",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("run_id", String, nullable=False),  # ID returned by OpenAI API
    Column("type", String, nullable=False),
    Column("tool", String, nullable=True),
    Column("input", String, nullable=True),
    Column("output", String, nullable=True),
    Column("created_at", DateTime, nullable=False)
)

def create_tables():
    metadata.create_all(bind=engine)

def get_engine():
    return engine
