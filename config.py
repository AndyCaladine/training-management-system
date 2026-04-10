import os

class Config:
    SECRET_KEY = "dev-secret-key"
    DATABASE = os.path.join(os.getcwd(), "instance", "database.db")