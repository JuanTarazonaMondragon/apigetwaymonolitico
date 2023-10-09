# -*- coding: utf-8 -*-
"""Database models definitions. Table representations as class."""
from sqlalchemy import Column, DateTime, Integer, String, TEXT, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


# from datetime import datetime

class BaseModel(Base):
    """Base database table representation to reuse."""
    __abstract__ = True
    creation_date = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        fields = ""
        for column in self.__table__.columns:
            if fields == "":
                fields = f"{column.name}='{getattr(self, column.name)}'"
                # fields = "{}='{}'".format(column.name, getattr(self, column.name))
            else:
                fields = f"{fields}, {column.name}='{getattr(self, column.name)}'"
                # fields = "{}, {}='{}'".format(fields, column.name, getattr(self, column.name))
        return f"<{self.__class__.__name__}({fields})>"
        # return "<{}({})>".format(self.__class__.__name__, fields)

    @staticmethod
    def list_as_dict(items):
        """Returns list of items as dict."""
        return [i.as_dict() for i in items]

    def as_dict(self):
        """Return the item as dict."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Order(BaseModel):
    """Orders database table representation."""
    STATUS_CREATED = "Created"
    STATUS_PAYED = "Payed"
    STATUS_CANCELED = "Canceled"
    STATUS_FINISHED = "Finished"

    __tablename__ = "orders"
    id_order = Column(Integer, primary_key=True)
    number_of_pieces = Column(Integer, nullable=False)
    description = Column(TEXT, nullable=False, default="No description")
    status_order = Column(String(256), nullable=False, default=STATUS_CREATED)
    id_client = Column(Integer, nullable=False)

    pieces = relationship("Piece", back_populates="order", lazy="joined")

    def as_dict(self):
        """Return the order item as dict."""
        dictionary = super().as_dict()
        dictionary['pieces'] = [i.as_dict() for i in self.Pieces]
        return dictionary


class Piece(BaseModel):
    """Piece database table representation."""
    STATUS_CREATED = "Created"
    STATUS_CANCELLED = "Cancelled"
    STATUS_QUEUED = "Queued"
    STATUS_MANUFACTURING = "Manufacturing"
    STATUS_MANUFACTURED = "Manufactured"

    __tablename__ = "pieces"
    id_piece = Column(Integer, primary_key=True)
    manufacturing_date = Column(DateTime(timezone=True), server_default=None)
    status_piece = Column(String(256), default=STATUS_QUEUED)
    id_order = Column(
        Integer,
        ForeignKey('orders.id_order', ondelete='cascade'),
        nullable=True)

    order = relationship('Order', back_populates='pieces', lazy="joined")
