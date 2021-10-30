#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 08:57:23 2021

@author: romanelgff
"""

# Importing required packages
from scipy.ndimage import gaussian_gradient_magnitude
import os
from pandas import DataFrame, Series, concat
from PIL import Image
import re, math, pickle
from wordcloud import WordCloud, ImageColorGenerator
import matplotlib.pyplot as plt
import numpy as np

# Definition des fonctions
def getTokens(doc):
    regex = r"""\w+"""
    tokens = [word.strip().lower() for word in re.findall(regex, doc)]
    return tokens

# Definition des classes
class DTM:
    def __init__(self, tuple_list, stop_words):
        
        #recuperation des titres et des URL
        the_url = []
        the_titles = []

        for tuple in tuple_list : #parcour de chaque document et construction d'un dico a partir de l'occurence des mots
            the_url.append(tuple[0])
            the_titles.append(tuple[1])
            
        #stockage des url, titres et mots vides anglais
        self.url = the_url 
        self.title = the_titles
        self.stopWords = stop_words

        #construction du dataframe de mots
        docs_terms = []  #liste de dictionnaires, qui compte le nombre d'occurrences de chaque terme dans chaque doc
        for tuples in tuple_list :
            text = tuples[2]
            the_words = getTokens(text)
            dictio = {} #dictionnaire comptant le nombre d'occurrences de chaque mot
            for word in the_words :
                if word not in self.stopWords: #gestion des mots vides
                    dictio[word] = dictio.get(word,0)+1
            docs_terms.append(dictio)
        self.data = DataFrame(docs_terms).fillna(0)
    
        df = self.data.astype('bool').sum()
        nbdoc = self.data.shape[0]
        log_idf = [math.log(nbdoc/value) for value in df]
        
        #remplissage du dataframe avec le tf.idf attribuant des "scores" pour chaque mot
        self.data = self.data.div(self.data.max(axis=1),axis=0)
        self.data = self.data.mul(log_idf,axis=1)
 
    def __repr__(self): #affichage du tableau tf.idf
        return self.data.__repr__()
    
    def nBest(self, N): #renvoie les N termes les plus frequents du corpus entier
        return self.data.sum().sort_values(ascending=False)[:N]

    def nBestDoc(self, N, integer): #renvoie les N termes les plus frequents du document choisi en second argument (integer numero du doc)
        return self.data.iloc[integer].sort_values(ascending=False)[:N] 

    def query(self, query): #renvoie la liste de documents contenant les mots de la requete query
        valid_words = [word for word in query.split() if word not in self.stopWords]
        
        if len(valid_words)==0:
            return ()
        
        if not all (word in self.data.columns for word in valid_words):
            return () #si tous les mots de la requete ne sont pas des mots connus on revoit liste nulle
        
        the_url = []
        for i in self.data.index:
            if all([self.data.loc[i,word]>0 for word in valid_words]):
                the_url.append(self.url[i])
        return the_url
    
    def queryScore(self, query, N): #renvoie les N documents avec les plus pertinents (par rapport a la requete query)
        valid_words = [word for word in query.split() if word not in self.stopWords]
        if not all (word in self.data.columns for word in valid_words):
            return "Please enter other words. The words you entered were not all in the document specified."
        
        scores = self.data[valid_words].sum(axis=1)
        
        return concat({'score':scores,'url':Series(self.url)},axis=1).sort_values(by='score',ascending=False)[:N]

    def wordCloudParrot(self, numDoc):
        
        #inspiration github pour un wordcloud en forme de perroquet
        #source: https://github.com/amueller/word_cloud/blob/master/examples/parrot.py
        d = os.path.dirname(__file__) if "__file__" in locals() else os.getcwd() #securite au cas ou pas bon repertoire
        
        parrot_color = np.array(Image.open(os.path.join(d, "image/parrot-by-jose-mari-gimenez2.jpg"))) #recuperation des couleurs du perroquet
        parrot_color = parrot_color[::3, ::3]
        
        #creation du "mask" du perroquet, le blanc n'est pas pris en compte 
        parrot_mask = parrot_color.copy()
        parrot_mask[parrot_mask.sum(axis=2) == 0] = 255 
        
        #delimination des bords
        edges = np.mean([gaussian_gradient_magnitude(parrot_color[:, :, i] / 255., 2) for i in range(3)], axis=0)
        parrot_mask[edges > .08] = 255
        
        #recuperation des 200 mots les plus pertinents du doc numDoc pour former un nuage de 200 mots
        words = self.nBestDoc(200, numDoc)
        #generate_from_frequencies() necessaire pour prendre compte les scores attribues aux mots du document
        wordcloud = WordCloud(mask=parrot_mask, max_font_size=40, random_state=42, relative_scaling=0).generate_from_frequencies(words)
        
        #generation des couleurs
        image_colors = ImageColorGenerator(parrot_color) 
        wordcloud.recolor(color_func=image_colors)
        wordcloud.to_file("image/parrot_doc{}.png".format(numDoc)) #sauvegarde du nuage de mots en perroquet dans le dossier image du projet
        plt.figure(figsize=(10, 10))
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        plt.show()
        
        return "Parrot Wordcloud"
        
    def wordCloud(self, numDoc):  
        wordcloud = WordCloud(background_color='white').generate_from_frequencies(self.nBestDoc(100, numDoc))
        wordcloud.to_file("image/wordcloud_doc{}.png".format(numDoc)) #sauvegarde du nuage de mots dans le dossier image du projet
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        plt.show()
        
        return "Classic Wordcloud with white background"
        
    def nMostSimilar(self, numDoc, N):
        doc1 = self.data.iloc[numDoc]
        sim = []
        documents = []
        
        for i in self.data.index:
            
            doc2 = self.data.iloc[i]
            dot_product = np.dot(doc1,doc2) #calcul du produit scalaire entre les deux documents (numDoc et celui de la boucle)
            norm_product = np.linalg.norm(doc1) * np.linalg.norm(doc2)
            
            sim.append(dot_product/norm_product) #formule du cosinus de similarite
            documents.append(self.title[i])
            
        return concat({'similarity':Series(sim),'docs':Series(documents)},axis=1).sort_values(by='similarity',ascending=False)[1:N+1]

# Programme principal
if __name__ == '__main__':
        
    #lecture du fichier pickFile genere au dessus
    with open("infos.pick", 'rb') as pickFile :
        doc = pickle.load(pickFile)
    
    #creation d'une liste des mots vides anglais
    with open("stop_words.txt",'r',encoding='utf8') as textFile :
        stop_words = []
        for word in textFile :
            if word !="":
                stop_words.append(word.strip())
    
    myDTM = DTM(doc, stop_words)
    
    # Test des nouvelles methodes creees
    print(myDTM.queryScore("this a new development because some countries have done research for years", 4)) #les 4 documents et leur url les plus pertinents pour la requete
    print(myDTM.queryScore("je suis un perroquet", 7)) #test avec des mots qui n'existent pas dans le document
    print(myDTM.wordCloud(4)) #nuage de mots classique avec fond blanc pour le document 4
    print(myDTM.wordCloudParrot(4)) #nuage de mots en forme de perroquet pour le document 4
    print(myDTM.nMostSimilar(3,3)) #les trois documents les plus similaires au document 3