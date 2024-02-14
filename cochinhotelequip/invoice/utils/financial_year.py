from datetime import datetime


def fiscal_year_4digit(current_date=datetime.now()):
    if current_date.month >= 4:
        fiscal_year = current_date.year
    else:
        fiscal_year = current_date.year - 1

    fiscal_year_code = str(fiscal_year)[2:] + str(fiscal_year + 1)[2:]

    return fiscal_year_code