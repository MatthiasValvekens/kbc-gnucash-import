# Import KBC statements into GnuCash

## Summary

KBC is a Belgian bank that allows you to download statements in `.csv` format.

This repository contains a dumb but effective utility that reformats a KBC
`.csv` in `.qif` for importing data into GnuCash.

The script is quite stupid and will simply assign all income (resp. expenses)
to a fixed income (resp. expense) account.
The idea is that you then only have to split/assign transactions to their
appropriate expense accounts in the GnuCash GUI, instead of having to copy
over data from the KBC statement manually.

## Usage

This is pretty much how I invoke it:

```bash
python -m kbc2qif infile.csv "Assets:Current Assets:Checking" Income:UNPROCESSED Expenses:UNPROCESSED
```


## Requirements

Python 3.7+, currently no other dependencies.