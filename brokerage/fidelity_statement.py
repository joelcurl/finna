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

class FidelityAccount:
    def __init__(self, positions):
        self.positions = positions
        self._calc_current_value()

    @property
    def total(self):
        return sum([position.Current_Value for position in self.positions])

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
        next(self.reader) # skip header
        for row in self.reader:
            row = {FidelityStatement.translate_field(key): value for key, value in row.items()}
            positions.append(self.SecurityPosition(**row))
        super().__init__(positions)
        self.accounts =  {account_name: FidelityAccount(self.account_positions(account_name)) for account_name in ACCOUNTS.keys()}
        import pdb; pdb.set_trace()

    def account_positions(self, account_name):
        return [position for position in self.positions if position.Account_Name_Number == ACCOUNTS[account_name]]

#with open('input/Portfolio_Position_Aug-12-2019.csv') as f:
#    fs = FidelityStatement(f.read())
#    print(fs.total)
#    print(fs.accounts['SAVINGS'].total)
#    print(fs.accounts['INVESTMENT'].total)
#    print(fs.accounts['IRA'].total)
#    print(fs.accounts['ROTH_IRA'].total)
#    print(fs.accounts['IRA_401K'].total)
#    print(fs.accounts['ESPP'].total)
#    print(fs.accounts['HSA'].total)
#    print(fs.accounts)
