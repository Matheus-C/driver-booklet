import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, distinct ,func ,or_,extract
from sqlalchemy.orm import sessionmaker,aliased

engine = create_engine(f"sqlite:///{os.getenv('path_to_db_web_app')}",
                        echo=False,
                        connect_args={'check_same_thread': False},
                        pool_size=20, max_overflow=0)
Session = sessionmaker(bind=engine)
session = Session()