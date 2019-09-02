from csv import DictReader
from recordclass import recordclass
from decimal import *


ACCOUNTS = {
    'SAVINGS': 'X93788759',
    'INVESTMENT': 'X94686157',
    'IRA': '225809769',
    'ROTH_IRA': '231294290',
    'IRA_401K': '80517',
    'ESPP': 'NIELSEN ESPP',
    'HSA': '233164897',
}

TAXABLE_ACCOUNTS = ['SAVINGS', 'INVESTMENT']

class FidelityAccount:
    def __init__(self, name, positions):
        self.name = name
        self.positions = positions
        self._calc_current_value()

    @property
    def total(self):
        return sum([position.Current_Value for position in self.positions])

    def is_taxable(self):
        if self.name in TAXABLE_ACCOUNTS:
            return True
        return False

    @staticmethod
    def translate_field(field):
        return field.strip(' ').translate(str.maketrans(' /\'', '___'))

    def _calc_current_value(self):
        for position in self.positions:
            try:
                position.Current_Value = self._to_Decimal(position.Current_Value)
            except (InvalidOperation, AttributeError): # n/a or none value
                position.Current_Value = Decimal(0)

    def _to_Decimal(self, value):
        if(isinstance(value, Decimal)):
                return value
        return Decimal(value.replace('$', ''))



class FidelityStatement(FidelityAccount):

    def __init__(self, csv_str):
        csv_iter = csv_str.split('\n')
        self.reader = DictReader(csv_iter)
        fields = [FidelityStatement.translate_field(name) for name in self.reader.fieldnames]
        self.SecurityPosition = recordclass('SecurityPosition', fields)

        positions = []
        for row in self.reader:
            row = {FidelityStatement.translate_field(key): value for key, value in row.items()}
            positions.append(self.SecurityPosition(**row))
        super().__init__(None, positions)
        self.accounts =  [FidelityAccount(account_name, self.account_positions(account_name)) for account_name in ACCOUNTS.keys()]

    def account_positions(self, account_name):
        return [position for position in self.positions if position.Account_Name_Number == ACCOUNTS[account_name]]

#with open('input/Portfolio_Position_Aug-12-2019.csv') as f:
#    fs = FidelityStatement(f.read())
#    print(fs.total)
#    for account in fs.accounts:
#        print(f'{account.name}: {account.total}')
