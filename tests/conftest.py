import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))


import pytest
from app import create_app
from config import TestingConfig
from models import db

@pytest.fixture
def client():
    app = create_app(TestingConfig)
    app.config["PROPAGATE_EXCEPTIONS"] = True
    with app.app_context():
        db.create_all()

        with app.test_client() as client:
            yield client
        db.session.remove()
        db.drop_all()
