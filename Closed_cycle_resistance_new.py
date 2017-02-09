# -*- coding: utf-8 -*-
"""
Created on Fri Jul 22 2016

@author: feliciaullstad


Python script intended be automated and to take a collection of raw datafiles with R vs T data
from the cryostat and concatenate to produce one R vs T datafile
as well as a graph and store this in a new folder.
"""

import matplotlib.pyplot as plt
import pandas as pd
import os
import string




plt.close("all")    #Closes plots from previous run

#######################################################
#Settings for this data
filebase='F10-rerun-2-12_04_2016_'    #Base name of files that need to be read. Copy txt file name and remove everything after final underscore.
file_location='/home/feliciaullstad/Desktop/Google_Drive/PhD/SmN data/Cryostat/F10-rerun-2' # must be a folder

#Must be strings
Sample_name='F10'
Cryostat_program='RvsT' #Just for adding RvsT to filenames and graph titles etc

#Do not change below here!
######################################################
if not os.path.exists(file_location+'-python'):     #Checks if the python folder exists
    os.makedirs(file_location+'-python')            #If not, it makes it
######################################################
#Plot settings RvsT
labels=['Temperature A', 'Temperature', 'Positive voltage', 'Negative voltage', 'Positive current', 'Negative current', 'V limit reached?', 'Desired current', 'Resistance']
units=['K', 'K','V', 'V', 'A', 'A', 'int','A', '$\Omega$']
plotx='Temperature B'   #Change this to plot other data on the x-axis
ploty='Resistance'      #Change this to plot other data on the y-axis
unitx=1 #Chooses element from labels vector for plotting purposes.
unity=8
titletext=labels[unity]+' vs. '+labels[unitx]+' for sample '+Sample_name
######################################################
#Find out which file numbers we want to use for RvsT plot and save them in RvsT_files_list_final
RvsT_files_list=[]
for file in os.listdir(file_location):
    if file.endswith(".txt"):
        if 'details' not in file:
            RvsT_files_list.append(file)
print(RvsT_files_list)
RvsT_files_list_final=[]
for filename in RvsT_files_list:
    testingfiles=pd.read_csv(file_location+'/'+filename, header=0, delim_whitespace=True,skiprows=0)
    if len(testingfiles)>3:
        RvsT_files_list_final.append(filename)
print(RvsT_files_list_final)

def all_data(RvsT_files_list_final):
    dataframe=pd.DataFrame()
    for item in RvsT_files_list_final:
        readfile=pd.read_csv(file_location+'/'+item, header=None, delim_whitespace=True, skiprows=2)
        dataframe=dataframe.append([readfile])
    return dataframe


####################################################
#Plot the RvsT (or other) data
def plot_RvsT_graph(readfile_list,plotx,ploty,titletext,units,unitx,unity,file_location,Sample_name):
    plot=plt.plot(readfile_list[1],readfile_list[8],'.')
    plt.xlabel(plotx+' ('+units[unitx]+')')
    plt.ylabel(ploty+' ('+units[unity]+')')
    plt.title(titletext)
    #plt.ylim(4e5,3e6)
    #plt.xlim(0,140)
    plot=plt.savefig(file_location+'-python/'+Sample_name+'_'+Cryostat_program+'_plot.pdf', format='pdf', dpi=1200)
    plt.close()
    return plot

###################################################
def save_all_data(dataframe,file_location,Sample_name,labels):
    myfile=file_location+'-python/'+Sample_name+'_'+Cryostat_program+'_data.txt'
    open(myfile,'w')
    dataframe.to_csv(myfile, header=labels, index=None, sep=' ', mode='w')
###################################################
final_data=all_data(RvsT_files_list_final)
print final_data
plot_RvsT_graph(final_data,plotx,ploty,titletext,units,unitx,unity,file_location,Sample_name)
save_all_data(final_data,file_location,Sample_name,labels)
print 'New datafiles created, graphs plotted.'
