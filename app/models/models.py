from sqlalchemy import ForeignKey,Column,String,Integer,Float,CHAR,DateTime,Date
from sqlalchemy.ext.declarative import declarative_base

import uuid

def generate_id():
    return str(uuid.uuid4())

Base = declarative_base()

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
