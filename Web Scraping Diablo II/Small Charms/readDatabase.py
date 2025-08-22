'''
Created on Jul 28, 2025

@author: Lexi Zellner

This script loads the DiabloII.db database and performs statistical analysis on the data.

'''

#Import
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sqlite3

#Display Options for DataFrames
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 300)
pd.set_option('display.max_rows', 300)
maxPrice = 20

#Read Data
with sqlite3.connect('DiabloII.db') as conn:
    df = pd.read_sql("SELECT * FROM ITEMS", conn)
    print(df.fillna(''))
    print('\n')

#Filter High-Priced Items
priceArray = df["Price"].to_numpy(dtype=float,na_value=0)
indices = list(filter(lambda x: priceArray[x] > maxPrice, range(len(priceArray))))
df = df.drop(index=indices,axis=0)

#Linear Regression
A = df.iloc[0:df.shape[0],1:(df.shape[1])-1].to_numpy(dtype=float,na_value=0)
b = df.iloc[0:df.shape[0],-1].to_numpy(dtype=float,na_value=0)
data = np.linalg.lstsq(A,b)
x = data[0]
cols = df.columns
for i in range(0,x.size):
    print('{0: <13}'.format(cols[i+1]) + ' = ' + format(x[i],'.4f'))
print('\n')

#Reorder
dfWeights = pd.DataFrame(columns=["Stat","Weight"])
dfWeightList = ['MF','GF','FHR','FRW',
                'FireResist','ColdResist','LiteResist','PsnResist','AllResist',
                'Life','Mana','Str','Dex','Defense','MaxDmg','AR',
                'Psn3','Psn4','Psn5','Psn6','Psn7','Psn8','Psn9','Psn10','Psn11','Psn12']
keys = df.columns.tolist()
count = 0
for col in dfWeightList:
    count = count + 1
    i = 0
    ind = -1
    for key in keys:
        i = i + 1
        if key == col:
            ind = i
    if dfWeights.size==0:
        dfWeights = pd.DataFrame({"Stat":col,"Weight":x[ind-2]},[count-1])
    else:
        if ind>=0:
            dfWeights = pd.concat([dfWeights,pd.DataFrame({"Stat":col,"Weight":x[ind-2]},[count-1])], ignore_index=True)
        else:
            dfWeights = pd.concat([dfWeights,pd.DataFrame({"Stat":col,"Weight":0},[count-1])], ignore_index=True)

#Plot Data
ax = dfWeights.plot.bar(x='Stat', y='Weight', width=1,bottom=0,edgecolor='k')
ax.get_legend().remove()
ax.set_yticks(ax.get_yticks(), labels=['-'*int(y<0) + '${:,.8}'.format(abs(y)) + '0' for y in ax.get_yticks()])
plt.title("Price of Attributes on Small Charms")
plt.ylabel('Price of Attribute')
ax.set_position([0.12,0.24,0.8,0.65])
plt.show()
