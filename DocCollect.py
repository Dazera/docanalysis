# -*- coding: utf-8 -*-
"""
Created: 2019-07-11
Updated: 2019-07-23
@author: RubenTsui@gmail.com
"""
### 

import re
from zhon import hanzi

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
    # the following for loop creates a list of all bigrams ('gram'==character here)
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
            if x is not None and x.name == 'div' and x["style"] in ["text-indent:0em;padding-left:2em;", "text-indent:2em;padding-left:2em;"]:
                    DocList[-1] += f"\n{item.text}"
            else: # otherwise current item is a standalone document
                DocList.append(item.text)

    return DocList


#############################################################
### Function to extract main text (full text 
### minus commentaries) from book
#############################################################
def getQuotedDocuments(soup, minchars=200):
    '''
    Input:
        soup:     bs4.BeautifulSoup object, typically a bs4-parsed HTML document 
        minchars: minimum no. of characters 
    Output:
        list of quoted documents (text enclosed between Chinese quotation marks「」)
    '''

    regex_quoted = re.compile(fr"(?<=「)[^「]{{{minchars},}}?(?=」)")  # lookaround - look ahead for 」; look behind for 「
    #regex_quoted = re.compile(r"(?<=「)[^「]{" + str(minchars) + r",}?(?=」)")  # lookaround - look ahead for 」; look behind for 「

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
def getQuotedDocumentsFromCommentaries(txt, minchars=200):
    '''
    Input:
        txt:     string, a text from book.commentaries 
        minchars: minimum no. of characters 
    Output:
        list of quoted documents (text enclosed between Chinese quotation marks「」)
    '''
    #regex_quoted = re.compile(r"(?<=「)[^「]{250,}?(?=」)")  # lookaround - look ahead for 」; look behind for 「
    regex_quoted = re.compile(fr"(?<=「)[^「]{{{minchars},}}?(?=」)")  # lookaround - look ahead for 」; look behind for 「

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
# Histories contains a list of folder names (= keys of the dictioary HistoryE2C)
Histories = list(HistoryE2C.keys())


#################################################################
# Change the 'book name' element (Chinese) in Book.flat_meta
# to English (pinyin) for compatibility with other data tables  
#################################################################
def normalizeBookNames(book):
    '''
    Input: an arry of history books 
    Output: same, but with the flat_meta attribute altered
    '''
    if book is not None:
        for vec in book.flat_meta:
            # change index 1 (book title) from zh to en
            if vec is not None:
                vec[1] = HistoryC2E[vec[1]]

#################################################################
# Utility to lookup scroll no. and section given book title and file no.
#################################################################
### Given bookname + fileno, return scroll number

ScrollDict = {}
SectionDict = {}
def processScrollSectionDicts(book):
    for vec in book.flat_meta:
        if vec is not None:
            fileno, bookname, section, scrollno = vec
            ScrollDict[f"{bookname}\t{fileno}"] = scrollno
            SectionDict[f"{bookname}\t{fileno}"] = section
### Given bookname + fileno, return section type (傳, 紀, etc.)

def scrollNum(bookname, fileno):
    '''
    book: Book object
    fileno: HTML file number
    '''
    k = f"{bookname}\t{fileno}"
    if k in ScrollDict:
        return ScrollDict[k]

def sectionType(bookname, fileno):
    '''
    book: Book object
    fileno: HTML file number
    '''
    k = f"{bookname}\t{fileno}"
    if k in SectionDict:
        return SectionDict[k]


#################################################################
# Consolidate commentaries into a dictionary and
# attach it to book.commentaries2
# fileno => [c1, c2, ...]
#################################################################
def consolidateCommentaries(book):
    Comm = {}
    for (i, commentary) in book.commentaries:
        fileno = str(i).zfill(4)
        if fileno in Comm:
            Comm[fileno].append(commentary)
        else:
            Comm[fileno] = []
    book.commentaries = Comm


