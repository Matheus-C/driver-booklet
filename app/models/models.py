from sqlalchemy import ForeignKey,Column,String,Integer,Float,CHAR,DateTime,Date,Boolean, TIMESTAMP, TEXT,text
from sqlalchemy.ext.declarative import declarative_base
from flask_login import UserMixin
from .database import *
from datetime import datetime

Base = declarative_base()

class PushSubscription(Base):
  __tablename__ = 'push_subscription'  
  id = Column(Integer, primary_key=True, unique=True)
  subscription_json = Column(String(512), nullable=False)
  timestamp = Column('timestamp', DateTime)
  userId = Column('userid', ForeignKey('users.id'))

class User(Base,UserMixin):
  __tablename__ = 'users'
  id = Column('id', Integer, primary_key=True)
  userTypeId = Column(Integer, ForeignKey('userType.id'))
  name = Column('name', String(255))
  userIdentification = Column('userIdentification', String(255))
  phone = Column('phone', String(255))
  address = Column('address', String(255))
  email = Column('email', String(255))
  birthDate = Column('birthDate', Date)
  password = Column('password', TEXT(255))
  is_active = Column(Boolean, default=False)

  def __repr__(self):
    return f'<User: {self.id},{self.name},{self.email}>'
   
  def get_id(self):
    return self.id
   
  @property
  def is_authenticated(self):
    return True  # Assuming all users are authenticated

  @property
  def is_active(self):
    return True

  @property
  def is_anonymous(self):
    return False

class UserType(Base):
  __tablename__ = 'userType'
  id = Column('id', Integer, primary_key=True)
  name = Column('name', String(255))
  description = Column('description', String(255))

class EventType(Base):
  __tablename__ = 'eventType'
  id = Column('id', Integer, primary_key=True)
  name = Column('name', String(255))
  category = Column('category', String(255))
  description = Column('description', String(255))

class Event(Base):
  __tablename__ = 'event'
  id = Column('id', Integer, primary_key=True)
  eventTimestamp = Column('eventTime', DateTime)
  idType = Column(Integer, ForeignKey('eventType.id'))
  idUser = Column(Integer, ForeignKey('users.id'))
  idVehicle = Column(Integer, ForeignKey('vehicle.id'))
  idCompany = Column(Integer, ForeignKey('company.id'))
  geolocation = Column('geolocation', String(512))
  idAttachment = Column(Integer, ForeignKey('attachment.id'))
  createdAt = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))

class Attachment(Base):
  __tablename__ = 'attachment'
  id = Column('id', Integer, primary_key=True)
  idUser = Column(Integer, ForeignKey('users.id'))
  idType = Column(Integer, ForeignKey('eventType.id'))
  description = Column('description', String(255))

class Company(Base):
  __tablename__ = 'company'
  id = Column('id', Integer, primary_key=True)
  idUser = Column(Integer, ForeignKey('users.id'))
  name = Column('name', String(255))
  description = Column('description', String(255))
  address = Column('address', String(255))
  phone = Column('phone', String(255))
  vatcode = Column('vatcode', String(255))

class UserCompany(Base):
  __tablename__ = 'userCompany'
  id = Column('id', Integer, primary_key=True)
  idUser = Column(Integer, ForeignKey('users.id'))
  idCompany = Column(Integer, ForeignKey('company.id'))
  startWork = Column('startWork', Date)
  validUntil = Column('validUntil', Date)


class CompanyVehicle(Base):
  __tablename__ = 'companyVehicle'
  id = Column('id', Integer, primary_key=True)
  idCompany = Column(Integer, ForeignKey('company.id'))
  idVehicle = Column(Integer, ForeignKey('vehicle.id'))
  startDate = Column('startDate', Date)
  validUntil = Column('validUntil', Date)

class Vehicle(Base):
  __tablename__ = 'vehicle'
  id = Column('id', Integer, primary_key=True)
  model = Column('model', String(255))
  manufacturer = Column('manufacturer', String(255))
  color = Column('color', String(255))
  licensePlate = Column('licensePlate', String(255))

class VehicleEvent(Base):
  __tablename__ = 'vehicleEvent'
  id = Column('id', Integer, primary_key=True)
  eventTime = Column('eventTime', DateTime)
  idType = Column(Integer, ForeignKey('eventType.id'))
  idUser = Column(Integer, ForeignKey('users.id'))
  idVehicle = Column(Integer, ForeignKey('vehicle.id'))
  idCompany = Column(Integer, ForeignKey('company.id'))
  mileage = Column('mileage', Float)
  idAttachment = Column('idAttachment', ForeignKey('attachment.id'))



Base.metadata.create_all(engine)