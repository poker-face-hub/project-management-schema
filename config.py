import os

class Config:
    DATABASE_URI=os.getenv("DATABASE_URI","project-management.db")
    DEBUG=False
    TESTING=False

class DevelopmentConfig(Config):
    DEBUG=True

class TestingConfig(Config):
    TESTING=True
    DATABASE_URI="file:testdb?mode=memory&cache=shared"