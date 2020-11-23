#!/usr/bin/env python
# coding: utf-8

# load necessary libraries
import pandas as pd
import codecs 
import numpy as np

import requests
import urllib.request
import time
from bs4 import BeautifulSoup
from urllib.request import urlopen
import re
import string
import os
import csv


dc_names = 'https://www.elections.gov.hk/dc2019/eng/results_hk.html'

html = urlopen(dc_names)

soup = BeautifulSoup(html, 'html.parser')

tables = soup.find_all('table')

constituencies_web = []
constituency_names = []

for table in tables:
    rows = table.find_all('tr')
    
    for row in rows:
        cells = row.find_all('td')
        
        if len(cells) > 3: # to skip the first row
            
            constituency = cells[1].text.strip()
            #constituencies_web.append(string.capwords(constituency).replace(' ', '_') + '_(constituency)')
            constituency_names.append(string.capwords(constituency))



print(constituency_names)



urls = []

# create urls for the constituencies
for constituency in constituencies_web:
    url = 'https://en.wikipedia.org/wiki/' + constituency
    urls.append(url)
    
print(urls)
    


constituencies = []
parties = []
candidates = []
votes = [] 


for url in urls:
        req = urllib.request.Request(url)
        
        try:
            urllib.request.urlopen(req)
            
        except urllib.error.URLError as e:
            print(e.reason)
            
        except urllib.error.HTTPError as e:
            print(e.code)
        
        else:
            html = urlopen(url)
            soup = BeautifulSoup(html, 'html.parser')
        
            table = soup.find(style="background-color:#f2f2f2;margin-bottom:-1px;border:1px solid #aaa;padding:.2em .4em").find_parent('table')
                
            rows = table.find_all('tr')[1:]
        
        for row in rows:
            cells = row.find_all('td')
    
            if len(cells) > 4:
                party = cells[1]
                parties.append(party.text.strip())
            
                candidate = cells[2]
                candidates.append(candidate.text.strip())
            
                vote = cells[3]
                votes.append(vote.text.strip().replace(',', ''))
                
                constituency = re.sub('https://en.wikipedia.org/wiki/(.*?)\(constituency\)', r'\1', url)
                constituencies.append(re.sub('\_', ' ', constituency))
    


print(constituencies, parties, candidates, votes)


constituencies = [re.sub('\_', '', x) for x in constituencies]

constituencies = [x.rstrip() for x in constituencies]

zippedList = list(zip(constituencies, parties, candidates, votes))


wiki_vote = pd.DataFrame(zippedList, columns = ['constituencies' , 'parties', 'candidates', 'votes'], index=range(len(votes)))

print(wiki_vote)

wiki_vote.to_csv(r'C:\Users\user\Documents\2019-2020\dissertation\dissertation\vote_wiki.csv',
         index = False, header = True)

# find out which constituencies are not in wikivote
try1 = pd.Series(constituency_names, name = '19constituencies')
# notin = np.logical_not(wiki_vote['constituencies'].isin(constituency_names))
try1[np.logical_not(try1.isin(wiki_vote['constituencies']))]


# scrape 2015 results

results2015 = 'https://www.elections.gov.hk/dc2015/eng/results_hk.html'

html = urlopen(results2015)

soup = BeautifulSoup(html, 'html.parser')

table = soup.find('table', class_= 'contents2')

rows = table.find_all('tr')


CACODE15 = []
winners15 = []
star = '*'
    
for row in rows:
    cells = row.find_all('td')

    if len(cells) == 5:
        vote = cells[4].text.strip()
        
        if star in vote: # to skip the first row
            
            winner = cells[3].text.strip()
            winners15.append(string.capwords(winner))
            
    if len(cells) == 3:
        vote = cells[2].text.strip()
        
        if star in vote: # to skip the first row
            winner = cells[1].text.strip()
            winners15.append(string.capwords(winner))



# scrape 2011 results 


results2011 = 'https://www.elections.gov.hk/dc2011/eng/results_hk.html'

html = urlopen(results2011)

soup = BeautifulSoup(html, 'html.parser')

table = soup.find('table', class_= 'contents2')

rows = table.find_all('tr')

# cells = rows[1].find_all('td')

# print(cells[4])

# print('*' in cells[4].text.strip())

winners11 = []
star = '*'
    
for row in rows:
    cells = row.find_all('td')

    if len(cells) == 5:
        vote = cells[4].text.strip()
        
        if star in vote: # to skip the first row
            
            winner = cells[3].text.strip()
            winners11.append(string.capwords(winner))
            
    if len(cells) == 3:
        vote = cells[2].text.strip()
        
        if star in vote: # to skip the first row
            winner = cells[1].text.strip()
            winners11.append(string.capwords(winner))

# create a candidate list for 2019
# https://stackoverflow.com/questions/62031303/how-to-scrape-data-with-merged-cells

results2019 = 'https://www.elections.gov.hk/dc2019/eng/results_hk.html'

html = urlopen(results2019)

soup = BeautifulSoup(html, 'html.parser')

table = soup.find('table')

rows = table.find_all('tr')

# in order to match with the dc2015 name arrangements
CACODE19 = []
candidatenames = []
votes = []
constituency19 = []

for tr in rows:
    cells = tr.select('td, th')
    if len(cells) != 3:
        CACODE = cells[0].get_text(strip=True)
        constituency = cells[1].get_text(strip=True)
    CACODE19.append(CACODE)
    constituency19.append(string.capwords(constituency))
    candidatename, vote = cells[-2:]
    candidatename = candidatename.get_text(strip=True)
    candidatenames.append(string.capwords(candidatename))
    vote = vote.get_text(strip=True)
    votes.append(re.sub(',|\*', '', vote))
    


print(CACODE19, constituency19, candidatenames, votes)


zippedList19 = list(zip(CACODE19, constituency19, candidatenames, votes))

results19 = pd.DataFrame(zippedList19, columns = ['CACODE19' , 'constituency19', 'candidatenames', 'votes'], index=range(len(votes)))[1:]

results19[1:].to_csv(r'C:\Users\user\Documents\2019-2020\dissertation\dissertation\result19.csv',
         index = False, header = True)




# check if candidate has been winner last term 

candidates = pd.read_csv(r'C:\Users\user\Documents\2019-2020\dissertation\dissertation\candidate_compiled.csv')

candidates['winner_15'] = candidates['candidatenames'].isin(winners15)

candidates['winner_11'] = candidates['candidatenames'].isin(winners11)

print(candidates)


candidates['winnerstreak'] = np.where(candidates['affiliation'] == 'pro-establishment' & 
                                      candidates['winner_15'] == 'True' &
                                      candidates['winner_11'] == 'False', 'True', 'False')

condition = [(candidates['affiliation'] == 'pro-establishment') & (candidates['winner_15'] == 'True') & (candidates['winner_11'] == 'True')]
values = [1]
candidates['winnerstreak'] = np.select(condition, values)

candidates.to_csv(r'C:\Users\user\Documents\2019-2020\dissertation\dissertation\candidate_compiled.csv',
         index = False, header = True)

