#%%
from inspect import Traceback
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import itertools
import folium 
import openrouteservice 
import json

from openrouteservice import convert
from networkx.algorithms.shortest_paths.weighted import dijkstra_path
from itertools import combinations
from functools import partial
from pyproj import CRS
from pyproj import Proj, transform
from ipywidgets import widgets, interact, interactive, fixed, interact_manual
from download import download 
from IPython import get_ipython

pd.options.display.max_rows = 8

#%%
data_co = pd.read_csv("coordonnees.csv", sep = ',')

#La colonne : Nom gare a été remplacé par NomGare dans le csv de base, y'a des espaces qui traines
dta1 = pd.read_csv("gares-peage-2019.csv", sep = ';')

dta1.rename({' NomGare ':'NOMGARE'},axis=1,inplace=True)
dta1.columns = map(lambda x: str(x).upper(), dta1.columns)


#il doit y avoir une valeur x et y dans le csv sous forme de string:'2' à la place de seulement 2, ex dta1.loc[0,'x']='2'
for i in range(len(dta1.index)):
    dta1.loc[i,'X']=float(dta1.loc[i,'X'].replace(',','.'))
    dta1.loc[i,'Y']=float(dta1.loc[i,'Y'].replace(',','.'))

#Extraction des données relatives aux autoroutes A9, A709, A61, A62, A75 et A66
dta_routes = dta1[(dta1.ROUTE=="A0009")|(dta1.ROUTE=="A0709")|(dta1.ROUTE=="A0061")|(dta1.ROUTE=="A0062")|(dta1.ROUTE=="A0075")|(dta1.ROUTE=="A0066")]  
dta_routes = dta_routes[['ROUTE','NOMGARE','X','Y']]

# reafections des indices
dta_routes.reset_index(drop = True, inplace = True)

for i in range(len(dta_routes.NOMGARE)):
    if dta_routes.loc[i,'NOMGARE'] in list(data_co.NOMGARE):
        print(dta_routes.loc[i,'NOMGARE'])

#On constate que le csv ne contient pas toute les sorties disponible,
#Il faut donc aller chercher les sorties sur le second csv donnée en lien,
#i.e le csv trace-du-reseau-autoroutier-doccitanie.

#Continuons tout de même la démarche jusqu'à la créations du tableau 
#contenant les coordonnées gps des villes selectionnées.

for i in range(len(dta_routes.NOMGARE)):
    if (dta_routes.loc[i,'NOMGARE'] not in list(data_co.NOMGARE)):
        dta_routes.drop(i,inplace=True)

dta_routes.reset_index(drop = True, inplace = True)

#transformation des coordonnées Lambert93 en coordonéees GPS

X = dta_routes['X']
Y = dta_routes['Y']
inProj = Proj(init='epsg:2154')
outProj = Proj(init='epsg:4326')
GPS=[]
GPS_x=[]
GPS_y=[]
for i in range(len(dta_routes.index)):
    GPS.append(transform(inProj,outProj,X[i],Y[i]))
GPS
for i in range(len(GPS)):
    dta_routes.loc[i,'X'],dta_routes.loc[i,'Y']=GPS[i]
dta_routes

#Transformation en fichier .csv
dta_routes.to_csv('routes.csv', sep = ';')

# Le csv gares-peage-2019 ne contient pas toutes les routes de notre étude, on peut aller les prendre
# le csv trace-du-reseau-autoroutier-doccitanie.


#%%
#Effectuons la même démarche pour le second csv.

dta2 = pd.read_csv("trace-du-reseau-autoroutier-doccitanie.csv", sep = ';')

dta_routes2 = dta2[(dta2.nom_route=="A9")|(dta2.nom_route=="A709")|(dta2.nom_route=="A61")|(dta2.nom_route=="A62")|(dta2.nom_route=="A75")|(dta2.nom_route=="A66")]  

#On peut remarquer que les noms et les numéros de sorties ne sont pas indiqués
#Par soucis de temps on décide donc d'utiliser le csv data_co de l'un de nos camarades.
#%%

price = pd.read_csv("DataFrame_price.csv", sep=';')
price = price.fillna(0)

price.columns = ([0]+list(data_co.NOMGARE))
price.index = list(data_co.NOMGARE)
del price[0]
#%%
#On utilise pour la suite le tableau obtenue précédement, cependant pour plus de lisibilité
#nettoyons légèrement le tableau des prix, en excluant les sorties de péage nulle.

price2 = price
del price2['VENDARGUES']
del price2['MONTPELLIER EST']
del price2['MONTPELLIER SUD']
del price2['MONTPELLIER OUEST']
del price2['ST JEAN DE VEDAS']
del price2['MONTPELLIER']
del price2['LE BOULOU (OUVERT)']
del price2['PEAGE TOULOUSE SUD/OUEST']
del price2['LE PALAYS']
del price2['PEAGE TOULOUSE SUD/EST']
del price2['MONTAUDRAN']
del price2['LASBORDES']
del price2['SOUPETARD']
del price2['LA ROSERAIE']
del price2['LA CROIX DAURADE']
del price2['BORDEROUGE']
del price2['LES IZARDS']
del price2['SESQUIERES']

