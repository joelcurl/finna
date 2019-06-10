from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from singleton_decorator import singleton
from memoized_property import memoized_property
from csv import DictReader

class MccReader:
    def __init__(self, csv_str):
        csv_iter = csv_str.split('\n')
        self.reader = DictReader(csv_iter)

    @memoized_property
    def codes(self):
        return [Mcc(mcc = int(row['mcc']), description = row['edited_description']) for row in self.reader]

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

