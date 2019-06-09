from cc.visa import TransactionDb
from cc.elan_statement import ElanStatementReader, MccReader
from cc import categories
from paystubs.reader import AcmePaystubReader
from paystubs.wages import AcmePaystub

cc_reader = None
with open('cc/statements/download.csv') as f:
    cc_reader = ElanStatementReader(f.read())
mcc_reader = None
with open('cc/mcc-codes/mcc_codes.csv') as f:
    mcc_reader = MccReader(f.read())

db = TransactionDb()
db.connect('sqlite:///cc.db')
db.add_many(cc_reader.visa_transactions)
db.add_many(mcc_reader.codes)

f = categories.Food()
d = f.to_dict()
dis = categories.Discretionary()
dis.to_dict()
o = categories.Other()

paystub_reader = None
with open('paystubs/statements/Paystub_201912.pdf', 'rb') as f:
    paystub_reader = AcmePaystubReader(f)
paystub = AcmePaystub(paystub_reader.text)

import pdb; pdb.set_trace()
print('')
