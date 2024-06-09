import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, distinct ,func ,or_,extract
from sqlalchemy.orm import sessionmaker,aliased
load_dotenv()

user_db = os.environ.get('user_db')
pass_db = os.environ.get('pass_db')
host_db = os.environ.get('host_db')

engine = create_engine(f"postgresql+psycopg2://{user_db}:{pass_db}@{host_db}", pool_recycle=100,pool_pre_ping=True)
Session = sessionmaker(bind=engine)
session = Session()

# from app import app
# app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqlconnector://{user_db}:{pass_db}@{host_db}"
# from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate
# db = SQLAlchemy(app)
# migrate = Migrate(app, db)