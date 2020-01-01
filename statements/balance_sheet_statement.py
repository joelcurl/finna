from .util import is_current_date
from recordclass import recordclass
from datetime import date
from decimal import *
from tabulate import tabulate
from taxes.tax import SingleTax as Tax

class BalanceSheetStatement:
    Assets = recordclass('Assets', 'current noncurrent')
    Liabilities = recordclass('Liabilities', 'current noncurrent')
    CurrentAssets = recordclass('CurrentAssets', 'cash brokerage')
    NoncurrentAssets = recordclass('NoncurrentAssets', 'brokerage taxes fixed')
    CurrentLiabilities = recordclass('CurrentLiabilities', 'credit leases')
    NoncurrentLiabilities = recordclass('NoncurrentLiabilities', 'taxes loans education')

    TaxAssets = recordclass('TaxAssets', 'federal_withheld state_withheld')
    TaxLiabilities = recordclass('TaxLiabilities', 'federal_tax_ytd state_tax_ytd')

    def __init__(self, then, now):
        self.then = then
        self.now = now
        self.assets = self.Assets(
                self.CurrentAssets(Decimal(0), {}),
                self.NoncurrentAssets({}, self.TaxAssets(Decimal(0), Decimal(0)), Decimal(0))
        )
        self.liabilities = self.Liabilities(
                self.CurrentLiabilities({}, Decimal(0)),
                self.NoncurrentLiabilities(self.TaxLiabilities(Decimal(0), Decimal(0)), Decimal(0), Decimal(0))
        )
        self.paystub_dates = {}
        self.paystub_taxable = {}
        self.cc_dates = {}
        self.miscellaneous_income = Decimal(0)
        self.preferred_taxable_income = Decimal(0)

    def add_bank_statement(self, statement):
        self.assets.current.cash += statement.balance

    def add_brokerage_statement(self, statement):
        if statement.is_taxable():
            self.assets.current.brokerage[statement.name] = statement.total
        else:
            self.assets.noncurrent.brokerage[statement.name] = statement.total

    def add_paystub(self, paystub):
        if not is_current_date(key=paystub.employer, past_dates=self.paystub_dates, today=paystub.pay_period.end):
            return
        if paystub.employer in self.paystub_taxable: # newer ytd info for employer already added
            self.assets.noncurrent.taxes.federal_withheld = paystub.ytd.taxes.federal_withheld
            self.assets.noncurrent.taxes.state_withheld = paystub.ytd.taxes.state_withheld
        else: # new employer
            self.assets.noncurrent.taxes.federal_withheld += paystub.ytd.taxes.federal_withheld
            self.assets.noncurrent.taxes.state_withheld += paystub.ytd.taxes.state_withheld
        self.paystub_taxable[paystub.employer] = paystub.ytd.taxes.taxable_wages

    def add_fixed_asset(self, asset):
        self.assets.noncurrent.fixed += asset.mark_to_market()

    def add_cc_statement(self, statement):
        if not is_current_date(key=statement.creditor, past_dates=self.cc_dates, today=statement.end):
            return
        self.liabilities.current.credit[statement.creditor] = Decimal(0)
        for transaction in statement.transactions:
            if self.then <= transaction.date and transaction.date <= self.now:
                self.liabilities.current.credit[statement.creditor] += transaction.amount
        for payment in statement.payments:
            if self.then <= payment.date and payment.date <= self.now:
                self.liabilities.current.credit[statement.creditor] += payment.amount

    def add_timed_liability(self, lease):
        self.liabilities.current.leases += -lease.amount_remaining(self.now)

    def add_static_liability(self, liability):
        self.liabilities.noncurrent.education += -liability.amount_remaining(self.now)

    @property
    def current_asset_total(self):
        return sum([
            self.assets.current.cash,
            sum(self.assets.current.brokerage.values()),
        ])

    @property
    def noncurrent_asset_total(self):
        return sum([
            sum(self.assets.noncurrent.brokerage.values()),
            self.tax_withheld,
            self.assets.noncurrent.fixed,
        ])

    @property
    def asset_total(self):
        return sum([self.current_asset_total, self.noncurrent_asset_total])

    @property
    def current_liability_total(self):
        return sum([
            self.outstanding_credit,
            self.liabilities.current.leases,
        ])

    @property
    def noncurrent_liability_total(self):
        return sum([
            self.tax_burden,
            self.liabilities.noncurrent.loans,
            self.liabilities.noncurrent.education,
        ])

    @property
    def ordinary_taxable_income(self):
        return sum(self.paystub_taxable.values()) + self.miscellaneous_income

    @property
    def tax_withheld(self):
        return sum([self.assets.noncurrent.taxes.federal_withheld, self.assets.noncurrent.taxes.state_withheld])

    @property
    def federal_tax_burden(self):
        tax_burden = -Tax.calc_income_tax(self.ordinary_taxable_income)
        self.liabilities.noncurrent.taxes.federal_tax_ytd = tax_burden
        return tax_burden

    @property
    def state_tax_burden(self):
        tax_burden = -Tax.calc_flat_tax(self.ordinary_taxable_income, 0.0495)
        self.liabilities.noncurrent.taxes.state_tax_ytd = tax_burden
        return tax_burden

    @property
    def tax_burden(self):
        return sum([self.federal_tax_burden, self.state_tax_burden])

    @property
    def liability_total(self):
        return sum([self.current_liability_total, self.noncurrent_liability_total])

    @property
    def equity(self):
        return self.asset_total + self.liability_total # this is actually assets - liabilities, as liabilities are negative values

    @property
    def outstanding_credit(self):
        return sum(self.liabilities.current.credit.values())

    def to_table(self):
        current_asset_table = [[f'Brokerage {account_name}', value] for account_name, value in self.assets.current.brokerage.items()]
        current_asset_table.insert(0, ['Current Assets', 'Amount'])
        current_asset_table.insert(1, ['Cash', self.assets.current.cash])
        current_asset_table.append(['Total', self.current_asset_total])

        noncurrent_asset_table = [[f'Brokerage {account_name}', value] for account_name, value in self.assets.noncurrent.brokerage.items()]
        noncurrent_asset_table.insert(0, ['Noncurrent Assets', 'Amount'])
        noncurrent_asset_table.append(['Federal Tax Withheld', self.assets.noncurrent.taxes.federal_withheld])
        noncurrent_asset_table.append(['State Tax Withheld', self.assets.noncurrent.taxes.state_withheld])
        noncurrent_asset_table.append(['Fixed Assets', self.assets.noncurrent.fixed])
        noncurrent_asset_table.append(['Total', self.noncurrent_asset_total])

        tables = [
                [
                    ['Balance Sheet', f'at {self.now}']
                ],

                current_asset_table,
                noncurrent_asset_table,

                [
                    ['', 'Total'],
                    ['Assets', self.asset_total],
                ],

                [
                    ['Current Liabilities', 'Amount'],
                    ['Outstanding Credit', self.outstanding_credit],
                    ['Leases', self.liabilities.current.leases],
                    ['Total', self.current_liability_total],
                ],
                [
                    ['Noncurrent Liabilities', 'Amount'],
                    ['Loans', self.liabilities.noncurrent.loans],
                    ['Education', self.liabilities.noncurrent.education],
                    ['Federal Tax YTD', self.federal_tax_burden],
                    ['State Tax YTD', self.state_tax_burden],
                    ['Total', self.noncurrent_liability_total],
                ],
                [
                    ['', 'Total'],
                    ['Liabilities', self.liability_total],
                    ['Personal Equity', self.equity],
                ],

        ]

        formatted_tables = ''
        for table in tables:
            formatted_tables += tabulate(table, tablefmt='fancy_grid', floatfmt='.2f', headers='firstrow') + '\n\n'
        return formatted_tables

