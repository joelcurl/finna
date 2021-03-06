from .visa import VisaTransaction, Mcc, TransactionDb
import sys, inspect
from decimal import Decimal
from memoized_property import memoized_property

# return all category classes mentioned here, less special ones like MccCategory and SuperCategory
def categories():
    do_not_return_these = [MccCategory, SuperCategory]
    is_class_member = lambda member: inspect.isclass(member) and member.__module__ == __name__
    cat_classes = inspect.getmembers(sys.modules[__name__], is_class_member)
    for remove_this in do_not_return_these:
        cat_classes.remove((remove_this.__name__, remove_this))
    return {cat_tuple[0]: cat_tuple[1] for cat_tuple in cat_classes}

class MccCategory:
    def __init__(self, mcc):
        self.mcc = mcc

    @memoized_property
    def description(self):
        return self.db_session.query(Mcc).filter(Mcc.mcc == self.mcc).one().description

    def matching_transactions(self):
        return self.db_session.query(VisaTransaction).filter(VisaTransaction.mcc == self.mcc).all()

    def to_dict(self):
        matches = self.matching_transactions()
        total = sum([transaction.amount for transaction in matches])
        if matches:
            return {'transactions': [t.to_dict() for t in matches], 'total': total}
        else:
            return {}

    def in_category(self, mcc):
        return mcc == self.mcc

    @property
    def total(self):
        return self.to_dict().get('total', Decimal(0))

    @property
    def db_session(self):
        return TransactionDb().session

class SuperCategory:
    @property
    def name(self):
        return type(self).__name__

    @property
    def description(self):
        return self.name

    def to_dict(self):
        matches = {}
        for t in self.types:
            d = t.to_dict()
            if d:
                matches[t.description] = d
        return matches

    def in_category(self, mcc):
        for mcc_category in self.types:
            if mcc_category.in_category(mcc):
                return True
        return False

    @property
    def total(self):
        _total = Decimal(0)
        for t in self.types:
            _total += t.total
        return _total

class Food(SuperCategory):
    types = [
            MccCategory(5411),
            MccCategory(5541),
            MccCategory(5812),
            MccCategory(5814),
            ]

class Medical(SuperCategory):
    types = [
            MccCategory(5047),
            MccCategory(8011),
            MccCategory(8021),
            MccCategory(8031),
            MccCategory(8041),
            MccCategory(8042),
            MccCategory(8043),
            MccCategory(8044),
            MccCategory(8049),
            MccCategory(8050),
            MccCategory(8062),
            MccCategory(8071),
            MccCategory(8099),
            ]

class Automotive(SuperCategory):
    types = [
            MccCategory(5013),
            MccCategory(5532),
            MccCategory(5533),
            MccCategory(5542),
            MccCategory(5551),
            MccCategory(5561),
            MccCategory(5571),
            MccCategory(5592),
            MccCategory(5598),
            MccCategory(5599),
            MccCategory(7538),
            ]

class Utilities(SuperCategory):
    types = [
            MccCategory(4814),
            MccCategory(4900),
            MccCategory(5960),
            MccCategory(6300),
            MccCategory(6381),
            MccCategory(6399),
            ]

class Education(SuperCategory):
    types = [
            MccCategory(5192),
            MccCategory(5942),
            MccCategory(8211),
            MccCategory(8220),
            MccCategory(8241),
            MccCategory(8244),
            MccCategory(8249),
            MccCategory(8299),
            ]

class Entertainment(SuperCategory):
    types = [
            MccCategory(4899),
            MccCategory(5815),
            MccCategory(5816),
            MccCategory(5816),
            MccCategory(5817),
            MccCategory(5818),
            MccCategory(7994),
            ]

class Luxuries(SuperCategory):
    types = [
            MccCategory(5921),
            MccCategory(5993),
            ]

class Other(SuperCategory):
    types = []

    def __init__(self):
        categorized_mccs = self.__categorized_mccs()
        all_mccs = set([row.mcc for row in TransactionDb().session.query(Mcc).all()])
        other_mccs = all_mccs - categorized_mccs
        for mcc in other_mccs:
            self.types.append(MccCategory(mcc))

    def __categorized_mccs(self):
        parent_cls = self.__class__.__bases__[0]
        subclasses = parent_cls.__subclasses__()
        subclasses.remove(self.__class__) # don't iterate through yourself

        categorized_mccs = []
        for sub_cls in subclasses:
            for t in sub_cls().types:
                if isinstance(t, MccCategory):
                    categorized_mccs.append(t.mcc)
        return set(categorized_mccs)

