'''
Created on Aug 13, 2025

@author: Lexi

This script parses the Diablo II Traderie website and scrapes listed "rune" entries and trade requests
The data is cleaned and then stored in the DiabloIIrunes.db database.

'''

#Import
from selenium import webdriver
import undetected_chromedriver as uc
from fake_useragent import UserAgent
import pandas as pd
from bs4 import BeautifulSoup
import re
import time
import sqlite3

#Settings
url = ["https://traderie.com/diablo2resurrected/product/","?prop_Ladder=true&prop_Mode=softcore&prop_Platform=PC"] #Blank
regexListing = re.compile(r'(\d+)  x (\S+) Rune', re.IGNORECASE)
regexListingSingle = re.compile(r'(\S+) Rune', re.IGNORECASE)
regexOffer = re.compile(r'(\d+) x (\S+) Rune', re.IGNORECASE)
regexOfferGems = re.compile(r'(\d+) x Perfect Amethyst', re.IGNORECASE)

#Display Options for DataFrames
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 300)
pd.set_option('display.max_rows', 300)
pd.set_option('future.no_silent_downcasting', True)

#Create Rune List
runeList = ['El','Eld','Tir','Nef','Eth','Ith','Tal','Ral','Ort','Thul',
            'Amn','Sol','Shael','Dol','Hel','Io','Lum','Ko','Fal','Lem','Pul','Um','Mal',
            'Ist','Gul','Vex','Ohm','Lo','Sur','Ber','Jah','Cham','Zod']
runeListWithGems = runeList.copy()
runeListWithGems.append('Perfect Amethyst')
runeIDs = {'El':'2946107871','Eld':'2316328159','Tir':'3128717341','Nef':'2850885338','Eth':'3656401092','Ith':'3461032747',
           'Tal':'3120045661','Ral':'3826075459','Ort':'3481558468','Thul':'2667920742','Amn':'4237640539','Sol':'2289057068',
           'Shael':'3835643192','Dol':'3683674872','Hel':'3157809229','Io':'2313512017','Lum':'3523099841','Ko':'3770490171',
           'Fal':'2442002770','Lem':'3214752119','Pul':'2899268590','Um':'2654038235','Mal':'2401638276','Ist':'2290642411',
           'Gul':'4160776515','Vex':'3806138905','Ohm':'3896329590','Lo':'3632079454','Sur':'3382986705','Ber':'4149485449',
           'Jah':'2552039455','Cham':'3191411278','Zod':'4067651730'}

#Create DataFrame
dfAllRunes = pd.DataFrame(columns=runeListWithGems)
for rune in runeList:
    
    print('Parsing Rune: ' + rune + '...')
    
    #Webdriver Options
    options = webdriver.ChromeOptions() 
    options.headless = True
    options.add_argument("--headless")
    options.add_argument(f"--user-agent={UserAgent().random}")
    options.uses_subprocess = False
    
    #Scrape Website
    driver = None
    try:
        driver = uc.Chrome(options=options)
        driver.get(url[0] + runeIDs[rune] + url[1])
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})") # Disable WebDriver flag
        driver.execute_script("return navigator.language") # Execute Cloudflare's challenge script
        html = driver.page_source #Parse HTML
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if driver:
            driver.close()
            driver.quit()
    
    #Parse HTMML
    soup = BeautifulSoup(html,'html.parser')
    listingInfo = soup.find_all('div', class_="listing-product-info")
    
    #Create DataFrame
    dfRunes = pd.DataFrame(columns=runeListWithGems)
    badFlag = 0
    removeFlag = 0
    for line in listingInfo:
        
        #Find Listed Item
        listing = line.find('a', class_='sc-iGgWBj hCbfch listing-name selling-listing')
        X = listing.get_text().replace('\xa0','\n').split('\n')
        X2 = [item.strip() for item in X]
        X3 = [item for item in X2 if item]
        listedEntry = X3[0]
        
        #Initialize Individual Trade DataFrame
        badFlag = 0
        mo = regexListing.search(listedEntry)
        if mo is not None:
            basedf = {mo.group(2):int(mo.group(1))} #Rune name, Number
        else:
            mo = regexListingSingle.search(listedEntry)
            if mo is not None:
                basedf = {mo.group(1):1} #Rune name, Number
            else:
                badFlag = 1 #Bad Listing, skip
                print('Bad Listing Offer: "' + listedEntry + '"')
        
        #Find Listed Offer(s)
        if not badFlag:
            offers = line.find_all('div', class_='price-line')
            listedOffers = []
            for offer in offers:
                Y = offer.get_text().replace('\xa0','\n').split('\n')
                Y2 = [item.strip() for item in Y]
                Y3 = [item for item in Y2 if item]
                [listedOffers.append(item) for item in Y3]
            
            #Split into Multiple Offers
            if len(listedOffers)>0:
                ind = [-1]
                [ind.append(i) for i, item in enumerate(listedOffers) if item == 'OR']
                ind.append(len(listedOffers))
                
                #Look at each "OR" segment - this is an individual trade
                for i in range(0,len(ind)-1):
                    tradeDict = basedf.copy()
                    removeFlag = 0
                    
                    #Look at each item within a segment
                    for entry in listedOffers[ind[i]+1:ind[i+1]]:
                        #Look for Rune Match
                        mo = regexOffer.search(entry)
                        if mo is not None:
                            if mo.group(1).isdigit():
                                #Add to this trade's dataframe
                                tradeDict.update({mo.group(2):-int(mo.group(1))})
                            else:
                                removeFlag = 1 #Bad listing, remove
                        else:
                            #Look for Perfect Amethyst
                            mo = regexOfferGems.search(entry)
                            if mo is not None:
                                if mo.group(1).isdigit():
                                    #Add to this trade's dataframe
                                    tradeDict.update({'Perfect Amethyst':-int(mo.group(1))})
                                else:
                                    removeFlag = 1 #Bad listing, remove
                            else:
                                removeFlag = 1 #Bad listing, remove
                    if removeFlag == 0:
                        #Add Trade to Dataframe
                        if max(tradeDict.values())<1:
                            print('')
                        dfRunes = pd.concat([dfRunes,pd.DataFrame(tradeDict, index=[len(dfAllRunes)+len(dfRunes)])])
                        
    #Finish Data Frame
    #dfRunes = dfRunes.fillna('')
    dfAllRunes = pd.concat([dfAllRunes.astype(dfRunes.dtypes),dfRunes.astype(dfAllRunes.dtypes)])
    
    #Wait to avoid Cloudflare issues
    time.sleep(10)

#Print Results
print(dfAllRunes.fillna(''))

#Add to Database
with sqlite3.connect('DiabloIIrunes.db') as conn:
    cursor = conn.cursor()
    dfAllRunes.to_sql('RUNES', conn, if_exists='replace',index=False)