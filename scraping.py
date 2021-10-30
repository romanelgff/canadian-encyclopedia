#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 12 20:37:09 2021

@author: romanelgff
"""

# Importing required packages
import sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup, Tag, NavigableString
from multiprocessing import Pool, cpu_count
import time, pickle

def validTag(tag):
    if tag.name in ['style','sup']:
        return False
    if "class" in tag.attrs: 
        for c in tag.attrs["class"]: #renvoie la liste des classes de la balise
            if c in ['article-content-body hide']:
                return False
    return True

def getSelectedText(tag): #fonction recursive
    texte = ' '
    if validTag(tag):
        for child in tag.children:
            if type(child) == NavigableString:
                texte += " "+(child.string).strip() 
            if type(child) == Tag:
                texte += getSelectedText(child)
    return texte

def parseURL(url): #fonction recuperant l'url de l'article, le titre et le contenu
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML,like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    req = Request(url, headers={'User-Agent': user_agent})

    try : 
        response = urlopen(req)
    except (HTTPError, URLError) as e : 
        sys.exit(e) 
    bsObj = BeautifulSoup(response, "lxml")
    
    titre = bsObj.find("h1").text 
    texte = " "
    div = bsObj.find("div", class_= "article-content")
    
    texte = getSelectedText(div)
    return (url, titre, texte)

if __name__ == '__main__':

    url = 'https://www.thecanadianencyclopedia.ca/en/browse/things/science-technology/inventions-and-innovations?type=article' 
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML,like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    
    #objet request
    req = Request(url, headers={'User-Agent': user_agent})
    
    try : #gestion des exceptions avec un bloc try/except
        response = urlopen(req)
    except (HTTPError, URLError) as e : 
        sys.exit(e) #sortie du programmme avec affichage de l'erreur
    
    #objet BeautifulSoup
    bsObj = BeautifulSoup(response, "lxml")
    #print(bsObj.prettify())

    div1 = bsObj.find("main", class_ = "wrap--narrow l l--hasSidebar search-listing-result")
    #print(div1.prettify())
        
    a_list = div1.find_all('a')
    #print(a_list)
    
    #creation d'une liste sans doublons des url (chaque url apparaissant deux fois dans la source des articles)
    url_list = [a.attrs['href'] for a, i in zip(a_list, range(len(a_list))) if i % 2 == 0]

    #liste des pages a scrapper en plus de la page principale, recuperee a partir de la liste d'url ci-dessus
    pages_list = [url for url in url_list if "page" in url]
    #print(pages_list)
    
    #reiteration du processus de recuperation des url pour les pages de la liste pages_list
    for page in pages_list:
        
        req2 = Request(page, headers={'User-Agent': user_agent})
        
        try : 
            response2 = urlopen(req2)
        except (HTTPError, URLError) as e : 
            sys.exit(e) 
        
        bsObj2 = BeautifulSoup(response2, "lxml")
        div2 = bsObj2.find("main", class_="wrap--narrow l l--hasSidebar search-listing-result")
        liste_a2 = div2.find_all('a')
        
        url_list.append([a.attrs['href'] for a, i in zip(liste_a2, range(len(liste_a2))) if i % 2 == 0])
    
    url_list = [url for url in url_list if "article/" in url] #liste finale ne contenant que les articles
    #print(url_list)
    
    #print(parseURL(url_list[3]))
    tuples_list = []
    start = time.time()
    with Pool(cpu_count()-1) as p:
        tuples_list = p.map(parseURL, url_list)
    print(time.time()-start)

    with open('infos.pick', 'wb') as pickFile:
        pickle.dump(tuples_list, pickFile)