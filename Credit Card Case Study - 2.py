#!/usr/bin/env python
# coding: utf-8

# In[51]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')


# In[52]:


customer_acquisition = pd.read_csv('Customer Acqusition.csv')
customer_acquisition


# In[53]:


spend = pd.read_csv('spend.csv')
spend


# In[54]:


repayment = pd.read_csv('Repayment.csv')
repayment


# In[55]:


# 1. In the above dataset,
# a. In case age is less than 18, replace it with mean of age values
customer_acquisition.loc[(customer_acquisition.Age<18),'Age']=customer_acquisition.Age.mean()
customer_acquisition.Age


# In[56]:


# b. In case spend amount is more than the limit, replace it with 50% of that customer’s limit (customer’s limit provided in acquisition table is the per transaction limit on his card)
customer_spend = pd.merge(left=customer_acquisition,right=spend,on="Customer",how="inner")
customer_spend[customer_spend["Amount"] > customer_spend['Limit']]


# In[57]:


customer_spend.loc[customer_spend["Amount"] > customer_spend["Limit"],"Amount"] = (50 * customer_spend["Limit"])/100
customer_spend.Amount


# In[58]:


# c. Incase the repayment amount is more than the limit, replace the repayment with the limit.
customer_repayment = pd.merge(left=customer_acquisition,right=repayment,on="Customer",how="inner")
customer_repayment[customer_repayment["Amount"] > customer_repayment['Limit']]


# In[59]:


customer_repayment.loc[customer_repayment["Amount"] > customer_repayment["Limit"],"Amount"] = customer_repayment["Limit"]
customer_repayment.Amount


# In[60]:


# 2. From the above dataset create the following summaries:
# a. How many distinct customers exist?
customer_acquisition['Customer'].drop_duplicates().count()


# In[61]:


# b. How many distinct categories exist?
customer_acquisition['Product'].drop_duplicates().count()


# In[62]:


# c. What is the average monthly spend by customers?
customer_spend = pd.merge(left=customer_acquisition,right=spend,on="Customer",how="inner")
customer_spend.groupby(pd.DatetimeIndex(customer_spend['Month']).month)['Amount'].mean().reset_index()


# In[63]:


# d. What is the average monthly repayment by customers?
customer_repayment = pd.merge(left=customer_acquisition,right=repayment,on="Customer",how="inner")
customer_repayment.groupby(pd.DatetimeIndex(customer_repayment['Month']).month)['Amount'].mean().reset_index()


# In[64]:


# e. If the monthly rate of interest is 2.9%, what is the profit for the bank for each month? (Profit is defined as interest earned on Monthly Profit. Monthly Profit = Monthly repayment – Monthly spend. Interest is earned only on positive profits and not on negative amounts)
s = customer_spend.groupby(pd.DatetimeIndex(customer_spend['Month']).month)['Amount'].sum().reset_index()
r = customer_repayment.groupby(pd.DatetimeIndex(customer_repayment['Month']).month)['Amount'].sum().reset_index()
profit = pd.DataFrame({'Month Number':[1,2,3,4,5,6,7,8,9,10,11,12],'Amount': (s.Amount - r.Amount),'Profit':(np.where((s.Amount - r.Amount)>0,((s.Amount - r.Amount)*2.9/100).round(2),'0'))})
profit


# In[65]:


# f. What are the top 5 product types?
spend.groupby('Type')['Amount'].sum().nlargest(n=5).reset_index()


# In[66]:


# g. Which city is having maximum spend?
customer_spend = pd.merge(left=customer_acquisition,right=spend,on="Customer",how="inner")
customer_spend.groupby('City')['Amount'].sum().nlargest(n=1).reset_index()


# In[67]:


# h. Which age group is spending more money?
customer_spend = pd.merge(left=customer_acquisition,right=spend,on="Customer",how="inner")
bins= [0,18,50,75,110]
labels = ['Less than 18','18-50','50-75','75 Above']
customer_spend['AgeGroup'] = pd.cut(customer_spend['Age'], bins=bins, labels=labels, right=False)
customer_spend.groupby('AgeGroup')['Amount'].sum().nlargest(n=1).reset_index()


# In[68]:


# i. Who are the top 10 customers in terms of repayment?
customer_repayment = pd.merge(left=customer_acquisition,right=repayment,on="Customer",how="inner")
customer_repayment.groupby('Customer')['Amount'].sum().nlargest(n=10).reset_index()


# In[69]:


# 3. Calculate the city wise spend on each product on yearly basis. Also include a graphical representation for the same
customer_spend = pd.merge(left=customer_acquisition,right=spend,on="Customer",how="inner")
customer_spend['Year'] = pd.DatetimeIndex(customer_spend['Month']).year
pd.pivot_table(data = customer_spend, index = 'City', columns=['Product','Year'],values='Amount', aggfunc='sum').plot(kind = 'bar')


# In[70]:


# 4. Create graphs for
# a. Monthly comparison of total spends, city wise
customer_spend = pd.merge(left=customer_acquisition,right=spend,on="Customer",how="inner")
customer_spend['Month'] = pd.DatetimeIndex(customer_spend['Month']).month
pd.pivot_table(data = customer_spend, index = 'City', columns='Month', 
               values='Amount', aggfunc='sum').plot(kind='bar',stacked=True)


# In[71]:


# b. Comparison of yearly spend on air tickets
customer_spend = pd.merge(left=customer_acquisition,right=spend,on="Customer",how="inner")
customer_spend['Year'] = pd.DatetimeIndex(customer_spend['Month']).year
pd.pivot_table(data = customer_spend[customer_spend.Type=='AIR TICKET'], index = 'Type', columns='Year', 
               values='Amount', aggfunc='sum').plot(kind='bar')


# In[72]:


# c. Comparison of monthly spend for each product (look for any seasonality that exists in terms of spend)
customer_spend = pd.merge(left=customer_acquisition,right=spend,on="Customer",how="inner")
customer_spend['Month'] = pd.DatetimeIndex(customer_spend['Month']).month
pd.pivot_table(data = customer_spend, index = 'Product', columns='Month', 
               values='Amount', aggfunc='sum').plot(kind='bar')


# In[73]:


# 5. Write user defined PYTHON function to perform the following analysis:You need to find top 10 customers for each city in terms of their repayment amount by different products and by different time periods i.e. year or month. The user should be able to specify the product (Gold/Silver/Platinum) and time period (yearly or monthly) and the function should automatically take these inputs while identifying the top 10 customers.
customer_repayment = pd.merge(left=customer_acquisition,right=repayment,on="Customer",how="inner")
customer_repayment['Month'] = pd.DatetimeIndex(customer_repayment['Month']).month
customer_repayment['Year'] = pd.DatetimeIndex(customer_repayment['Month']).year
def top10Customers(product_category,time_period):    
    return customer_repayment.loc[(customer_repayment.Product == product_category)].groupby(['Customer','City','Product',time_period]).Amount.sum().nlargest(n=10).reset_index().sort_values('Amount',ascending=False)

product_category=str(input("Please Enter Product Category (Gold/Silver/Platinum): "))
time_period=str(input("Please Enter Time Period (Year/Month): "))
Customers=top10Customers(product_category,time_period)
Customers

