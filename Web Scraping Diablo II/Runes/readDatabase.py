'''
Created on Aug 14, 2025

@author: Lexi

This script loads the DiabloII.db database and performs statistical analysis on the data.

Weighted-LSQR explanation:
Trades are split into two categories:
1) Rune-for-Rune trades where A[i,j]>0 and A[i,k]<0 and b[i]=0 (e.g. 1xIst - 2xMal = 0)
2) Rune-for-Amethyst trades where A[i,j]>0, all other A[i,]=0, and b[i]>0 (e.g. 1xIst = 10)
The first category pushes x to be trivial, reducing its own error term to zero
The second category pushes x to be non-trivial
The combination leads to a "balance" between 0 and a fair x estimate (x = c*xhat where 0<c<1)
In order to prioritize a fair x estimate, the trades with Amethysts will be highly weighted (c>>0, c<1)

'''

#Import
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sqlite3
import sys
import math
from helperFunctions import *
import seaborn as sns
from math import nan

#Display Options for DataFrames
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 3000)
pd.set_option('display.max_rows', 3000)
np.set_printoptions(linewidth=2000)
np.set_printoptions(threshold=sys.maxsize, edgeitems=10)

#Read Data
with sqlite3.connect('DiabloIIrunes.db') as conn:
    df = pd.read_sql("SELECT * FROM RUNES", conn)

#Clean up DataFrame
df = df[df.max(axis=1)>=1]
df = df.reset_index(drop=True)
runesToDrop = []

#Create Rune List
runeList = ['El','Eld','Tir','Nef','Eth','Ith','Tal','Ral','Ort','Thul',
            'Amn','Sol','Shael','Dol','Hel','Io','Lum','Ko','Fal','Lem','Pul','Um','Mal',
            'Ist','Gul','Vex','Ohm','Lo','Sur','Ber','Jah','Cham','Zod']
runeIndex = [int(df[df[rune]>0].first_valid_index()) for rune in runeList]

#Manual Guess
xGuess = 1.3 ** np.logspace(-1,2,num=33,base=7) / 4
xGuess[xGuess>30] = 30 #High Runes
xGuess[7] = 2*xGuess[7] #Ral
#xGuess[8] = 0.5*xGuess[8] #Ort
xGuess[29] = (2.4)*xGuess[29] #Ber
xGuess[30] = (1.6)*xGuess[30] #Jah
xGuess[31] = (1/4)*xGuess[31] #Cham
xGuess[32] = (1/2)*xGuess[32] #Zod
indsToRemove = [runeList.index(rune) for rune in runesToDrop]
for i,ind in enumerate(indsToRemove):
    xGuess = np.delete(xGuess,ind-i)

#Remove Runes to Drop
df, runeList, runeIndex = remove_runes(df,runeList,runesToDrop)

#Remove Rune-for-Rune trades
'''
df['Perfect Amethyst'] = -df['Perfect Amethyst']
df = df[df.min(axis=1)>0]
df['Perfect Amethyst'] = -df['Perfect Amethyst']
df = df.reset_index(drop=True)
runeIndex = [(-100 if df[df[rune]>0].first_valid_index() is None else int(df[df[rune]>0].first_valid_index())) for rune in runeList]
'''

#Aggregate
for i,rune in enumerate(runeList):
    innerdf = df[df[rune]>0]
    if i==0:
        tempdf = innerdf.sum() / innerdf.sum().max()
    else:
        tempdf = pd.concat([tempdf,innerdf.sum() / innerdf.sum().max()], axis=1)
dfAggregate = tempdf.transpose()
'''
dfAggregate[dfAggregate>0] = 0
sns.heatmap(abs(dfAggregate),cmap='Reds')
plt.xticks([x+0.5 for x in range(len(runeList))],labels=runeList)
plt.yticks([x+0.5 for x in range(len(runeList))],labels=runeList)
plt.tick_params(axis='y',labelrotation=0)
plt.show()
'''

#Linear Regression Setup
A,b = df_to_matrix(df,'Perfect Amethyst')
W = np.ones([A.shape[0],1])
W[b>0.5] = 25*W[b>0.5]

#Linear Regression
x = np.linalg.lstsq(A*W,b*W.reshape(W.shape[0],))[0]

#Store value of each Rune in Dataframe
dfRunes = pd.concat([pd.DataFrame(data=runeList,columns=['Rune']),pd.DataFrame(data=x,columns=['Value'])],axis=1)

#Check only pAme trades and get the average value for each rune
for i, rune in enumerate(runeList):
    Atest, btest = df_to_matrix(df[df[rune]>0],'Perfect Amethyst')
    pAmeValue = list()
    flag1 = np.min(Atest, axis=1) >= 0 #Filter out other runes in trade
    flag2 = btest > 0 #Look at perf amethyst values
    for j in range(len(btest)):
        if flag1[j] and flag2[j]:
            pAmeValue.append(float(btest[j] / Atest[j,i]))
    dfRunes.loc[i,'pAme'] = str(pAmeValue).replace(' ','').replace('[','').replace('\n','').replace(']','') if len(pAmeValue)>0 else '0'
    dfRunes.loc[i,'pAmeAvg'] = np.average(pAmeValue) if len(pAmeValue)>0 else nan

'''
#Set estimate for Rune Values
xGuess = dfRunes['pAmeAvg'].to_numpy(dtype=float)
for i in range(len(xGuess)):
    if xGuess[i]<1e-2:
        xGuess[i] = min(1.5*xGuess[i-1],50)
'''
    
