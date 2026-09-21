import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import sqlite3
import pytest
from app import create_app
from config import TestingConfig
from database import init_db

@pytest.fixture
def client():
    app=create_app(TestingConfig)
    database_uri=app.config["DATABASE_URI"]
    conn=sqlite3.connect(database_uri)
    init_db(conn)

    with app.test_client() as client:
        yield client

    conn.close()