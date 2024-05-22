from . import db
from sqlalchemy import Column, Integer, String, Enum, ForeignKey, DECIMAL, Boolean, TIMESTAMP, Text
from sqlalchemy.orm import relationship
import enum

class VendorType(enum.Enum):
    Hotel = "Hotel"
    Restaurant = "Restaurant"
    TourOperator = "TourOperator"
    Yacht = "Yacht"

class User(db.Model):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    name = Column(String(100))
    tg_username = Column(String(100))
    email = Column(String(100), unique=True, index=True)
    phone = Column(String(15))
    created_at = Column(TIMESTAMP, server_default=db.func.localtimestamp())

    # Relationship definitions
    bookings = relationship("Booking", back_populates="user")
    receipts = relationship("Receipt", back_populates="user")
    reviews = relationship("Review", back_populates="user")

class Vendor(db.Model):
    __tablename__ = 'vendors'
    vendor_id = Column(Integer, primary_key=True)
    name = Column(String(100))
    type = Column(Enum(VendorType))
    address = Column(String(255))
    contact_info = Column(String(100))
    created_at = Column(TIMESTAMP, server_default=db.func.current_timestamp())

    # Relationship definitions
    services = relationship("Service", back_populates="vendor")
    cashbacks = relationship("Cashback", back_populates="vendor")

class Service(db.Model):
    __tablename__ = 'services'
    service_id = Column(Integer, primary_key=True)
    vendor_id = Column(Integer, ForeignKey('vendors.vendor_id'))
    name = Column(String(100))
    description = Column(Text)
    price = Column(DECIMAL(10, 2))
    created_at = Column(TIMESTAMP, server_default=db.func.current_timestamp())

    # Relationship definitions
    vendor = relationship("Vendor", back_populates="services")
    bookings = relationship("Booking", back_populates="service")

class Booking(db.Model):
    __tablename__ = 'bookings'
    booking_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    service_id = Column(Integer, ForeignKey('services.service_id'))
    booking_date = Column(TIMESTAMP)
    status = Column(String(50))
    created_at = Column(TIMESTAMP, server_default=db.func.current_timestamp())

    # Relationship definitions
    user = relationship("User", back_populates="bookings")
    service = relationship("Service", back_populates="bookings")
    visits = relationship("Visit", back_populates="booking")

class Visit(db.Model):
    __tablename__ = 'visits'
    visit_id = Column(Integer, primary_key=True)
    booking_id = Column(Integer, ForeignKey('bookings.booking_id'))
    visit_date = Column(TIMESTAMP)
    amount_spent = Column(DECIMAL(10, 2))
    confirmed_by_vendor = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=db.func.current_timestamp())

    # Relationship definitions
    booking = relationship("Booking", back_populates="visits")
    receipts = relationship("Receipt", back_populates="visit")
    reviews = relationship("Review", back_populates="visit")

class Receipt(db.Model):
    __tablename__ = 'receipts'
    receipt_id = Column(Integer, primary_key=True)
    visit_id = Column(Integer, ForeignKey('visits.visit_id'))
    user_id = Column(Integer, ForeignKey('users.user_id'))
    receipt_image_path = Column(String(255))
    amount = Column(DECIMAL(10, 2))
    cashback_amount = Column(DECIMAL(10, 2))
    created_at = Column(TIMESTAMP, server_default=db.func.current_timestamp())

    # Relationship definitions
    visit = relationship("Visit", back_populates="receipts")
    user = relationship("User", back_populates="receipts")

class Cashback(db.Model):
    __tablename__ = 'cashbacks'
    cashback_id = Column(Integer, primary_key=True)
    vendor_id = Column(Integer, ForeignKey('vendors.vendor_id'))
    percentage = Column(DECIMAL(5, 2))
    start_date = Column(TIMESTAMP)
    end_date = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, server_default=db.func.current_timestamp())

    # Relationship definitions
    vendor = relationship("Vendor", back_populates="cashbacks")

class Review(db.Model):
    __tablename__ = 'reviews'
    review_id = Column(Integer, primary_key=True)
    visit_id = Column(Integer, ForeignKey('visits.visit_id'))
    user_id = Column(Integer, ForeignKey('users.user_id'))
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=db.func.current_timestamp())

    # Relationship definitions
    visit = relationship("Visit", back_populates="reviews")
    user = relationship("User", back_populates="reviews")
