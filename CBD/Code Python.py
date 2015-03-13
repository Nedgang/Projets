#!/usr/bin/python
# -*- coding: utf-8 -*-



##########
# IMPORT #
##########

import sqlite3          # Import a tool to create SQL database and interact with it
import csv      
import os               # Allow to interact with system files
import glob             # Take files from a directory
from Tkinter import *   # Module for GUI
import networkx as nx   # Allow to draw interaction graphs
import matplotlib.pyplot as plt
import pylab


######################
# DATABASE FUNCTIONS #
######################

def createDatabase(name="Hepc_Retro.sq3", data=os.getcwd()+"/data_hepcidin"):
    """ Create a database, by default the one asked for the CBD project.
    name: Enter the name of the database (string)
    data: the path of the data directory (string)
    """
    if (name[-4:]!='.sq3'):                 # To be sure that all the bases will have tche correct extension, allowing me to count them.
        name=name+'.sq3'
    
    if (exist(name)):
        print ("La base de données existe déjà!")

    else:
        database = os.getcwd()+"/"+name     # Creation of a file containingg my database: os.getcwd() is the method allowing to obtain the path of my current working directory, which contain my script.
        conn = sqlite3.connect(database)    # Creation of an object to connect my programm to the database
        cur = conn.cursor()                 # Creation of a cursor to allow me to cancel my actions
        
        for f in glob.glob(data+"/*"):
            fName = os.path.splitext(os.path.basename(f))[0]    # Allow to have the name of the file without the .txt
            print ("Creation of the table "+fName+" for: "+os.path.basename(f))
            cur.execute("CREATE TABLE "+fName+""" ( SourceId varchar(10), SourceLabel varchar(250), SourceEntityType varchar(1), EdgeLabel varchar (250), TargetId varchar(250), TargetLabel varchar(250),
    TargetEntityType varchar(1), PUBMED_ID varchar(8), nsent int, ntagged_nsent int, nsent_nrelation int, Period varchar(10))""")
            
            with open(f, "r") as tsvin :      # Open the file f, using his path
                tsvin = csv.DictReader(tsvin, delimiter="\t")   # Read the file and stock it in tsvin
                for row in tsvin :
                    insertstr = "INSERT INTO "+fName+" VALUES("+"\""+row["SourceId"]+"\""+","+"\""+row["SourceLabel"]+"\""+","+"\""+row["SourceEntityType"]+"\""+","+"\""+row["EdgeLabel"]+"\""+","+"\""+row["TargetId"]+"\""+","+"\""+row["TargetLabel"]+"\""+","+"\""+row["TargetEntityType"]+"\""+","+"\""+row["PUBMED_ID"]+"\""+","+row["nsent"]+","+row["ntagged_nsent"]+","+row["nsent_nrelation"]+","+"\""+row["period"]+"\""")"
                    cur.execute(insertstr)

        conn.commit()   # Allow the changes to go into my database
        cur.close()     # Close the cursor
        conn.close()    # Close the connector
    

def deleteDatabase(name="Hepc_Retro.sq3", database=os.getcwd()):
    """ Delete a database, by default the one asked for the CBD project.
    name: Enter the name of the database (string)
    database: The path to the database file
    """
    if (name[-4:]!='.sq3'):
        name=name+'.sq3'

    os.remove(database+'/'+name)


def exist(name):
    # Verification if the database already exist
    for f in glob.glob(os.getcwd()+"/*"):
        if f == os.getcwd()+"/"+name:
            return True
    return False


def getDatabase(path=os.getcwd()):
    """ Return all the database existing in the path. Default: working directory.
    path: path of database directory (string)
    """
    for f in glob.glob(path+"/*"):
        if (f[-4:]=='.sq3'):
            print (os.path.basename(f))




##################
# USER FUNCTIONS #
##################

# Besoin 1:
def protAsso(nameProt="Hepcidin", nameBase="Hepc_Retro.sq3"):
    """Return the proteins associated to the nameProt by year
    nameProt: the name of the protein (string)
    nameBase: databasename (string)
    """
    result = _protAsso(nameProt, nameBase)
    a=2001
    for i in result:
        print("Protéines associées à "+nameProt+" dans les données de l'année "+str(a))
        print(i)
        print("")
        a=a+1
    a=2001
    for j in result:
        print ("In "+str(a)+", "+str(len(j))+" "+nameProt+" associated proteins detected.")
        a=a+1

