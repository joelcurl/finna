from statements.income_statement import IncomeStatement
from paystubs.reader import AcmePaystubReader
from paystubs.wages import AcmePaystub
from liabilities.timed_liability import concept_lease
from cc.visa import TransactionDb, MccReader
from cc.elan_statement import ElanStatementReader
from cc.statement import CcStatement
from decimal import *

getcontext().prec = 6 # to avoid printing too many decimal places

i = IncomeStatement('2019-09-01', '2019-10-01')

with open('paystubs/input/Paystub_201912.pdf', 'rb') as f:
    i.add_paystub(AcmePaystub(AcmePaystubReader(f).text))

i.add_timed_liability(concept_lease)

db = TransactionDb()
db.connect('sqlite:///cc/cc.db')
with open('cc/mcc-codes/mcc_codes.csv') as mcc:
    with open('cc/input/download.csv') as cc:
        i.add_cc_statement(CcStatement(ElanStatementReader(cc.read()), MccReader(mcc.read())))

print(i.to_table())
