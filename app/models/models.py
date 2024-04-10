from sqlalchemy import ForeignKey,Column,String,Integer,Float,CHAR,DateTime,Date
from sqlalchemy.ext.declarative import declarative_base
from .database import *

import uuid

def generate_id():
    return str(uuid.uuid4())

Base = declarative_base()

class PushSubscription(Base):
  __tablename__ = 'push_subscription'  
  id = Column(Integer, primary_key=True, unique=True)
  subscription_json = Column(String, nullable=False)


class Event(Base):
  __tablename__ = 'event'  
  id = Column(Integer, primary_key=True, unique=True)
  type = Column(String, nullable=False)
  start_time = Column(Date, nullable=False)

Base.metadata.create_all(engine)

# class FlightCombinations(Base):
#     __tablename__ = 'flight_combinations'
#     origin = Column('origin',String)
#     destination= Column("destination",String)
#     date_start= Column("date_start",Date)
#     date_end= Column("date_end",Date)
#     type= Column("type",String)
#     num_days= Column("num_days",Integer)
#     price= Column("price",Float)
#     url = Column("url",String,primary_key=True)
#     extraction_date = Column("extraction_date",DateTime)
