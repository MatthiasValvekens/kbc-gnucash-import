import csv
import decimal
from collections import OrderedDict
from decimal import Decimal, DecimalException


__all__ = ["CIDictReader", "parse_amount"]


def parse_amount(amount_str: str) -> decimal.Decimal:
    if amount_str is None:
        raise ValueError
    # ugly, but Decimal doesn't really support formatting parameters
    # (unless we involve the locale module)
    amt_str = amount_str.replace(",", ".")

    try:
        rd = Decimal(amt_str).quantize(Decimal(".01"))
    except (ValueError, IndexError, DecimalException):
        raise ValueError
    return rd


class CIDictReader(csv.DictReader):
    def __next__(self):
        row = super().__next__()
        # minuscule computational overhead
        return CIOrderedDict(row)


class CIStr(str):
    def __eq__(self, other):
        if not isinstance(other, str):
            return False
        return self.casefold() == other.casefold()

    def __hash__(self):
        return hash(self.casefold())


def as_cistr(key):
    return key if isinstance(key, CIStr) else CIStr(key)


class CIOrderedDict(OrderedDict):
    # inspired by https://stackoverflow.com/a/32888599/4355619

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._convert_keys()

    def __getitem__(self, key):
        return super().__getitem__(as_cistr(key))

    def __setitem__(self, key, value):
        super().__setitem__(as_cistr(key), value)

    def __delitem__(self, key):
        return super().__delitem__(as_cistr(key))

    def __contains__(self, key):
        return super().__contains__(as_cistr(key))

    def pop(self, key, *args, **kwargs):
        return super().pop(as_cistr(key), *args, **kwargs)

    def get(self, key, *args, **kwargs):
        return super().get(as_cistr(key), *args, **kwargs)

    def setdefault(self, key, *args, **kwargs):
        return super().setdefault(as_cistr(key), *args, **kwargs)

    def update(self, e=None, **kwargs):
        super().update(self.__class__(e or {}))
        super().update(self.__class__(**kwargs))

    def _convert_keys(self):
        for k in list(self.keys()):
            v = super().pop(k)
            self.__setitem__(k, v)
