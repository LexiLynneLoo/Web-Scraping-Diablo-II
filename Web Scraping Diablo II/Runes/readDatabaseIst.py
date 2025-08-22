'''
Created on Aug 14, 2025

@author: Lexi

This script loads the DiabloII.db database and performs statistical analysis on the data.

'''

#Import
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sqlite3
import sys
import math
from helperFunctions import *

#Display Options for DataFrames
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 3000)
pd.set_option('display.max_rows', 3000)
np.set_printoptions(linewidth=2000)
np.set_printoptions(threshold=sys.maxsize, edgeitems=10)

#Read Data
with sqlite3.connect('DiabloIIrunes.db') as conn:
    df = pd.read_sql("SELECT * FROM RUNES", conn)
    #print(df.fillna(''))
    #print('\n')

#Clean up DataFrame
df = df[df.max(axis=1)>=1]
df = df.reset_index(drop=True)

#Remove Perfect Amethyst trades
df = df[df["Perfect Amethyst"].isnull()]
df = df.reset_index(drop=True)
df = df.drop('Perfect Amethyst',axis=1)

#Create Rune List
runeList = ['El','Eld','Tir','Nef','Eth','Ith','Tal','Ral','Ort','Thul',
            'Amn','Sol','Shael','Dol','Hel','Io','Lum','Ko','Fal','Lem','Pul','Um','Mal',
            'Ist','Gul','Vex','Ohm','Lo','Sur','Ber','Jah','Cham','Zod']
runeIndex = [int(df[df[rune]>0].first_valid_index()) for rune in runeList]

#Manual Guess
xGuess = 1.3 ** np.logspace(-1,2,num=33,base=7) / 12
#xGuess[xGuess<0.1] = 0.1 #Low Runes
xGuess[xGuess>30] = 30 #High Runes
xGuess[7] = 2*xGuess[7] #Ral
xGuess[8] = 0.5*xGuess[8] #Ort
#xGuess[26] = (0.8)*xGuess[26] #Ohm
xGuess[29] = (2.4)*xGuess[29] #Ber
xGuess[30] = (1.6)*xGuess[30] #Jah
xGuess[31] = (1/4)*xGuess[31] #Cham
xGuess[32] = (1/2)*xGuess[32] #Zod

#xGuess[runeList.index('Ist')]

#Linear Regression Setup
A,b = df_to_matrix(df,'Ist')

#Linear Regression
data = np.linalg.lstsq(A,b)
x = data[0]
x = np.concatenate((np.concatenate((x[0:runeList.index('Ist')],np.ndarray([1]))),x[runeList.index('Ist'):len(x)]))
x[runeList.index('Ist')] = 1

dfRunes = pd.DataFrame(runeList)
for i, rune in enumerate(runeList):
    
    #Assign LSQR value to each Rune
    dfRunes.at[i,1] = float(x[i])
    #dfRuneSingle = df[df[rune]>0]
    #inds = [x - min(df.index.to_list()) for x in dfRuneSingle.index.to_list()]
    
    '''
    #Check only pAme trades
    Atest, btest = df_to_matrix(df[df[rune]>0],'Ist')
    #Atest = A[inds,]
    #btest = b[inds,]
    pAmeValue = list()
    flag1 = np.min(Atest, axis=1) >= 0 #Filter out other runes in trade
    flag2 = btest > 0 #Look at perf amethyst values
    for j in range(len(btest)):
        if flag1[j] and flag2[j]:
            pAmeValue.append(float(btest[j] / Atest[j,i]))
    if len(pAmeValue)>0:
        dfRunes.at[i,2] = str(pAmeValue).replace(' ','').replace('[','').replace('\n','').replace(']','')
    else:
        dfRunes.at[i,2] = '0'
    if len(pAmeValue)>0:
        dfRunes.at[i,3] = np.average(pAmeValue)
    else:
        dfRunes.at[i,3] = 0
    '''
dfRunes.columns=['Rune','Value'] #,'pAme','pAmeAvg']


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
'''
for i, rune in enumerate(runeList):
    if not dfRunes.at[i,'pAme'] == '':
        test = [float(x) for x in dfRunes.at[i,'pAme'].split(',')]
        x_pos = i * np.ones(len(test))
        ax1.plot(x_pos,test, linestyle='-', linewidth=0.5, marker='o', markersize=1, c='#0000ff')
plt3 = ax1.plot(range(len(runeList)), dfRunes['pAmeAvg'], linestyle='-', marker='o', c='#0000ff', label='Filtered')
'''
#plt4 = ax1.plot(range(len(runeList)), x2, linestyle='-', marker='o', c='#ffaa00', label='Modified')
ax1.axhline(y=1, color=(0.5,0,1), linestyle='--', linewidth=1)
for i in [1e-2,5e-2, 1e-1, 2.5e-1, 5e-1, 1, 2, 3, 5, 10, 20, 30, 50, 100, 300, 500]:
    ax1.axhline(y=i, color=(0.1,0.1,0.1), linewidth=0.3)
ax1.tick_params(axis='x', labelrotation=90)
ax1.legend(handles=[plt1[0],plt2], loc='upper left') #,plt3[0]
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
A2 = df.to_numpy(dtype=float,na_value=0)
maxResidual = max(max(abs(A2@x)),max(abs(A2@xGuess)))
ax2.scatter(range(df.shape[0]), A2@x, s=3, c='#00ff00', label='LSQR')
ax2.scatter(range(df.shape[0]), A2@xGuess, s=3, c='#ff0000', label='Manual Guess')
#ax2.scatter(range(df.shape[0]), A2@x2, s=3, c='#ffaa00', label='Modified')
ax2.axhline(y=0, color=(0.5,0,1), linestyle='--', linewidth=1)
ax2.legend(loc='upper left')
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


