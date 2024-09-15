from flask_login import UserMixin
from sqlalchemy import ForeignKey, Column, String, Integer, Float, DateTime, Date, Boolean, TIMESTAMP, TEXT, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from .database import *

Base = declarative_base()


class PushSubscription(Base):
    __tablename__ = 'push_subscription'
    id = Column(Integer, primary_key=True, unique=True)
    subscription_json = Column(String(512), nullable=False)
    timestamp = Column('timestamp', DateTime)
    userId = Column('userid', ForeignKey('users.id'))


class User(Base, UserMixin):
    __tablename__ = 'users'
    id = Column('id', Integer, primary_key=True)
    userTypeId = Column(Integer, ForeignKey('userType.id'))
    name = Column('name', String(255))
    userIdentification = Column('userIdentification', String(255))
    phone = Column('phone', String(255))
    address = Column('address', String(255))
    email = Column('email', String(255))
    birthDate = Column('birthDate', Date)
    _password = Column('password', TEXT(255))
    _mail_verified = Column('mail_verified', Boolean, default=False)
    is_active = Column(Boolean, default=False)
    valid_until = Column('valid_until', Date)

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
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = value

    @property
    def mail_verified(self):
        return self._mail_verified

    @password.setter
    def mail_verified(self, value):
        self._mail_verified = value

    @property
    def is_anonymous(self):
        return False

    def __str__(self):
        return self.name


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
    name_pt = Column('name_pt', String(255))

    def __str__(self):
        return self.name_pt


class Event(Base):
    __tablename__ = 'event'
    id = Column('id', Integer, primary_key=True)
    eventTimestamp = Column('eventTime', DateTime)
    idType = Column(Integer, ForeignKey('eventType.id'))
    idUser = Column(Integer, ForeignKey('users.id'))
    idVehicle = Column(Integer, ForeignKey('vehicle.id'))
    idCompany = Column(Integer, ForeignKey('company.id'))
    idGeolocation = Column(Integer, ForeignKey('geolocation.id'))
    createdAt = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))


class Attachment(Base):
    __tablename__ = 'attachment'
    id = Column('id', Integer, primary_key=True)
    idUser = Column(Integer, ForeignKey('users.id'))
    idCompany = Column(Integer, ForeignKey('company.id'))
    idVehicle = Column(Integer, ForeignKey('vehicle.id'))
    idType = Column(Integer, ForeignKey('eventType.id'))
    start_date = Column('start_date', Date)
    end_date = Column('end_date', Date)
    description = Column('description', String(512))
    createdAt = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    user = relationship('User')
    company = relationship('Company')
    vehicle = relationship('Vehicle')
    type = relationship('EventType')


class Company(Base):
    __tablename__ = 'company'
    id = Column('id', Integer, primary_key=True)
    idUser = Column(Integer, ForeignKey('users.id'))
    name = Column('name', String(255))
    description = Column('description', String(255))
    address = Column('address', String(255))
    phone = Column('phone', String(255))
    vatcode = Column('vatcode', String(255))
    owner = relationship('User')

    def __str__(self):
        return self.name


class UserCompany(Base):
    __tablename__ = 'userCompany'
    id = Column('id', Integer, primary_key=True)
    idUser = Column(Integer, ForeignKey('users.id'))
    idCompany = Column(Integer, ForeignKey('company.id'))
    startWork = Column('startWork', Date)
    validUntil = Column('validUntil', Date)
    user = relationship('User')
    company = relationship('Company')


class CompanyVehicle(Base):
    __tablename__ = 'companyVehicle'
    id = Column('id', Integer, primary_key=True)
    idCompany = Column(Integer, ForeignKey('company.id'))
    idVehicle = Column(Integer, ForeignKey('vehicle.id'))
    startDate = Column('startDate', Date)
    validUntil = Column('validUntil', Date)
    company = relationship('Company')
    vehicle = relationship('Vehicle')


class Vehicle(Base):
    __tablename__ = 'vehicle'
    id = Column('id', Integer, primary_key=True)
    model = Column('model', String(255))
    manufacturer = Column('manufacturer', String(255))
    color = Column('color', String(255))
    licensePlate = Column('licensePlate', String(255))

    def __str__(self):
        return self.licensePlate


class VehicleEvent(Base):
    __tablename__ = 'vehicleEvent'
    id = Column('id', Integer, primary_key=True)
    eventTime = Column('eventTime', DateTime)
    idType = Column(Integer, ForeignKey('eventType.id'))
    idUser = Column(Integer, ForeignKey('users.id'))
    idVehicle = Column(Integer, ForeignKey('vehicle.id'))
    idCompany = Column(Integer, ForeignKey('company.id'))
    mileage = Column('mileage', Float)
    createdAt = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))


class Geolocation(Base):
    __tablename__ = 'geolocation'
    id = Column('id', Integer, primary_key=True)
    coordinates = Column('coordinates', String(512))
    address = Column('address', String(512))


Base.metadata.create_all(engine)
