from urllib.request import urlopen
from bs4 import BeautifulSoup
import numpy as np
from array import array
import pandas as pd
from tabulate import tabulate

def get_table():
    soup = BeautifulSoup(urlopen("https://www.sbsolver.com/t/answers"), 'lxml')
    arr = [element.text for s in soup.find_all('td') for element in s]
    lens = [eval(i) for i in arr[1:arr.index('tot')]]
    tot_idxs = [idx for idx, char in enumerate(arr) if char == 'tot']
    grid = arr[tot_idxs[0]+1:tot_idxs[1]]
    grid = [0 if g == '-' else g for g in grid]
    grid = [grid[i:i + 2 + len(lens)] for i in range(0, len(grid), 2 + len(lens))]
    
    for gi in range(len(grid)):
        grid[gi] = list((grid[gi][0], *(int(gg) for gg in grid[gi][1:])))

    df  = pd.DataFrame([g[1:-1] for g in grid], index = [g[0] for g in grid], columns=lens)
    twoltr = arr[tot_idxs[1]+len(df.columns)+2:arr.index('word')]
    for i in range(len(twoltr)):
        twoltr[i] = twoltr[i].replace('\xa0x\xa0', '')
    return df, twoltr


def johnson(words, df, twoltr): 
#     copy of df to return at end
    df2 = df.copy(deep = True)

#     Subtracting from grid based on words (first letter and length)
    words = list(filter(None, set(words[:-1].upper().split("\n"))))
    for word in words:
        df.loc[word[0:1], len(word)] -= 1
    
#     Removing rows with zero valules
    for char in df.index:
        if(sum(df.loc[char]) == 0):
            df = df.drop(index = char)
    
#     Removing cols with zero values
    for wordLen in df.columns:
        if(sum(df[wordLen]) == 0):
            del df[wordLen]

    newltr = []
    for x in range(len(twoltr)):
        twochars = twoltr[x][0:2]
        nums = eval(twoltr[x][2:])
        for word in words:
            if(word[0:2].upper() == twochars.upper()):
                nums -= 1
        if(nums == 1):
            newltr.append(twochars)
        elif(nums != 0):
            newltr.append(twochars+str(nums))

    toAdd = []
    for char in df.index:
        text = ""
        for ltr in newltr:
            if(ltr[0:1]==char):
                text += ltr + " "
        if(text != ""):
            toAdd.append(text)
            
#     print and return
    print(tabulate(df.assign(Two_Ltr=toAdd).replace(0,""), headers = 'keys', tablefmt = 'grid'))
    return df2
