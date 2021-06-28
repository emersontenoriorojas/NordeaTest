# Customers Transactions Database Analysis
import streamlit as st
import matplotlib.pyplot as plt
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
# Number of customers by country_counterparty
df_nclientsbyCountry = df.groupby(['country_id'])['id_customer'].nunique().reset_index(name='number_customers')
# Average amount of transactions by country
df_amountAVG = df.groupby(['country_id'])['amount'].mean().round(1).reset_index(name='amountAVG')
# Max amount on transactions by country
df_amountMax = df.groupby(['country_id'])['amount'].max().reset_index(name='amountMAX')
# Max amount on transactions
df_ntransactioninMonthperCustomer = df.groupby(['id_customer', 'country_id'])['id_customer'].size().reset_index(
    name='nTransaction')
df_avgtransactioninMonthperCountry = df_ntransactioninMonthperCustomer.groupby(
    ['country_id'])['nTransaction'].mean().apply(np.ceil).reset_index(
    name='avgnTransactions')
# Min amount on transactions
df_amountMin = df.groupby(['country_id'])['amount'].min().reset_index(name='amountMIN')
df_ntransactions = df.groupby(['country_id']).size().reset_index(name='number_transactions')
df_customerSegmentation = df_ntransactions.merge(
    df_nclientsbyCountry.set_index('country_id'), on='country_id').merge(
    df_amountAVG, on='country_id').merge(df_amountMax, on='country_id').merge(df_amountMin, on='country_id').merge(
    df_avgtransactioninMonthperCountry, on='country_id')
# endregion
# region Charts section
alt.Chart(df_ntransactioninMonthperCustomer).mark_circle(size=60).encode(
    x='nTransaction',
    y='id_customer',
    color='country_id',
    tooltip=['Name', 'country_id', 'nTransaction', 'id_customer']
).interactive()
# endregion



#df_nCustomerbyCountry['transactions_pcustomer'] = (df_nCustomerbyCountry.groupby(['country_id'])['country_id'].transform('count')).astype(int)
# Addin column # of trasactions in a month
# df = df.sort_values(by=['id_customer'])
#print(df_ntransactioninMonthperCustomer)
# filterdf = df[(df_avgtransaction['id_customer'] == 325555) | (df['id_customer'] == 0)]
