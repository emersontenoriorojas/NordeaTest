# Customers Transactions Database Analysis
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import plotly.figure_factory as ff
import math
import numpy as np
from io import StringIO
import altair as alt
import pandas as pd

# region Data reading
pd.set_option('display.max_columns', None)
# Reading the customer database
data = pd.read_csv("transactions.csv", sep=";", header=None)
df = pd.DataFrame(data)
# endregion
# region Data quality
# Assigning columns name to the customers_trasactions database
df.columns = ['id_customer', 'debit_credit', 'amount', 'country_id']
# Replacing nan values, just some data quality control.
df['amount'] = df['amount'].replace(np.nan, 0)
# Just checking if all customers are identified
df['id_customer'] = df['id_customer'].replace(np.nan, "customer_id missing")
# Irregular Amount transaction
irregularAmount = df[(df['amount'] >= 1) & (df['amount'] <= 5)]
# endregion
# region Adding columns
# Assuming and assigning transaction order by customer
df['transaction_order'] = (df.groupby(['id_customer'])['id_customer'].rank(method='first')).astype(int)
# Creating a transaction_id just in case if i need to review details later. Concatenating id, amount, country and order
df['transaction_id'] = df['id_customer'].map(str) + df['amount'].map(str) + df['country_id'] + df[
    'transaction_order'].map(str)
# endregion
# region Customer Segmentation
# Income values most be all positive values for the analysis =>
df = df[df['amount'] > 0]
# Number of customers by country_counterparty. Needed to know in how many customers is distributed the number
# of transactions
df_nclientsbyCountry = df.groupby(['country_id'])['id_customer'].nunique().reset_index(name='number_customers')
# Average amount of transactions by country. Needed to compare with other transactions that
df_amountAVG = df.groupby(['country_id'])['amount'].mean().round(1).reset_index(name='amountAVG')
# Max amount on transactions by country
df_amountMax = df.groupby(['country_id'])['amount'].max().reset_index(name='amountMAX')
# Number of transactions per customer and country counterparty
df_ntransactioninMonthperCustomer = df.groupby(['id_customer', 'country_id'])['id_customer'].size().reset_index(
    name='nTransaction')
# Number of transactions per customer
df_ntransactionsAllbyCustomer = df.groupby(['id_customer'])['id_customer'].size().reset_index(
    name='nTransactions')
# Average transaction amount per customer
df_avgtransactionamountinMonthperCustomer_andCountry = df.groupby(
    ['id_customer', 'country_id'])['amount'].mean().round(0).reset_index(
    name='avgTransaction')
df_avgtransactionamountinMonthperCustomer = df.groupby(
    ['id_customer'])['amount'].mean().round(0).reset_index(
    name='avgTransaction')

df_AlertUnusualTransactions = pd.merge(df[['id_customer', 'amount', 'transaction_id', 'transaction_order']],
                                       df_avgtransactionamountinMonthperCustomer,
                                       how='left', left_on=['id_customer'],
                                       right_on=['id_customer'])
# Adding a binary alert to filter transactions that do not are usual to the customer financial behavior
df_AlertUnusualTransactions['Alert'] = np.where(
    df_AlertUnusualTransactions['amount'] > df_AlertUnusualTransactions['avgTransaction']*0.5 +
    df_AlertUnusualTransactions['avgTransaction'], 1, 0)
# Calculating the percentage of increase respect average
df_AlertUnusualTransactions['% Increase respect Average'] = (
        ((df_AlertUnusualTransactions['amount'] - df_AlertUnusualTransactions['avgTransaction']) / (
            df_AlertUnusualTransactions['avgTransaction']))*100).__round__(0)
# Sorting by amount and filtering just Alert positive. Need to see the biggest transaction amount first
df_AlertUnusualTransactions = df_AlertUnusualTransactions[(df_AlertUnusualTransactions['Alert'] == 1)]
df_AlertUnusualTransactions = df_AlertUnusualTransactions.sort_values(by='amount', ascending=False).reset_index()

# Average transaction amount per customer id, now i need the country as a column, i use pivot_table
# Replace the NAN values when the avg wasn't found for a customer
df_avgtransactionamountinMonthperCustomer2 = pd.pivot_table(df_avgtransactionamountinMonthperCustomer_andCountry,
                                                            values='avgTransaction', index=['id_customer'],
                                                            columns=['country_id'], aggfunc=np.sum).fillna(0)
# Average transaction amount by country
df_avgtransactioninMonthperCountry = df_ntransactioninMonthperCustomer.groupby(
    ['country_id'])['nTransaction'].mean().apply(np.ceil).reset_index(
    name='avgnTransactions')
# Min amount on transactions
df_amountMin = df.groupby(['country_id'])['amount'].min().reset_index(name='amountMIN')
# Number of transactions by contry, needed to know where the volume of transactions is more dense
df_ntransactions = df.groupby(['country_id']).size().reset_index(name='number_transactions')
# Putting all relevant information in a table. joining by the conutry_id
df_customerSegmentation = df_ntransactions.merge(
    df_nclientsbyCountry.set_index('country_id'), on='country_id').merge(
    df_amountAVG, on='country_id').merge(df_amountMax, on='country_id').merge(df_amountMin, on='country_id').merge(
    df_avgtransactioninMonthperCountry, on='country_id')
# endregion
# region Streamlit Charts section
st.title('Data Analysis       |       Trasactions Database')
checkbox = st.sidebar.checkbox("Show information By Country_counterparty")
slider = st.sidebar.slider('nTransaction', max_value=500, min_value=1, value=500)
if checkbox:
    st.dataframe(df_customerSegmentation)

c = alt.Chart(df_ntransactioninMonthperCustomer).mark_point().encode(
    x=alt.X('nTransaction', scale=alt.Scale(domain=[1, slider])),
    y=alt.Y('id_customer'),
    color='country_id',
    tooltip=['country_id', 'id_customer', 'nTransaction']
).properties(
    title='Customer Segmentation'
).interactive()
st.altair_chart(c, use_container_width=True)

# Pyplot Chart
source = df_avgtransactionamountinMonthperCustomer

# This chart show the amounts transacted
fig = px.histogram(source, x="avgTransaction", marginal="rug", hover_data=source.columns)
# Plot!
st.plotly_chart(fig, use_container_width=True)
# endregion
# region Testing data results
# print(source)

# pd.DataFrame(df_AlertUnusualTransactions).to_csv("file3.csv")
# This lines are for search the client transaction history.Those customers that triggered the alert
search_customerAlert = (df[(df['id_customer'] == 570) | (df['id_customer'] == 1519) | (df['id_customer'] == 2845) | (
        df['id_customer'] == 9932) | (df['id_customer'] == 4324)])
search_customerAlert = search_customerAlert.sort_values(by='amount', ascending=False)
# Searching ID's who triggered the alert
search_nTrasactionCustomerAlert = (df_ntransactionsAllbyCustomer[(
        df_ntransactionsAllbyCustomer['id_customer'] == 570) | (df_ntransactionsAllbyCustomer['id_customer'] == 1519) |
        (df_ntransactionsAllbyCustomer['id_customer'] == 2845) |
        (df_ntransactionsAllbyCustomer['id_customer'] == 9932) |
        (df_ntransactionsAllbyCustomer['id_customer'] == 4324)])
# print(df_AlertUnusualTransactions)
# Exporting
# pd.DataFrame(df_AlertUnusualTransactions).to_csv("suspect1.csv")
#endregion