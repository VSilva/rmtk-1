# -*- coding: utf-8 -*-
"""
Created on Wed May 28 18:19:44 2014

@author: chiaracasotto
"""
import numpy as np
import matplotlib.pyplot as plt
from idealisation import bilinear
from idealisation import quadrilinear
from assign_damage import assign_damage
from common.conversions import get_spectral_ratios
import os
import csv

def read_data(in_type,an_type,linew,fontsize,units,flag):
    cd = os.getcwd()
    if in_type == 1: # full pushover curve
        input1 = cd+'/inputs/displacements_pushover.csv' # storeys height and displacements at story levels starting from level 0
        input2 = cd+'/inputs/reactions_pushover.csv' # Base Reactions [kN]
        input3 = cd+'/inputs/building_parameters.csv' # First period of vibration and partecipation factor normalised with respect to top floor
        input4 = cd+'/inputs/limits.csv' # Limit States expressed as drifts

        with open(input3, 'rb') as f:
            reader = csv.reader(f)
            newlist = [row for row in reader]
        T = [float(ele[1]) for ele in newlist[1:]] # First period
        Gamma = [float(ele[2]) for ele in newlist[1:]] # first modal participation factor normalised with respect to the top displ., Dispersions
        w = [float(ele[3]) for ele in newlist[1:]] # weight assigned to each building if multiple buildings are input
        noStorey = [int(ele[4]) for ele in newlist[1:]]
        noBlg = len(T)
        H = []
        for i in range(1,len(newlist)):
            H.append([float(ele) for ele in newlist[i][5:5+int(noStorey[i-1])]])
            #H.append(np.array(newlist[i][5:5+int(noStorey[i-1])],float)) # storeys height [m]
                
        with open(input1, 'rb') as f:
            reader = csv.reader(f)
            newlist = [row for row in reader]
        tmp, disp = [],[]
        tmp.append([[] for i in range(0,len(newlist))]); tmp = tmp[0]
        disp.append([[] for i in range(0,noBlg)]); disp = disp[0]
        for i in range(1,len(newlist)):        
            for ele in newlist[i][2:]:
                if ele is not '':
                    tmp[i-1].append(ele)
            j = int((i-1)/noStorey[0])
            disp[j].append(abs(np.array(tmp[i-1][:],float)))

        with open(input2, 'rb') as f:
            reader = csv.reader(f)
            newlist = [row for row in reader] 
        react = newlist[1:]
        R, tmp = [],[]
        tmp.append([[] for i in range(0,len(react))]); tmp = tmp[0]
        for i in range(0,len(react)):
            for ele in react[i]:
                if ele is not '':
                    tmp[i].append(ele)
            R.append(abs(np.array(tmp[i][1:],float)))

        with open(input4, 'rb') as f:
            reader = csv.reader(f)
            newlist = [row for row in reader]
        newlist = [ele[1:] for ele in newlist]
        limits = np.array(newlist[1::2],float) #limit states [drifts]
        bUthd = np.array(newlist[2::2],float)
        
        if len(limits) < noBlg:
            limits = np.repeat(limits,noBlg,axis=0)
            bUthd = np.repeat(bUthd,noBlg,axis=0)
        bUthd = bUthd.tolist()
        limits = limits.tolist()
            
        # Assign damage to each analysis and return displacement profile at each Limit state attainment
        droof = []
        for blg in range(0,len(disp)):
            droof.append(disp[blg][noStorey[blg]-1]) # roof displacements  
            
        dcroof = []
        for blg in range(0,noBlg):
            [disp_profile] = assign_damage(limits[blg],disp[blg],H[blg],noStorey[blg])
            dcroof.append(disp_profile[noStorey[blg]-1])  # roof displacement at each Limit state
            
        if an_type == 0: # Elastoplastic pushover
        # Bilinearisation of the pushover curve and plot
            SPO = []
            for blg in range(0,noBlg):
                [dy,du,Fy] = bilinear(droof[blg],R[blg],flag,linew,fontsize,units)
                SPO.append([dy,du,Fy]) # yielding disp., ultimate disp., yielding force
        else: # Any pushover shape
            # Quadrilinearisation of the pushover curve and plot
            SPO = []
            for blg in range(0,noBlg):
                [dy,ds,dmin,du,Fy,Fmax,Fmin] = quadrilinear(droof[blg],R[blg],flag,linew,fontsize,units)
                SPO.append([dy,ds,dmin,du,Fy,Fmax,Fmin]) # yielding, start of softening, start of plateu, ultimate disp. and # yielding, start of softening, start of plateu, base shears
    else:
        input1 = cd+'/inputs/idealised_curve.csv' # idealised Base shear [kN] vs top displacement [m]
        input2 = cd+'/inputs/displacement_profile.csv' # displacement profile at each the Limit state
        input3 = cd+'/inputs/building_parameters.csv' # First period of vibration and partecipation factor normalised with respect to top floor
        
        with open(input1, 'rb') as f:
            reader = csv.reader(f)
            newlist = [row for row in reader]
        SPO = []
        if an_type == 0:
            dy = [float(ele[1]) for ele in newlist[1:]]
            du = [float(ele[2]) for ele in newlist[1:]]
            Fy = [float(ele[3]) for ele in newlist[1:]]
            noBlg = len(dy)
            for blg in range(0,noBlg):
                SPO.append([dy[blg], du[blg], Fy[blg]])
            if flag:
                # Plot idealised curve
                for i in range(0,noBlg):
                    x = np.array([0, dy[i],du[i]])
                    y = np.array([0, Fy[i], Fy[i]])
                    plt.plot(x,y,color='b',marker = 'o',label='bilinear input '+str(i),linewidth=linew)
                
                plt.xlabel('roof displacement, droof '+units[0],fontsize=fontsize)
                plt.ylabel('base shear, Vb '+units[1],fontsize=fontsize)
                plt.suptitle('Pushover curve',fontsize=fontsize)
                plt.legend(loc='lower right',frameon = False)
                plt.show()
        else:
            dy = [float(ele[1]) for ele in newlist[1:]]
            ds = [float(ele[2]) for ele in newlist[1:]]
            dmin = [float(ele[3]) for ele in newlist[1:]]
            du = [float(ele[4]) for ele in newlist[1:]]
            Fy = [float(ele[5]) for ele in newlist[1:]]
            Fmin = [float(ele[6]) for ele in newlist[1:]]
            noBlg = len(dy)
            for blg in range(0,noBlg):
                SPO.append([dy[blg], ds[blg], dmin[blg], du[blg], Fy[blg], Fmin[blg]])
            if flag:
                for i in range(0,noBlg):
                    x = np.array([0, dy[i], ds[i], dmin[i], du[i]])
                    y = np.array([0, Fy[i], Fy[i], Fmin[i], Fmin[i]])
                    plt.plot(x,y,color='b',marker = 'o', label='quadrilinear input '+str(i),linewidth = linew)
                
                plt.xlabel('roof displacment, droof '+units[0],fontsize=fontsize)
                plt.ylabel('base shear, Vb '+units[1],fontsize=fontsize)
                plt.suptitle('Pushover curve',fontsize=fontsize)
                plt.legend(loc='lower right',frameon = False)
                plt.show()
        
        with open(input2, 'rb') as f:
            reader = csv.reader(f)
            newlist = [row for row in reader]
        disp_profile = []  
        for i in range(1,len(newlist)):
            disp_profile.append([float(ele) for ele in newlist[i][1:]])
        noStorey = len(disp_profile)
        dcroof = disp_profile[::2] # roof displacement at each Limit state
        bUthd = disp_profile[1::2]
            
        with open(input3, 'rb') as f:
            reader = csv.reader(f)
            newlist = [row for row in reader]
        T = [float(ele[1]) for ele in newlist[1:]] # First period
        Gamma = [float(ele[2]) for ele in newlist[1:]] # First modal participation factor normalised with respect to the top displ.
        w = [float(ele[3]) for ele in newlist[1:]]# weight assigned to each building if multiple buildings are input
    
    # Obtain ratios between spectral acceleration at average period and spectral accelerations 
    # at the period of each building, in order to produce fragility and vulnerability with a common IM
    # and to be able to combine them
    Tav = np.average(np.array(T),weights = w) # average period
    Sa_ratios = get_spectral_ratios(Tav,T) # ratios
    return [T, Gamma, w, dcroof, SPO, bUthd, noBlg, Tav, Sa_ratios]