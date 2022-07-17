from datetime import datetime, date

from .qif import Transfer, Account, Split
from .util import CIDictReader, parse_amount
import re

__all__ = ["KBCExtractor"]


SUPERFLUOUS_WHITESPACE = re.compile(r"\s\s+")


def _parse_date(date_str: str) -> date:
    return datetime.strptime(date_str, "%d/%m/%Y").date()


class KBCExtractor:
    delimiter = ";"
    description_field = "omschrijving"
    amount_field = "bedrag"
    date_field = "datum"
    memo_field = "vrije mededeling"
    # extraction pattern for debit card transactions
    memo_pattern = re.compile(
        r" OM \d\d\.\d\d UUR (?P<memo>.+) MET KBC-DEBETKAART ([X\d]+ )+"
        r"(KAARTHOUDER: (?P<cardholder>.+))?"
    )

    def __init__(
        self,
        asset_account: Account,
        target_account_income: Account,
        target_account_expenses: Account,
    ):
        self.asset_account = asset_account
        self.target_account_income = target_account_income
        self.target_account_expenses = target_account_expenses

    def ingest(self, csv_in):
        csv = CIDictReader(csv_in, delimiter=self.delimiter)

        for row in csv:
            amount = parse_amount(row[self.amount_field])
            acct = (
                self.target_account_income
                if amount > 0
                else self.target_account_expenses
            )
            split = Split(amount=amount, target_account=acct)
            yield Transfer(
                amount=amount,
                asset_account=self.asset_account,
                splits=[split],
                memo=self.extract_memo(row),
                transaction_date=_parse_date(row[self.date_field]),
            )

    def extract_memo(self, row):
        memo_content = row[self.memo_field].strip()
        if memo_content:
            return memo_content

        descr = self.extract_memo_from_description(row[self.description_field])
        return SUPERFLUOUS_WHITESPACE.sub(" ", descr)

    def extract_memo_from_description(self, description_content):
        m = self.memo_pattern.search(description_content)
        if m is None:
            return description_content.strip()
        memo = m.group("memo").strip()
        cardholder = m.group("cardholder")
        if cardholder is not None:
            cardholder = cardholder.strip()

        if cardholder:
            return f"{memo} (CH: {cardholder})"
        else:
            return memo
