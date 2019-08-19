from .visa import TransactionDb, VisaTransaction, Mcc
from decimal import Decimal
from datetime import datetime
from collections import namedtuple
from memoized_property import memoized_property
from csv import DictReader

class ElanStatementReader:
    Transaction = namedtuple('Transaction', 'date isDebit name mcc amount id')
    transactions = []

    def __init__(self, csv_str):
        csv_iter = csv_str.split('\n')
        self.reader = DictReader(csv_iter)
        self.ElanTransaction = namedtuple('ElanTransaction', self.reader.fieldnames)
        self.creditor = 'Elan'
        for row in self.reader:
            self.transactions.append(self.ElanTransaction(**row))

    @memoized_property
    def elan_transactions(self):
        ts = []
        for t in self.transactions:
            date = datetime.strptime(t.Date, '%m/%d/%Y').date()
            isDebit = t.Transaction == 'DEBIT'
            memo = t.Memo.split(';')
            mcc = int(memo[1])
            amount = Decimal(t.Amount)
            try:
                id = str(int(memo[0]))
            except ValueError:
                id = '{} ${}'.format(date, amount) # use date and amount as id if 'INTERNET' payment or id is otherwise missing
            ts.append(self.Transaction(date, isDebit, t.Name, mcc, amount, id))
        return ts

    @memoized_property
    def visa_transactions(self):
        return [VisaTransaction(**dict(t._asdict())) for t in self.elan_transactions]



