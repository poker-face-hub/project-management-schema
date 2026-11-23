import os

class Config:
    DATABASE_URI=os.getenv("DATABASE_URI","project-management.db")
    SQLALCHEMY_DATABASE_URI=os.getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///project_management_orm.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG=False
    TESTING=False

class DevelopmentConfig(Config):
    DEBUG=True

class TestingConfig(Config):
    TESTING=True
    DATABASE_URI="file:testdb?mode=memory&cache=shared"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"