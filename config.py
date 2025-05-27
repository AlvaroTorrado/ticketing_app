class Config:
    SECRET_KEY = 'torrado'  # Protección de formularios
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root@mysql/tfg_tickets'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
import os

SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
