from cc.visa import TransactionDb, MccReader
from cc.elan_statement import ElanStatementReader
from cc.statement import CcStatement
from paystubs.reader import AcmePaystubReader
from paystubs.wages import AcmePaystub
from statements.cash_flow_statement import CashFlowStatement

db = TransactionDb()
db.connect('sqlite:///cc/cc.db') # todo maybe this should be in-mem?
cc_statement = None
with open('cc/mcc-codes/mcc_codes.csv') as mcc:
    with open('cc/input/download.csv') as cc:
        cc_reader = ElanStatementReader(cc.read())
        mcc_reader = MccReader(mcc.read())
        cc_statement = CcStatement(cc_reader, mcc_reader)
paystub = None
with open('paystubs/input/Paystub_201912.pdf', 'rb') as f:
    paystub_reader = AcmePaystubReader(f)
    paystub = AcmePaystub(paystub_reader.text)

cfs = CashFlowStatement('beg time', 'end time', 0)
cfs.add_paystub(paystub.current)
cfs.add_cc_statement(cc_statement)

print(cfs.to_table())

