'''
Created on Aug 18, 2025

@author: Lexi
'''


#Import
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sqlite3
import sys
import math
from helperFunctions import *

#5 runes, 8 trades (Values = [0.1, 0.1, 0.2, 1, 3])
df = pd.DataFrame(columns=['Rune #1','Rune #2','Rune #3','Rune #4','Rune #5','Constant'])
df = pd.concat([df,pd.DataFrame({'Rune #1':[2],'Rune #3':[-1]})])
df = pd.concat([df,pd.DataFrame({'Rune #1':[10],'Constant':[-1]})])
df = pd.concat([df,pd.DataFrame({'Rune #2':[1],'Rune #1':[-1]})])
df = pd.concat([df,pd.DataFrame({'Rune #2':[10],'Rune #4':[-1]})])
df = pd.concat([df,pd.DataFrame({'Rune #3':[5],'Constant':[-1]})])
#df = pd.concat([df,pd.DataFrame({'Rune #3':[10],'Constant':[-2]})])
df = pd.concat([df,pd.DataFrame({'Rune #4':[3],'Rune #5':[-1]})])
df = pd.concat([df,pd.DataFrame({'Rune #5':[1],'Rune #3':[-15]})])

#Linear Regression
A, b = df_to_matrix(df)
data = np.linalg.lstsq(A,b)
x = data[0]

print(df.fillna(''))
print('')
for i,xVal in enumerate(x):
    print(f'Rune #{i+1} value = {xVal:.2f}')
print('')
print(f'Residual = {sum(A@x-b):.2f}')