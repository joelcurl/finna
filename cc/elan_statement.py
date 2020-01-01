from cc.visa import VisaTransaction
from decimal import Decimal
from datetime import datetime
from collections import namedtuple
from memoized_property import memoized_property
from csv import DictReader

class ElanStatementReader:
    Transaction = namedtuple('Transaction', 'date isDebit name mcc amount id')

    def __init__(self, csv_str):
        csv_iter = csv_str.split('\n')
        self.reader = DictReader(csv_iter)
        self.ElanTransaction = namedtuple('ElanTransaction', self.reader.fieldnames)
        self.creditor = 'Elan'
        self.transactions = []
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
                continue # likely a payment, not a purchase
            ts.append(self.Transaction(date, isDebit, t.Name, mcc, amount, id))
        return ts

    @memoized_property
    def elan_payments(self):
        return [self.Transaction(
            datetime.strptime(t.Date, '%m/%d/%Y').date(),
            t.Transaction == 'DEBIT',
            t.Name,
            -1,
            Decimal(t.Amount),
            f'{t.Date}-{t.Amount}',
            ) for t in self.transactions if t.Transaction == 'CREDIT']

    @memoized_property
    def visa_transactions(self):
        return [VisaTransaction(**dict(t._asdict())) for t in self.elan_transactions]

    @memoized_property
    def payments(self):
        return [VisaTransaction(**dict(p._asdict())) for p in self.elan_payments]



