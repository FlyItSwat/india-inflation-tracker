"""Inflation analytics using index levels, not sums of annual inflation rates."""
import pandas as pd

def validate_data(df):
    needed = {'Date','Headline','Food','Housing','Fuel'}
    if not needed.issubset(df.columns):
        raise ValueError('Missing columns: ' + ', '.join(sorted(needed-set(df.columns))))
    result = df.copy()
    result['Date'] = pd.to_datetime(result['Date'], errors='raise')
    result = result.sort_values('Date').reset_index(drop=True)
    if result['Date'].duplicated().any():
        raise ValueError('Dates must be unique')
    for col in sorted(needed-{'Date'}):
        result[col] = pd.to_numeric(result[col], errors='raise')
        if result[col].isna().any() or (result[col] <= 0).any():
            raise ValueError(f'{col} index levels must be positive')
    return result

def add_inflation(df):
    df = validate_data(df)
    for col in ['Headline','Food','Housing','Fuel']:
        df[f'{col} YoY (%)'] = (df[col]/df[col].shift(12)-1)*100
        df[f'{col} MoM (%)'] = (df[col]/df[col].shift(1)-1)*100
    return df

def purchasing_power(amount, annual_inflation_percent, years):
    if amount < 0 or years < 0 or annual_inflation_percent <= -100:
        raise ValueError('Invalid amount, years, or inflation')
    return amount / ((1+annual_inflation_percent/100)**years)

def real_income_change(nominal_income_growth_percent, inflation_percent):
    if nominal_income_growth_percent <= -100 or inflation_percent <= -100:
        raise ValueError('Growth and inflation must exceed -100%')
    return ((1+nominal_income_growth_percent/100)/(1+inflation_percent/100)-1)*100

def period_inflation(start_index, end_index):
    if start_index <= 0 or end_index <= 0:
        raise ValueError('Index levels must be positive')
    return (end_index/start_index-1)*100
