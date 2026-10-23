import pandas as pd


def clean_leases(file_path):
    df = pd.read_csv(file_path)

    # Normalize text: trim both, standardize only the category column
    df['customer'] = df['customer'].str.strip().replace('', pd.NA)
    df['status'] = df['status'].str.strip().str.lower()

    # Dates: accept ISO or US format; impossible dates become NaT
    iso = pd.to_datetime(df['start_date'], format='%Y-%m-%d', errors='coerce')
    us = pd.to_datetime(df['start_date'], format='%m/%d/%Y', errors='coerce')
    df['start_date'] = iso.fillna(us)

    # Rates: strip $ and commas; non-numbers become NaN
    df['monthly_rate'] = pd.to_numeric(
        df['monthly_rate'].astype('string').str.replace(r'[\$,]', '', regex=True),
        errors='coerce',
    )

    # Exact duplicates are checked after normalizing
    df = df.drop_duplicates()

    # Every rejected row says why
    df['reject_reason'] = ''
    df.loc[df['customer'].isna(), 'reject_reason'] += 'missing customer; '
    df.loc[df['start_date'].isna(), 'reject_reason'] += 'invalid date; '
    df.loc[df['monthly_rate'].isna(), 'reject_reason'] += 'invalid rate; '

    valid = df['reject_reason'] == ''
    cleaned = df[valid].drop(columns='reject_reason').to_dict('records')
    rejected = df[~valid].to_dict('records')
    return cleaned, rejected