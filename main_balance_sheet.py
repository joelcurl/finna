from statements.balance_sheet_statement import BalanceSheetStatement
from banking.macu_statement import MacuStatement
from brokerage.fidelity_statement import FidelityStatement, ACCOUNTS
from paystubs.reader import AcmePaystubReader
from paystubs.wages import AcmePaystub
from property.mac_book import MacBook
from property.kelly_valuator import ChevyMalibu05Valuator
from cc.visa import TransactionDb, MccReader
from cc.elan_statement import ElanStatementReader
from cc.statement import CcStatement
from liabilities.timed_liability import concept_lease

bs = BalanceSheetStatement('2019-09-01')

'''Assets'''

with open('banking/input/ExportedTransactions.csv') as f:
    bs.add_bank_statement(MacuStatement(f.read()))
with open('banking/input/ExportedTransactions (1).csv') as f:
    bs.add_bank_statement(MacuStatement(f.read()))
with open('banking/input/ExportedTransactions (2).csv') as f:
    bs.add_bank_statement(MacuStatement(f.read()))

with open('brokerage/input/Portfolio_Position_Aug-12-2019.csv') as f:
    brokerage = FidelityStatement(f.read())
    for account in ACCOUNTS.keys():
        if account == 'SAVINGS' or account == 'INVESTMENT':
            bs.add_brokerage_statement_to_current(account, brokerage.accounts[account])
        else:
            bs.add_brokerage_statement_to_noncurrent(account, brokerage.accounts[account])

with open('paystubs/input/Paystub_201912.pdf', 'rb') as f:
    bs.add_paystub(AcmePaystub(AcmePaystubReader(f).text))

bs.add_fixed_asset(MacBook())
bs.add_fixed_asset(ChevyMalibu05Valuator(milage=150000, sell_zip=84102))

'''Liabilities'''
db = TransactionDb()
db.connect('sqlite:///cc/cc.db')
with open('cc/mcc-codes/mcc_codes.csv') as mcc:
    with open('cc/input/download.csv') as cc:
        bs.add_cc_statement(CcStatement(ElanStatementReader(cc.read()), MccReader(mcc.read())))

bs.add_timed_liability(concept_lease)

print(bs.to_table())