for i in ['VENDARGUES','MONTPELLIER EST','MONTPELLIER SUD','MONTPELLIER OUEST','ST JEAN DE VEDAS',
'MONTPELLIER','LE BOULOU (OUVERT)','PEAGE TOULOUSE SUD/OUEST','LE PALAYS','PEAGE TOULOUSE SUD/EST',
'MONTAUDRAN','LASBORDES','SOUPETARD','LA ROSERAIE','LA CROIX DAURADE','BORDEROUGE','LES IZARDS',
'SESQUIERES']:
    price2.drop(i,inplace=True)



#Création de la base de données finale qui contient le prix des péages que nous avons retenus
price2.to_csv('DataFrame_price2.csv')

#%%

#Créations des portions de routes en 5.
Sorties=[0,1,2,3,4,6,7,8,9,10,11,12,13,14,15,16,19,
20,21,22,23,24,25,26,27,29,30,31,33,35,36,37,38,39,40,
41,42]
P1 = [[0,1,2,3,4,6,7,8,9,10,11],[2,3],[]]
P2 = [[12,13,14,15,16,19],[],[1,3]]
P3 = [[20,21,22,23,24,25],[4,5],[1,2]]
P4 = [[26,27,28,29,30],[],[3,5]]
P5 = [[31,33,35,36,37,38,39,40,41,42],[],[3,4]]
P=[P1,P2,P3,P4,P5]
PP = P1[0]+P2[0]+P3[0]+P4[0]+P5[0]

def transforme(a):
    '''transforme le nom de la sortie en entier parmis la "liste Sortie" '''
    if a in PP:
        return(a)
    for i in range(len(data_co.NOMGARE)):
        if a == data_co.NOMGARE[i] :
            if a in [5,17,18,32,34]:
                return("Entrée/sortie invalide")
            return(i)
    return("Entrée/sortie invalide")

def re_transforme(a):
    if a in (list(data_co.NOMGARE)):
        return(a)
    for i in range(len(data_co.NOMGARE)):
        b = data_co.NOMGARE[i]
        if a == transforme(b) :
            return(b)
    return("Entrée/sortie invalide")

def id_portion(a):
    '''retourne à quel portion de route appartient l'entier ou le nom de sortie "a" '''
    a = transforme(a)
    for i in range(5):
        if a in P[i][0]:
            return(i)

def position_portion(a):
    '''retourne l'indice de a(entier/nom de sortie) dans la portion de route auquel il appartient'''
    a = transforme(a)
    i_a = id_portion(a)
    for j in range(len(P[i_a][0])):
        if a == P[i_a][0][j]:
            return(j)

def r(L):
    '''renverse une liste'''
    a = [0]*(len(L))
    for i in range(len(L)):
        a[-(i+1)] = L[i]
    return(a)

def chemin(e,s): 
    '''retourne le trajet des sorties (entier dans la "liste sortie") 
    entre l'entré/sortie (entier/ou nom:string)'''
    e = transforme(e)
    s = transforme(s)
    i_e = id_portion(e)
    i_s = id_portion(s)
    min_pe = position_portion(min(P[i_e][0])) 
    # = 0
    max_pe = position_portion(max(P[i_e][0]))
    min_ps = position_portion(min(P[i_s][0])) 
    # = 0
    max_ps = position_portion(max(P[i_s][0]))
    pp_e = position_portion(e)
    pp_s = position_portion(s)

    if e ==s:
        return("Vous ne prenez aucun itinéraire")
    if (e == 29 and s == 30):
        return("Itinéraire impossible")
    if (e == 30 and s == 29):
        return("Itinéraire impossible")
    if i_e == i_s:
        if e < s:
            return(P[i_e][0][pp_e:pp_s+1])
        return( r(P[i_e][0][pp_s:pp_e+1]) )

    if (i_e+1 in P[i_s][2]) :
        if (i_e == 1) | (i_e == 4)| (i_e ==2 and i_s==1):
            return(r(P[i_e][0][min_pe:pp_e+1])+P[i_s][0][min_ps:pp_s+1])
        return(P[i_e][0][pp_e:max_pe+1]+P[i_s][0][min_ps:pp_s+1])

    if (i_e+1 in P[i_s][1]) :
        if (i_s == 1)|(i_s == 3) :
            return( r(P[i_e][0][min_pe:pp_e+1]) + (P[i_s][0][min_ps:pp_s+1]) )
        return( r(P[i_e][0][min_pe:pp_e+1]) + r(P[i_s][0][pp_s:max_ps+1]) )

    if e < s:
        if (i_e == 1) :
            return( r(P[i_e][0][min_pe:pp_e+1]) + P[2][0] +P[i_s][0][min_ps:pp_s+1])
        else :
            return(P[i_e][0][pp_e:max_pe+1]+ P[2][0] +P[i_s][0][min_ps:pp_s+1])
    else :
        if (i_s == 1) :
            return( r(P[i_e][0][min_pe:pp_e+1]) + r(P[2][0]) + P[i_s][0][min_ps:pp_s+1])
        else :
            return( r(P[i_e][0][min_pe:pp_e+1]) + r(P[2][0]) + r(P[i_s][0][pp_s:max_ps+1]))

