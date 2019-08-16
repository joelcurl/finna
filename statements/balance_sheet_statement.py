from recordclass import recordclass
from decimal import *
from tabulate import tabulate
from taxes.tax import SingleTax as Tax

class BalanceSheetStatement:
    Assets = recordclass('Assets', 'current noncurrent')
    Liabilities = recordclass('Liabilities', 'current noncurrent')
    CurrentAssets = recordclass('CurrentAssets', 'cash brokerage')
    NoncurrentAssets = recordclass('NoncurrentAssets', 'brokerage taxes fixed')
    CurrentLiabilities = recordclass('CurrentLiabilities', 'credit leases')
    NoncurrentLiabilities = recordclass('NoncurrentLiabilities', 'taxes loans')

    TaxAssets = recordclass('TaxAssets', 'federal_withheld state_withheld')
    TaxLiabilities = recordclass('TaxLiabilities', 'federal_tax_ytd state_tax_ytd')
    ordinary_taxable_income = Decimal(0)
    preferred_taxable_income = Decimal(0)

    def __init__(self, now):
        self.now = now
        self.assets = self.Assets(
                self.CurrentAssets(Decimal(0), {}),
                self.NoncurrentAssets({}, self.TaxAssets(Decimal(0), Decimal(0)), Decimal(0))
        )
        self.liabilities = self.Liabilities(
                self.CurrentLiabilities(Decimal(0), Decimal(0)),
                self.NoncurrentLiabilities(self.TaxLiabilities(Decimal(0), Decimal(0)), Decimal(0))
        )

    def add_bank_statement(self, statement):
        self.assets.current.cash += statement.balance

    def add_brokerage_statement_to_current(self, name, statement):
        self.assets.current.brokerage[name] = statement.total

    def add_brokerage_statement_to_noncurrent(self, name, statement):
        self.assets.noncurrent.brokerage[name] = statement.total

    def add_paystub(self, paystub):
        self.assets.noncurrent.taxes.federal_withheld = sum(paystub.ytd.taxes.fed_withholding.values())
        self.assets.noncurrent.taxes.state_withheld = sum(paystub.ytd.taxes.state_withholding.values())
        # todo liabilities somehow maybe use paystub.ytd.taxes.taxable_wages
        self.ordinary_taxable_income += sum(paystub.ytd.taxes.taxable_wages.values())

    def add_fixed_asset(self, asset):
        self.assets.noncurrent.fixed += asset.mark_to_market()

    def add_cc_statement(self, statement):
        self.liabilities.current.credit += statement.total

    def add_lease_liability(self, lease):
        self.liabilities.current.leases += -lease.amount_remaining(self.now)

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
            self.assets.noncurrent.taxes.federal_withheld,
            self.assets.noncurrent.taxes.state_withheld,
            self.assets.noncurrent.fixed,
        ])

    @property
    def asset_total(self):
        return sum([self.current_asset_total, self.noncurrent_asset_total])

    @property
    def current_liability_total(self):
        return sum([
            self.liabilities.current.credit,
            self.liabilities.current.leases,
        ])

    @property
    def noncurrent_liability_total(self):
        return sum([
            self.liabilities.noncurrent.taxes.federal_tax_ytd,
            self.liabilities.noncurrent.taxes.state_tax_ytd,
            self.liabilities.noncurrent.loans,
        ])

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
    def liability_total(self):
        return sum([self.current_liability_total, self.noncurrent_liability_total])

    @property
    def equity(self):
        return self.asset_total + self.liability_total # this is actually assets - liabilities, as liabilities are negative values

    def to_table(self):
        current_asset_table = [[f'Brokerage {account_name}', value] for account_name, value in self.assets.current.brokerage.items()]
        current_asset_table.insert(0, ['Noncurrent Assets', 'Amount'])
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
                    ['Outstanding Credit', self.liabilities.current.credit],
                    ['Leases', self.liabilities.current.leases],
                    ['Total', self.current_liability_total],
                ],
                [
                    ['Noncurrent Liabilities', 'Amount'],
                    ['Loans', self.liabilities.noncurrent.loans],
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

