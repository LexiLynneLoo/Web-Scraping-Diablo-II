'''
Created on Jun 19, 2025

@author: Lexi
'''


'''
    #Skills
    referenceDict.update({
        r'\+(\d+) to All Skills':"AllSkills",
        r'\+(\d+) to Combat Skills \(Barbarian Only\)':"CombatSkills",
        r'\+(\d+) to Barbarian Skill Levels':"BarbSkills",
    })
    
    #Resists
    referenceDict.update({
        r'\+(\d+)% to Maximum Poison Resist':"MaxPsnResist",
        r'Fire Resist -(\d+)%':"FireResist",
        r'Poison Resist +(\d+)%':"PsnResist",
        r'Lightning Resist +(\d+)%':"LiteResist",
        r'All Resistances +(\d+)':"AllResist",
        r'\+(\d+) Lightning Absorb':"LiteAbsorb",
    })
    
    #Attack / Damage
    referenceDict.update({
        r'\+(\d+)% Increased Attack Speed':"AtkSpeed",
        r'(\d+)% Bonus to Attack Rating':"AR Bonus",
        r'(\d+)% Life stolen per hit':"LifeSteal",
        r'\+(\d+) to Maximum Damage':"MaxDmg",
        r'Damage Reduced by (\d+)%':"DR%",
        r'Damage Reduced by (\d+)':"DR",
        r'(\d+)% Chance of Crushing Blow':"CB",
    })
    
    #Chance to Proc or Charges
    referenceDict.update({
        r'(\d+)% Chance to cast level 15 Poison Nova when struck':"PsnNova",
        r'Level (\d+) Venom (20/20 Charges)':"VenomLvl",
    })
    
    #Attributes
    referenceDict.update({
        r'\+(\d+) to Strength':"Strength",
        r'\+(\d+) to Dexterity':"Dexterity",
    })
    
    #FHR, FCR
    referenceDict.update({
        r'\+(\d+)% Faster Hit Recovery':"FHR",
    })
    
    #Misc
    referenceDict.update({
        r'(........) \(Cannot be Repaired\)':"Ethereal",
        r'(..)destructible':"Indestructible",
        r'(.......) Monster Heal':"Monster Heal",
        r'Slows Target by (\d+)%':"Slow",
        r'Attacker Takes Lightning Damage of (\d+)':"ThornLite",
        r'Socketed \((\d+)\)':"Sockets",
        r'(\d+) to Light Radius':"LightRadius",
        r'(.....)back':"Knockback",
    })
'''