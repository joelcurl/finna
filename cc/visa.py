from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from singleton_decorator import singleton

#DeclBase = declarative_base()

@as_declarative()
class Base:
    def to_dict(self):
        return {k:v for k,v in self.__dict__.items() if k[0] != '_'}

class VisaTransaction(Base):
    __tablename__ = 'transactions'
    id = Column(String, primary_key=True)
    date = Column(DateTime)
    isDebit = Column(Boolean)
    name = Column(String, nullable=True)
    mcc = Column(Integer, ForeignKey('mcc.mcc'))
    amount = Column(Numeric)

class Mcc(Base):
    __tablename__ = 'mcc'
    mcc = Column(Integer, primary_key=True)
    description = Column(String)

engine = create_engine('sqlite:///cc.db')
Base.metadata.create_all(engine)

@singleton
class TransactionDb:
    def connect(self, conn_str):
        self.engine = create_engine(conn_str)
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(self.engine)()

    def add_many(self, things):
        for thing in things:
            self.session.merge(thing)
        self.session.commit()