#################################################################
# Retrieve indented documents from Main Text, 
# and attach a dictionary iDocsM to book
# with the key-value pair:  fileno => [q1, q2, ...]
#
# Retrieve quoted documents from Main Text, 
# and attach a dictionary qDocsM to book
# with the key-value pair:  fileno => [q1, q2, ...]
#################################################################
def RetrieveDocumentsMain(book):
    book.iDocsM = {}  # indented docs from _Main_ text indexed by file no.
    book.qDocsM = {}  # quoted docs from _Main_ text indexed by file no 
    for k, soup in enumerate(book.flat_bodies):
        fileno = str(k).zfill(4)
        # retrieve indented documents
        indented = getIndentedDocuments(soup)
        if indented:
            book.iDocsM[fileno] = indented
        # retrieve quoted documents
        quoted = getQuotedDocuments(soup)
        #if quoted == []: print(f"empty quotes from file {fileno}, book '{book.bookname}'")
        if quoted:
            book.qDocsM[fileno] = quoted


#################################################################
# Retrieve quoted documents from book.commentaries 
# and attach a dictionary qDocsC to book
# with the key-value pair:  fileno => [q1, q2, ...]
#################################################################
def RetrieveDocumentsCommentary(book):
    book.qDocsC = {}  # quoted docs index by file no. 
    for (fileno, commentary_list) in book.commentaries.items():
        #fileno = str(k).zfill(4)
        for commentary in commentary_list:
            quoted = getQuotedDocumentsFromCommentaries(commentary)
            if fileno not in book.qDocsC:
                book.qDocsC[fileno] = []
            else:
                book.qDocsC[fileno].extend(quoted)
    # now remove key-value pairs where value is [] (empty list)
    for k in list(book.qDocsC.keys()):
        if book.qDocsC[k] == []:
            del book.qDocsC[k]


#################################################################
# This function creates the document statistics 
# and attach it to book.docsSummary
#################################################################
def getDocsSummary(book):
    ### Create the union of the 3 sets of keys 
    #all_filenumbers = set(list(book.iDocsM.keys()) + list(book.qDocsM.keys()) + list(book.qDocsC.keys()))
    #all_filenumbers = list(all_filenumbers)
    #all_filenumbers.sort()
    book.docsSummary = []
    #for fileno in all_filenumbers:
    for i in range(len(book.flat_bodies)):
        book.flat_bodies[i].find('a', {'class':'gobookmark'}).extract()  # remove bookmark
        fileno = str(i).zfill(4)
        ## column 'book'
        rec = [book.bookname] # 
        ## column 'fileno'
        rec.append(fileno) # add fileno
        ## column 'scrollno'
        rec.append(scrollNum(book.bookname, fileno))
        ## column 'section'
        rec.append(sectionType(book.bookname, fileno))
        ## column 'grandChar' -- grand total of character in book.flat_bodies[fileno].text 
        rec.append(len(book.flat_bodies[i].body.text))
        ## column commentaryChar
        if book.commentaries is not None and fileno in book.commentaries:
            rec.append(len(''.join(book.commentaries[fileno])))
        else:
            rec.append(0)
        ## columns 'iDocsM', 'iDocsCharM'
        if fileno in book.iDocsM:
            rec.append(len(book.iDocsM[fileno]))           # no. of documents in list
            rec.append(len(''.join(book.iDocsM[fileno])))   # no. of characters across all docs in list 
        else:
            rec.extend([0, 0])
        ## columns 'qDocsM', 'qDocsCharM'
        if fileno in book.qDocsM:
            rec.append(len(book.qDocsM[fileno]))
            rec.append(len(''.join(book.qDocsM[fileno])))
        else:
            rec.extend([0, 0])
        ## columns 'qDocsC', 'qDocsCharC'
        if book.commentaries is not None and fileno in book.qDocsC:
            rec.append(len(book.qDocsC[fileno]))
            rec.append(len(''.join(book.qDocsC[fileno])))
        else:
            rec.extend([0, 0])
        book.docsSummary.append(rec)    


#################################################################
# This function creates, for the given book, 
#   1. one-character dictionary with frequency (no. of occurrences)
#   2. two-character dictionary with frequency 
#################################################################


