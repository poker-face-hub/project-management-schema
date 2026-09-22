import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import sqlite3
import pytest
from app import create_app
from config import TestingConfig
from database import get_connection,init_db

@pytest.fixture
def client():
    app=create_app(TestingConfig)
    with app.app_context():
        conn=get_connection()
        init_db(conn)

    with app.test_client() as client:
        yield client

    conn.close()