def trajet(e,s,k):
    '''liste de tous les trajets possible en k sorties intermédiares 
    entre l'entré/sortie (e/s sous forme entier/string)'''
    e = transforme(e)
    s = transforme(s)
    L = []
    for i in(combinations(chemin(e,s),k+2)): 
        if list(i)[0]==e and list(i)[-1]==s:
            L.append(list(i))
    return(L)

def cout_direct(e,s):
    '''retourne le coût d'un allé direct entre entré/sortie
    (e/s sous forme int/string)'''
    e = transforme(e)
    s = transforme(s)
    prix = float(price.iloc[e,s])     
    # les éléments du tableau price sont des numpy.float et non des float 
    # pause problème lors d'opérations
    return(prix)

#NARBONNE SUD valeur  = 8.58,5 
price.loc['VENDARGUES','NARBONNE SUD'] = '8.585'


def chemin_k_sortie(e,s,k):
    e = transforme(e)
    s = transforme(s)
    L = trajet(e,s,k)
    long_L = len(L)
    L2 = [0]*long_L
    indice = 0
    prix = 1000
    for i in range(long_L):
        L_c = L[i]
        prix_c = 0
        for j in range(len(L_c)-1):
            prix_c = prix_c + cout_direct(L_c[j],L_c[j+1])
        if prix > prix_c:
            prix = prix_c
            indice = i
        L2[i] = prix_c
    return([L[indice],L2[indice]])

def chemin_opt(e,s,k):
    if e==s:
        return("Vous devez choisir une sortie différente de votre point d'entrée")
    opt = chemin_k_sortie(e,s,0)
    for i in range(1,k+1):
        opt_c = chemin_k_sortie(e,s,i)
        if opt_c[1] < opt[1]:
            opt = opt_c 
    for i in range(len(opt[0])):
        opt[0][i] = re_transforme(opt[0][i])
    return(opt)

def nb_sortie_possible(e,s):
    return(len(chemin(e,s))-2)


# carte interactive (Classe Graph)

class Graph(object):
    def __init__(self):
        pass

    def carte(self,DEPART,ARRIVEE):

        client = openrouteservice.Client(key='5b3ce3597851110001cf62486f5564a064e34f3895221e5a0d9a2405')
    
        ligne_DEPART = data_co[data_co.NOMGARE == DEPART].index[0]
        ligne_ARRIVEE = data_co[data_co.NOMGARE == ARRIVEE].index[0]

        x = [data_co.loc[ligne_DEPART,'X'],data_co.loc[ligne_ARRIVEE,'X']]
        y = [data_co.loc[ligne_DEPART,'Y'],data_co.loc[ligne_ARRIVEE,'Y']]
    
        m = folium.Map(
            location=[43.1838000,3.0050000],
            zoom_start=10, 
            control_scale=True)

        coords  = (x[0],y[0]),(x[1],y[1])
        res = client.directions(coords)

        geometry = client.directions(coords)['routes'][0]['geometry'] 
        decoded = convert.decode_polyline(geometry) 

        distance_txt = "<h4> <b>Distance : " + "<strong>"+str(round(res['routes'][0]['summary']['distance']/1000,1))+ " Km </strong>" +"</h4></b>"
        duration_txt = "<h4> <b>Duration : " + "<strong>"+str(round(res['routes'][0]['summary']['duration']/60,1))+ " Min. </strong>" +"</h4></b>"

        folium.GeoJson(decoded).add_child(folium.Popup(distance_txt+duration_txt,max_width=300)).add_to(m)

        folium.Marker(
            location=list(coords[0][::-1]),
            popup="DEPART",
            icon=folium.Icon(color="green"),
            ).add_to(m)

        folium.Marker(
            location=list(coords[1][::-1]),
            popup="ARRIVEE",
            icon=folium.Icon(color="red"),
            ).add_to(m)

        return(m)

#interface 

#selection du tableau des noms des villes nous intéressant!

villes_interface = data_co.NOMGARE
for i in [5,17,18,32,34]:
    villes_interface = villes_interface.drop(i)
villes_interface = list(villes_interface)

def interface_carte(DEPART,ARRIVEE,k):
    a = nb_sortie_possible(DEPART,ARRIVEE)
    if k > a:
        return('le nombre de sortie maximum est', a,'sortie(s)' )
    a = chemin_opt(DEPART,ARRIVEE,k)
    print('le trajet le moins cher pour', k, 'sortie est le trajet', a[0],'il vous coûtera', a[1],'Euros')
    b = Graph()
    b = b.carte(DEPART,ARRIVEE)
    return(b)

interact(interface_carte,DEPART=villes_interface,ARRIVEE=villes_interface,k=(0,25))

