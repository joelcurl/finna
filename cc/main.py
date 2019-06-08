from visa import TransactionDb
from elan_statement import ElanStatementReader, MccReader
import categories

cc_reader = None
with open('statements/download.csv') as f:
    cc_reader = ElanStatementReader(f.read())
mcc_reader = None
with open('mcc-codes/mcc_codes.csv') as f:
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
import pdb; pdb.set_trace()
print('')
