import os
from dotenv import load_dotenv
from pathlib import Path

base_dir = Path(__file__).resolve().parent
load_dotenv(base_dir / '.env')


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'change-me-in-production')
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'your_password')
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'group_project_management')

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DATABASE}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