#Testing
#xGuess = x.copy()
#xGuess[-13] = 2*xGuess[-13]
#xGuess[-13:] = 100*xGuess[-13:]
    
#Display Information
'''
residualGuess = b-A@xGuess
inds = abs(residualGuess).argsort()[-10:-1]
dfResiduals = df.iloc[inds,].fillna('')
dfResiduals['Residuals'] = residualGuess[inds]
tempDict = {}
for i,rune in enumerate(runeList):
    tempDict.update({rune:[(1/100)*round(100*xGuess[i])]})
dfResiduals = pd.concat([dfResiduals,pd.DataFrame(tempDict)])
dfResiduals = dfResiduals.drop(columns='Perfect Amethyst')
print(dfResiduals)
print(f'Residual Sum = {sum(abs(residualGuess[inds]))}')
'''

#Plot Data 1
fig, (ax1, ax2) = plt.subplots(2,1,figsize=(8, 9))
plt1 = ax1.plot(range(len(runeList)), xGuess, linestyle='-', marker='o', c='#ff0000', label='Manual Guess')
axtemp = dfRunes.plot(ax=ax1, x='Rune', y='Value', marker='o', c='#00ff00', label='LSQR')
plt2 = axtemp.get_children()[1]
#for i, rune in enumerate(runeList):
#    if not dfRunes.at[i,'pAme'] == '':
#        test = [float(x) for x in dfRunes.at[i,'pAme'].split(',')]
#        x_pos = i * np.ones(len(test))
#        ax1.plot(x_pos,test, linestyle='-', linewidth=0.5, marker='o', markersize=1, c='#0000ff')
#plt3 = ax1.plot(range(len(runeList)), dfRunes['pAmeAvg'], linestyle='-', marker='o', c='#0000ff', label='Filtered')
ax1.axhline(y=1, color=(0.5,0,1), linestyle='--', linewidth=1)
for i in [1e-2,5e-2, 1e-1, 2.5e-1, 5e-1, 1, 2, 3, 5, 10, 20, 30, 50, 100, 300, 500]:
    ax1.axhline(y=i, color=(0.1,0.1,0.1), linewidth=0.3)
ax1.tick_params(axis='x', labelrotation=90)
ax1.legend(handles=[plt1[0],plt2], loc='upper left') #,plt3[0]], loc='upper left')
ax1.set_yscale('log')
ax1.set_xlim([-1,len(runeList)])
ax1.set_ylim([1e-3,1e2])
ax1.set_yticks([1e-3,5e-3,1e-2,5e-2, 1e-1, 2.5e-1, 5e-1, 1, 2, 3, 5, 10, 20, 30, 50, 100],
       labels=['1/1000','1/500','1/100','1/20','1/10','1/4','1/2','1','2','3','5','10','20','30','50','100'])
ax1.set_xticks(range(len(runeList)), labels=runeList)
ax1.set_title("Relative Value of Runes")
ax1.set_ylabel('Value')
ax1.set_position([0.15, 0.56, 0.80, 0.38])

#Plot Data 2
Ares, bres = df_to_matrix(dfAggregate,'Perfect Amethyst')
maxResidual = max(max(abs(b-A@x)),max(abs(b-A@xGuess)))
plt1 = ax2.scatter(range(df.shape[0]), b-A@xGuess, s=3, c='#ff0000', label='Manual Guess')
plt2 = ax2.scatter(range(df.shape[0]), b-A@x, s=3, c='#00ff00', label='LSQR')
ax2.plot(runeIndex,bres-Ares@xGuess, c='#aa0000', label='Manual Guess')
ax2.plot(runeIndex,bres-Ares@x, c='#00aa00', label='LSQR')
ax2.axhline(y=0, color=(0.5,0,1), linestyle='--', linewidth=1)
ax2.legend(handles=[plt1,plt2], loc='lower left')
ax2.set_yscale('symlog')
ax2.tick_params(axis='x', labelrotation=90)
ax2.set_xticks(runeIndex, labels=runeList)
ax2.set_xlim([-5,max(df.shape[0],max(runeIndex))+5])
ax2.set_ylim([-10 ** math.ceil(math.log(maxResidual,10)), 10 ** math.ceil(math.log(maxResidual,10))])
ax2.set_title("Residual Error")
ax2.set_xlabel('Rune')
ax2.set_ylabel('Error')
ax2.set_position([0.15, 0.13, 0.80, 0.30])

#Finish Plot
figsubtext1 = 'Manual Guess is based on standard expected trade value'
figsubtext2 = 'Filtered data shows only "Rune for Perfect Amethyst (Value=1)" trades, not rune-for-rune'
plt.figtext(0.5, 0.03, figsubtext1, wrap=True, horizontalalignment='center', fontsize=8)
plt.figtext(0.5, 0.01, figsubtext2, wrap=True, horizontalalignment='center', fontsize=8)
plt.show()

#print(f'Residuals (LSQR)  = {sum(abs(b-A@x)):.2f}')
#print(f'Residuals (Guess) = {sum(abs(b-A@xGuess)):.2f}')
#print((bres-Ares@xGuess)-(bres-Ares@x))


#val1 = b[1368]-sum(A[1368]*x)
#val2 = b[1368]-sum(A[1368]*xGuess)
