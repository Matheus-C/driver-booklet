import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, distinct ,func ,or_,extract
from sqlalchemy.orm import sessionmaker,aliased
load_dotenv()

user_db = os.environ.get('user_db')
pass_db = os.environ.get('pass_db')
host_db = os.environ.get('host_db')

engine = create_engine(f"mysql+mysqlconnector://{user_db}:{pass_db}@{host_db}", pool_recycle=3600)
Session = sessionmaker(bind=engine)
session = Session()