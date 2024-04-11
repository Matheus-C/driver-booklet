import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, distinct ,func ,or_,extract
from sqlalchemy.orm import sessionmaker,aliased

load_dotenv()


user_db = os.environ.get('user_db')
pass_db = os.environ.get('pass_db')
host_db = os.environ.get('host_db')

# engine = create_engine(f"sqlite:///{os.getenv('path_to_db_web_app')}",
#                         echo=False,
#                         connect_args={'check_same_thread': False},
#                         pool_size=20, max_overflow=0)
engine = create_engine(f"mysql+mysqlconnector://{user_db}:{pass_db}@{host_db}")
Session = sessionmaker(bind=engine)
session = Session()