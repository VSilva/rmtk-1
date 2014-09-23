# -*- coding: utf-8 -*-
"""
Created on Thu Jun  5 16:03:26 2014

@author: chiaracasotto
"""
import csv
import os
import matplotlib.pyplot as plt
import scipy.stats as stat
import numpy as np
from common.conversions import from_median_to_mean

def export(vuln, plot_feature, x, y):
    plotflag, linew, fontsize, units, iml = plot_feature[0:5]
    cd = os.getcwd()
    if vuln == 0:
        if plotflag[0][2]:
            plot_fragility(iml,np.exp(x),y,linew,fontsize,units)   
        # Export fragility parameters (mu and cov of Sa) to csv
        # from log-mean to mean and from dispersion to cofficient of variation
        [meanSa, stSa] = from_median_to_mean(np.exp(x),y)
        cov = np.divide(stSa,meanSa)
        output_path = cd+'/outputs/fragility_parameters.csv'
        header = ['DS', 'mean', 'coefficient of variation']
        n_lines = len(meanSa)
        DS = range(len(meanSa)+1)
        col_data = [DS[1:], meanSa, cov]
        print_outputs(output_path,header,n_lines,col_data)
        
    # Plot mean Vulnerability curve
    elif vuln == 0:      
        if plotflag[0][3]:       
            plt.plot(iml,x, marker='o', linestyle='None',label = 'LR')
            plt.xlabel('Spectral acceleration at T elastic, Sa(Tel) '+units[2],fontsize = fontsize)
            plt.ylabel('Loss Ratio',fontsize = fontsize)
            plt.suptitle('Vulnerability Curve',fontsize = fontsize)
            plt.legend(loc='lower right',frameon = False)
            plt.savefig(cd+'/outputs/vulnerability_curve.png')
            plt.show()
        # Export discrete vulnerability curve to csv
        output_path = cd+'/outputs/vulnerability_curve.csv'
        header = ['Intensity Measure Level','mean Loss Ratio','coefficient of variation Loss Ratio']
        n_lines = len(x)
        col_data = [iml, x, y/x] # mean and coefficient of variation of LR
        print_outputs(output_path,header,n_lines,col_data)
        
def print_outputs(output_file,header,n_lines,col_data):
    outfile = open(output_file, 'wt')
    writer = csv.writer(outfile, delimiter=',')
    writer.writerow(header)
    for j in range(0, n_lines):
        dat = [ele[j] for ele in col_data]
        writer.writerow(dat)
    outfile.close()

def plot_fragility(iml,Sa50,bTSa,linew,fontsize,units):
    # INPUT: Sa50 is the median of iml, while bTSa is the dispersion, that is to say the std(log(iml))
    colours = ['b','r','g','k','c','y']
    cd = os.getcwd()
    #texto = ['yielding','collapse','mod']
    for q in range(0,len(Sa50)):
        txt = 'Damage State '+str(q+1)
        y = stat.norm(np.log(Sa50[q]),bTSa[q]).cdf(np.log(iml))
        plt.plot(iml,y,color=colours[q],linewidth=linew,label = txt)
    
    plt.xlabel('Spectral acceleration at T elastic, Sa(Tel) '+units[2],fontsize = fontsize)
    plt.ylabel('Probabilty of Exceedance',fontsize = fontsize)
    plt.suptitle('Fragility Curves',fontsize = fontsize)
    plt.legend(loc='lower right',frameon = False)
    plt.savefig(cd+'/outputs/fragility_curves.png')
    plt.show()