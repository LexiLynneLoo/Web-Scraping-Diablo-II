'''
Created on Jul 28, 2025

@author: Lexi Zellner

This script simply loads the DiabloII.db database, removes duplicate entries, and rewrites the database.

'''

#Import
import pandas as pd
import sqlite3

#Read Distinct Data and Rewrite
with sqlite3.connect('DiabloII.db') as conn:
    df = pd.read_sql("SELECT DISTINCT * FROM ITEMS", conn)
    df.to_sql('ITEMS', conn, if_exists='replace',index=False)

print('Removed duplicates and cleaned up database.')