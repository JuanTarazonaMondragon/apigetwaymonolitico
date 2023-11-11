# -*- coding: utf-8 -*-
"""Database models definitions. Table representations as class."""
from sqlalchemy import Column, DateTime, Integer, String, TEXT, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class BaseModel(Base):
    """Base database table representation to reuse."""
    __abstract__ = True
    creation_date = Column(DateTime(timezone=True), server_default=func.now())
    update_date = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

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


class Client(BaseModel):
    """Client database table representation."""
    STATUS_CREATED = "Created"
    STATUS_FINISHED = "Finished"

    __tablename__ = "clients"
    id_client = Column(Integer, primary_key=True)
    email = Column(TEXT, nullable=False)
    username = Column(TEXT, nullable=False)
    password = Column(TEXT, nullable=False)
    address = Column(TEXT, nullable=False)
    postal_code = Column(Integer, nullable=False)
    role = Column(Integer, nullable=False, default=0) # 0 = CLIENT    1 = ADMIN

    def as_dict(self):
        """Return the client item as dict."""
        dictionary = super().as_dict()
        dictionary['client'] = [i.as_dict() for i in self.pieces]
        return dictionary
