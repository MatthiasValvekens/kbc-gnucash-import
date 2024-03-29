"""
Simple data model & serialisation code for one-to-many transactions in QIF
files.
"""

import decimal
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from typing import Optional, List, TextIO


__all__ = ["Account", "Transfer", "Split", "declare_accounts_and_transactions"]


@dataclass(frozen=True)
class Account:
    label: str
    is_income: bool = False

    def declare(self, out: TextIO):
        out.write("!Account\n")
        out.write(f"N{self.label}\n")
        if self.is_income:
            out.write("I\n")
        out.write("^\n\n")


@dataclass(frozen=True)
class Split:
    amount: decimal.Decimal
    target_account: Account
    split_memo: Optional[str] = None

    def declare(self, out: TextIO):
        out.write(f"S{self.target_account.label}\n")
        if self.split_memo:
            out.write(f"E{self.split_memo}\n")
        out.write(f"${self.amount}\n")


@dataclass(frozen=True)
class Transfer:
    amount: decimal.Decimal
    asset_account: Account
    memo: str
    transaction_date: date
    splits: List[Split]

    def declare(self, out: TextIO):
        out.write(f"D{self.transaction_date.strftime('%Y-%m-%d')}\n")
        out.write(f"T{self.amount}\n")
        out.write(f"M{self.memo}\n")
        for split in self.splits:
            split.declare(out)
        out.write("^\n\n")


def declare_accounts_and_transactions(transfers: List[Transfer], out: TextIO):

    # sort by asset account
    by_account = defaultdict(list)
    for t in transfers:
        by_account[t.asset_account].append(t)

    for account, ts in by_account.items():
        # Declare the asset account
        out.write("!Type:Cat\n")
        account.declare(out)

        # Then proceed with transactions
        out.write("!Type:Bank\n")
        for t in ts:
            t.declare(out)
