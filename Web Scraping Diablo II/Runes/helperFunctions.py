'''
Created on Aug 16, 2025

@author: Lexi
'''

def df_to_matrix(df,brune):
    
    A = df.drop(brune,axis=1).to_numpy(dtype=float,na_value=0)
    b = -df[brune].to_numpy(dtype=float,na_value=0)
    
    #Normalize
    #Amax = np.max(A, axis=1, keepdims=True)
    #bmax = np.max(A, axis=1)
    #A = A / Amax
    #b = b / bmax
    
    return A,b

def remove_runes(df,runeList,runesToRemove):
    
    for rune in runesToRemove:
        df = df[df[rune].isnull()]
        runeList.remove(rune)
        df = df.drop(columns=rune)
        
    runeIndex = [int(df[df[rune]>0].first_valid_index()) for rune in runeList]
    
    return df,runeList,runeIndex