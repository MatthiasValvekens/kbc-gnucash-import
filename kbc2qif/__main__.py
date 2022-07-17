import sys
from .kbc import KBCExtractor
from .qif import Account, declare_accounts_and_transactions


def run():
    if len(sys.argv) != 5:
        print("Usage: kbc2qif CSV_IN ASSET_ACCT INCOME_ACCT EXPENSE_ACCT")
    csv_file = sys.argv[1]
    asset_acct = Account(sys.argv[2])
    income_acct = Account(sys.argv[3], is_income=True)
    expense_acct = Account(sys.argv[4])

    extractor = KBCExtractor(
        asset_account=asset_acct,
        target_account_income=income_acct,
        target_account_expenses=expense_acct,
    )

    with open(csv_file, "r") as inf:
        transfers = list(extractor.ingest(inf))

    declare_accounts_and_transactions(transfers, sys.stdout)


if __name__ == "__main__":
    run()
