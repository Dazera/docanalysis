# -*- coding: utf-8 -*-
"""
Created on Sun Jul 11 17:15:24 2019

@author: RubenTsui@gmail.com
"""
### 

import re

# Given a string of characters, add characters to existing dictionary 
def AddChar2Dict(s, D):
    '''
    Input:
        s: a string of characters
        D: a dictionary of characters: key=character, value=character count
    Output:
        The augmented dictionary
    '''
    for c in s: # loops through s character by character
        if c in D: # if c already exists as a key
            D[c] += 1 # add count by 1
        else: # otherwise just add it to the dictionary
            D[c] = 1
    #return D

##### Build 《重編國語辭典修訂本》（版本編號：2015_20190329） word list 
### Source: https://resources.publicense.moe.edu.tw/dict_reviseddict_download.html
MOE_DICT = {} # only 2-character words are considered
with open('MOE_dict_revised.txt', 'r', encoding='utf-8') as fh:
    for line in fh:
        word = line.strip()
        if len(word) == 2:  # keep only 2-character words
            MOE_DICT[word] = 1
        
len(MOE_DICT)


#### Function to find 2-character words containing a particular character

# Given a string of characters, add "words containing a character" to existing dictionary 
# Given a string of characters, add "words containing a character" to existing dictionary 
def AddWord2Dict(s, D):
    '''
    Input:
        s: a string of characters
        D: a dictionary of characters: key=character, value=character count
    Output:
        The augmented dictionary
    '''
    word_candidates = []
    for i, x in enumerate(list(s[:-1])):
        word_candidates.append(s[i:i+2])
    # check against MOE_DICT
    words = []
    for w in word_candidates:
        if w in MOE_DICT:
            if w in D:
                D[w] += 1 
            else:
                D[w] = 1

    

#############################################################
### Function to collect documents (combining 'broken-up'
### ones into one string per document)
#############################################################
def getIndentedDocuments(soup):
    '''
    Input:
        soup: bs4.BeautifulSoup object, usually a parsed HTML document 
    Output:
        list of documents (within each document, 'broken-up' parts are delimited by '\n')
    '''
    DocList = []
    for item in soup.find_all("div", {'style': True}):  # find all div's with 'style' attribute
        # if current item is an indent (0,2) or (2,2), 
        # then check previous sibling
        if item["style"] in ["text-indent:0em;padding-left:2em;", "text-indent:2em;padding-left:2em;"]:
            x = item.find_previous_sibling()
            # if previous sibling is a div with indent (2,2),
            # then current item is a continuation of it, so "append" it (as a string)
            # to the last element in DocList
            if x.name == 'div' and x["style"] in ["text-indent:0em;padding-left:2em;", "text-indent:2em;padding-left:2em;"]:
                    DocList[-1] += f"\n{item.text}"
            else: # otherwise current item is a standalone document
                DocList.append(item.text)

    return DocList


#############################################################
### Function to extract main text (full text 
### minus commentaries) from book
#############################################################
def getQuotedDocuments(soup, minchars=250):
    '''
    Input:
        soup:     bs4.BeautifulSoup object, typically a bs4-parsed HTML document 
        minchars: minimum no. of characters 
    Output:
        list of quoted documents (text enclosed between Chinese quotation marks「」)
    '''

    regex_quoted = re.compile(r"(?<=「)[^「]{{{minchars},}}?(?=」)")  # lookaround - look ahead for 」; look behind for 「
    regex_quoted = re.compile(r"(?<=「)[^「]{" + str(minchars) + r",}?(?=」)")  # lookaround - look ahead for 」; look behind for 「

    DocList = []
    # "regular" text
    regs = soup.find_all('div', {'style': re.compile(r"text-indent:[20]em;padding-left:0em;")})
    # extract quoted docs from "regular" text
    for r in regs:
        DocList.extend(regex_quoted.findall(r.text))
        
    return DocList



#############################################################
### Function to extract quoted documents from 
### book.commentaries
#############################################################
def getQuotedDocumentsFromCommentaries(txt, minchars=250):
    '''
    Input:
        txt:     string, a text from book.commentaries 
        minchars: minimum no. of characters 
    Output:
        list of quoted documents (text enclosed between Chinese quotation marks「」)
    '''
    regex_quoted = re.compile(r"(?<=「)[^「]{250,}?(?=」)")  # lookaround - look ahead for 」; look behind for 「

    DocList = []
    # extract quoted docs from input text txt
    DocList.extend(regex_quoted.findall(txt))
        
    return DocList


######################################################################
#### Print top n of dictionary entries by value, in descending order
#### value in each (key, value) pair must be numerical
######################################################################
punctuations = '，；。：「」？！、『』（）〔〕[]０(),;.:"'
def DictTopN(D, n, Punct=False):
    ### D: input dictionary
    ### n: number of top entries to display
    ### Punct: whether punctuation marks should be included
    if Punct:
        s = [(k, D[k]) for k in sorted(D, key=D.get, reverse=True)]
    else:
        s = [(k, D[k]) for k in sorted(D, key=D.get, reverse=True) if k not in punctuations]
    return s[:n]


#################################################################
# Converting bewteen en-zh history book names
# (the en names correspond to the folder names for the HTML files)  
#################################################################
HistoryE2C = {}
HistoryC2E = {}
with open("History_Books.txt", "r", encoding='utf-8') as f:
    for line in f:
        (en, zh) = line.strip().split('\t')
        HistoryE2C[en] = zh
        HistoryC2E[zh] = en
Histories = list(HistoryE2C.keys())






