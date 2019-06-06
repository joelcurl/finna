

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

Base = declarative_base()

class VisaTransaction(Base):
    __tablename__ = 'transaction'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    isDebit = Column(Boolean)
    name = Column(String, nullable=True)
    mcc = Column(Integer, ForeignKey('mcc.mcc'))
    amount = Column(Integer)

class Mcc(Base):
    __tablename__ = 'mcc'
    mcc = Column(Integer, primary_key=True)
    description = Column(String)

engine = create_engine('sqlite:///cc.db')
Base.metadata.create_all(engine)


from collections import namedtuple
import csv

Transaction = namedtuple('Transaction', 'date isDebit name mcc amount')

class ElanStatementReader:
    elan_transactions = []

    def __init__(self, csv_str):
        csv_iter = csv_str.split('\n')
        self.reader = csv.DictReader(csv_iter)
        self.Transaction = namedtuple('ElanTransaction', self.reader.fieldnames)
        for row in self.reader:
            self.elan_transactions.append(self.Transaction(**row))

    def transactions(self):
        ts = []
        for t in self.elan_transactions:
            mcc = int(t.Memo.split(';')[1])
            isDebit = t.Transaction == 'DEBIT'
            ts.append(Transaction(t.Date, isDebit, t.Name, mcc, t.Amount))
        return ts


reader = None
with open('statements/download.csv') as f:
    reader = ElanStatementReader(f.read())

import pdb; pdb.set_trace()
print('')
