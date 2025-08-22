'''
Created on Jun 17, 2025

@author: Lexi
'''

def parseD2item(item,df):
    import pandas as pd
    import re
    parsedString = item.text
    lines = parsedString.split('\n')
    attributes = []
    for i in lines:
        attributes.append(i.strip())
    
    #Initialization
    attributesDict = {"ItemName":[attributes[0]]} #, "ItemType":[attributes[1]]}
    referenceDict = {}
    weightDict = {}
    
    #Required Level
    referenceDict.update({
        r'Required Level: (\d+)':"Lvl",
        r'Reoured Level: (\d+)':"Lvl",
    })
    weightDict.update({
        "Lvl":1
    })
    
    #Unidentified
    '''
    referenceDict.update({
        r'(..)identified':"Unid",
    })
    weightDict.update({
        "Unid":1
    })
    '''
    
    #Skills
    '''
    referenceDict.update({
        r'\+(\d+) to All Skills':"AllSkills",
    })
    weightDict.update({
        "AllSkills":1
    })
    '''
    '''
        r'\+(\d+) to All Attributes':"AllAttributes",
        "AllAttributes":20,
    '''
    #Attributes
    referenceDict.update({
        r'\+(\d+) to Dexterity':"Dex",
        r'\+(\d+) to Strength':"Str",
        r'\+(\d+) to Life':"Life",
        r'\+(\d+) to Mana':"Mana",
    })
    weightDict.update({
        "Dex":2,
        "Str":2,
        "Life":20,
        "Mana":17,
    })
    
    #MF
    referenceDict.update({
        r'(\d+)% Better Chance of Getting Magic Items':"MF",
        r'(\d+)% Better Chance of Getting Magic 1 Tom':"MF",
        r'(\d+)% Better Chance of Getting Magic Irems':"MF",
        r'(\d+)% Extra Gold from Monsters':"GF",
    })
    weightDict.update({
        "MF":7,
        "GF":10,
    })
    
    #Resists
    referenceDict.update({
        r'Fire Resist \+(\d+)%':"FireResist",
        r'Poison Resist \+(\d+)%':"PsnResist",
        r'Lightning Resist \+(\d+)%':"LiteResist",
        r'Lightning Resist (\d+)%':"LiteResist",
        r'Cold Resist \+(\d+)%':"ColdResist",
        r'Cold Resist (\d+)%':"ColdResist",
        r'All Resistances \+(\d+)':"AllResist",
        r'All Reesistances \+(\d+)':"AllResist",
        r'\+(\d+) Defense':"Defense",
        r'\+(\d+)% Faster Hit Recovery':"FHR",
    })
    weightDict.update({
        "FireResist":11,
        "PsnResist":11,
        "LiteResist":11,
        "ColdResist":11,
        "AllResist":5,
        "Defense":30,
        "FHR":5,
    })
    
    #AR / Damage
    referenceDict.update({
        r'\+(\d+) to Maximum Damage':"MaxDmg",
        r'\+(\d+) to Attack Rating':"AR",
        r'\+(\d+) poison damage over 5 seconds':"Psn5",
        r'\+(\d+) poison damage over 6 seconds':"Psn6",
        r'\+(\d+) poison damage over 9 seconds':"Psn9",
        r'\+(\d+) poison damage over 10 seconds':"Psn10",
        r'\+(\d+) poison damage over 11 seconds':"Psn11",
        r'\+(\d+) poison damage over 12 seconds':"Psn12",
    })
    weightDict.update({
        "MaxDmg":3,
        "AR":36,
        "Psn3":15,
        "Psn4":50,
        "Psn5":100,
        "Psn6":175,
        "Psn7":102,
        "Psn8":176,
        "Psn9":281,
        "Psn10":329,
        "Psn11":376,
        "Psn12":451,
    })
    
    #Experience
    '''
    referenceDict.update({
        r'\+(\d+)% to Experience Gained':"ExpGain",
    })
    weightDict.update({
        "ExpGain":10,
    })
    '''
    
    #???
    referenceDict.update({
        r'\+(\d+)% Faster Run/walk':"FRW",
        r'(\d+)% Faster Run/walk':"FRW",
    })
    weightDict.update({
        "FRW":3,
    })
    
    
    for item in attributes:
        flag = 0
        if (item==attributes[0]) or (item==attributes[1]) or ('Keep in Inventory' in item) or ('All Skills' in item) or ('All Attributes' in item) or ('Experience Gained' in item):
            flag = 1
        for key in referenceDict:
            regex = re.compile(key, re.IGNORECASE)
            mo = regex.search(item)
            if mo is not None:
                flag = 1
                if referenceDict[key]=="Psn12":
                    print(mo.group(1))
                if mo.group(1).isdigit():
                    scalar = weightDict[referenceDict[key]]
                    attributesDict[referenceDict[key]] = int(mo.group(1))/scalar
                else:
                    attributesDict[referenceDict[key]] = '1'
        if not flag:
            print('Attribute not Found:' + item)
    
    #Add entry to Data Frame
    df = pd.concat([df,pd.DataFrame(attributesDict)], ignore_index=True)
    return df









