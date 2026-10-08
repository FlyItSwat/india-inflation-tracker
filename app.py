import pandas as pd
import plotly.express as px
import streamlit as st
from calculations import add_inflation, purchasing_power, real_income_change, period_inflation

st.set_page_config(page_title='India Inflation Tracker', page_icon='🇮🇳', layout='wide')
st.title('India Inflation Tracker')
st.warning('The bundled dataset is SYNTHETIC and is NOT official Indian CPI data. Upload an official monthly CPI-index CSV for real analysis.')
st.caption('Upload monthly index levels with columns: Date, Headline, Food, Housing, Fuel. Use a consistent index base and definitions.')
upload = st.file_uploader('Optional: upload monthly CPI index CSV', type='csv')
try:
    df = add_inflation(pd.read_csv(upload if upload is not None else 'sample_cpi.csv'))
except Exception as exc:
    st.error(f'Invalid dataset: {exc}')
    st.stop()

st.subheader('CPI index levels')
category = st.selectbox('Category', ['Headline','Food','Housing','Fuel'])
fig = px.line(df, x='Date', y=category, title=f'{category} CPI index')
st.plotly_chart(fig, use_container_width=True)
valid = df.dropna(subset=[f'{category} YoY (%)'])
if not valid.empty:
    st.metric('Latest year-over-year inflation', f"{valid.iloc[-1][f'{category} YoY (%)']:.2f}%")
    st.metric('Inflation over available sample', f'{period_inflation(df[category].iloc[0], df[category].iloc[-1]):.2f}%')
    st.subheader('Year-over-year inflation')
    st.plotly_chart(px.line(df, x='Date', y=[f'{x} YoY (%)' for x in ['Headline','Food','Housing','Fuel']], title='YoY inflation by category'), use_container_width=True)
    st.subheader('Inflation heatmap')
    heat = df[['Date',f'{category} YoY (%)']].dropna().copy()
    heat['Year'] = heat['Date'].dt.year
    heat['Month'] = heat['Date'].dt.strftime('%b')
    heat['MonthNum'] = heat['Date'].dt.month
    heat = heat.sort_values('MonthNum')
    pivot = heat.pivot(index='Year', columns='Month', values=f'{category} YoY (%)')
    st.plotly_chart(px.imshow(pivot, text_auto='.1f', aspect='auto', color_continuous_scale='RdBu_r', title='YoY inflation (%)'), use_container_width=True)
else:
    st.info('At least 13 consecutive monthly observations are needed for a year-over-year comparison.')

st.subheader('Purchasing power calculator')
a,b,c = st.columns(3)
amount = a.number_input('Amount today (₹)', min_value=0.0, value=100000.0, step=1000.0)
rate = b.number_input('Assumed annual inflation (%)', min_value=-99.0, max_value=100.0, value=6.0)
years = c.slider('Years', 0, 50, 10)
st.metric('Future purchasing power in today’s ₹', f'₹{purchasing_power(amount,rate,years):,.2f}')
st.caption('This measures the purchasing power of a fixed nominal amount after the specified years.')
st.subheader('Nominal vs real income growth')
wage = st.number_input('Nominal income growth (%)', min_value=-99.0, max_value=100.0, value=8.0)
infl = st.number_input('Inflation over the same period (%)', min_value=-99.0, max_value=100.0, value=6.0)
st.metric('Real income growth', f'{real_income_change(wage,infl):.2f}%')
st.download_button('Download computed monthly data', df.to_csv(index=False).encode(), 'inflation_analysis.csv', 'text/csv')
st.caption('Method: YoY = (index / index 12 months ago − 1) × 100. Data must be consecutive monthly observations. No seasonal adjustment is applied.')