def _protAsso(nameProt="Hepcidin", nameBase="Hepc_Retro.sq3"):
    """Return the proteins associated to the nameProt by year
    nameProt: the name of the protein (string)
    nameBase: databasename (string)
    """
    database = os.getcwd()+"/"+nameBase  
    conn = sqlite3.connect(database)        
    cur = conn.cursor()

    result=[]

    for i in range(2001, 2012):    
        cur.execute("SELECT DISTINCT TargetLabel FROM events_"+str(i)+" WHERE SourceEntityType='P' AND TargetEntityType='P' AND UPPER(SourceLabel) LIKE UPPER('%"+nameProt+"%')")
        tmp=list(cur)
        
        clean=[]    # Base avec des noms non normalisés! Donc on vérifie pour chacun.
        for m in tmp:
            n = str(m[0])
            if n.lower() not in clean:
                clean.append(n.lower())
        result.append(clean)
        
    return result
    
    cur.close()     
    conn.close()       


# Besoin 2
def diseaseAsso(nameProt="Hepcidin", nameBase="Hepc_Retro.sq3"):
    """Return diseases associated to nameProt by year
    nameProt: the name of the protein (string)
    nameBase: databasename (string)
    """
    database = os.getcwd()+"/"+nameBase  
    conn = sqlite3.connect(database)        
    cur = conn.cursor()     

    for i in range(2001,2012):
        result=[]
        cur.execute("SELECT DISTINCT TargetLabel FROM events_"+str(i)+" WHERE SourceEntityType='P' AND TargetEntityType='I' AND UPPER(SourceLabel) LIKE UPPER('%"+nameProt+"%')")
        print("Maladies associées à "+nameProt+" dans les données de l'année "+str(i))
        tmp=list(cur)

        clean=[]    # Base avec des noms non normalisés! Donc on vérifie pour chacun.
        for m in tmp:
            n = str(m[0])
            if n.lower() not in clean:
                clean.append(n.lower())
        result.append(clean)
        print clean
        print("")

    cur.close()     
    conn.close()    


# Besoin 3
def redondProt(nameProt="Hepcidin", nameBase="Hepc_Retro.sq3"):
    """Return the proteins that detected in 2+ years
    nameProt: the name of the protein (string)
    nameBase: databasename (string)
    """
    database = os.getcwd()+"/"+nameBase  
    conn = sqlite3.connect(database)        
    cur = conn.cursor()

    total=[]    # To countain the result of the SELECT command on all the tables
    count={}    # To be used to count each protein
    result=[]   # To contain all the proteins found 2+ times
    
    for i in range(2001, 2012):    
        cur.execute("SELECT DISTINCT TargetLabel FROM events_"+str(i)+" WHERE SourceEntityType='P' AND TargetEntityType='P' AND UPPER(SourceLabel) LIKE UPPER('%"+nameProt+"%')")
        tmp=list(cur)
        total=total+tmp

    for p in total:     
        if p[0] != '':
            if p[0] not in count:
                count[p[0]]=1
            else:
                count[p[0]]+=1

    for j in count:
        if count[j] > 1:
            result.append(str(j))

    print result
    
    cur.close()     
    conn.close()   


# Besoin 4
def publBackgrd(nameProt="Hepcidin", nameBase="Hepc_Retro.sq3"):
    """Return all the publications about nameProt-protein interaction.
    nameProt: the name of the protein (string)
    nameBase: databasename (string)
    """
    database = os.getcwd()+"/"+nameBase  
    conn = sqlite3.connect(database)        
    cur = conn.cursor()

    total=[]
    result=[]

    for i in range(2001, 2012):    
        cur.execute("SELECT DISTINCT PUBMED_ID FROM events_"+str(i)+" WHERE SourceEntityType='P' AND TargetEntityType='P' AND UPPER(SourceLabel) LIKE UPPER('%"+nameProt+"%')")
        tmp=list(cur)
        print "Évenements background en",i , ":",len(tmp)
        total=total+tmp

    print "Évenements background au total :", len(total)
    
    cur.close()     
    conn.close()
    


#############
# INTERFACE #
#############

def displayProtAsso():
        
    data = _protAsso()
    
    G=nx.Graph()    # Crease a new graph
    m=2001          # Year counter

    

    G.add_node('H')
    for y in data:
        for i in y:
            name=(i)
            if name not in G.nodes(): # Add a new prot only if it is not already on the graph.
                G.add_node(name)
                G.add_edge(name, 'H')

        #pos=nx.spring_layout(G)
        #nx.draw_networkx_labels(G,pos,font_size=10,font_family='sans-serif')
        plt.axis('off')
        plt.title("Hepcidin associated proteins in "+str(m)+": "+str(len(G.nodes())-1)+" proteins")
        nx.draw(G)
        plt.savefig(os.getcwd()+"/Int_prot_prot_"+str(m)+'.png')
        pylab.close()
        print("Graph pour l'année "+str(m)+" fait.")
        m=m+1




