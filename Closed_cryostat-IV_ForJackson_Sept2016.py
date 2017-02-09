# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 16:05:07 2015
Edited on Tue Sept 27 19:42

@author: feliciaullstad


Python script intended be automated and to take a collection of raw datafiles with R vs T data
from the cryostat and concatenate to produce one R vs T datafile and several IV-files
as well as graphs and store this in a new folder.
"""

import matplotlib.pyplot as plt
import pandas as pd
import os
import string




plt.close("all")    #Closes plots from previous run

#######################################################
#ONLY CHANGE THESE THINGS!

filebase='JM017-20_09_2016_'    #Base name of files that need to be read. Copy txt file name and remove everything after final underscore.
file_location='/Users/Felicia/Desktop/Google_Drive/PhD/SmN data/Cryostat/JM017' #This must be the folder you have your files in
Sample_name='JM017' #For naming created textfiles and plots

Cryostat_program='RvsT' #Import from details file
IV_temperature_scans=[300,100,60,40,20,10,8,4] #Write in the temperatures you did IV-scans at
row_nr=5    #number of rows in a IV-scan text-file
tempdiff=1  #largest temperature difference allowed between your set temp and the measured temp in th first point for each IV data file



"""DO NOT CHANGE BELOW THIS LINE"""
######################################################
if not os.path.exists(file_location+'-python'):     #Checks if the python folder exists
    os.makedirs(file_location+'-python')            #If not, it makes it
######################################################
#Plot settings RvsT
labels=['Temperature A', 'Temperature', 'Positive voltage', 'Negative voltage', 'Positive current', 'Negative current', 'V limit reached?', 'Desired current', 'Resistance']
units=['K', 'K','V', 'V', 'A', 'A', ' ', '$\Omega$']
plotx='Temperature'   #Change this to plot other data on the x-axis
ploty='Resistance'      #Change this to plot other data on the y-axis
titletext=ploty+' vs. '+plotx+' for sample '+Sample_name
#Plot settings IV plot
IVplotx1='Positive voltage'
IVploty1='Positive current'
IVplotx2='Negative voltage'
IVploty2='Negative current'
IVunitx='V'
IVunity='A'
IVtitletext='Current vs. voltage for sample '+Sample_name+' at '
######################################################

def stripfile(filename):
    """
    Strips the file name to just the file number so that it can be handled easier
    """
    filename=filename.replace(filebase,'')
    filename=filename.replace('.txt','')
    if '~' in filename:
        filename=filename.replace('~','')
    filename=int(filename)
    return filename
######################################################

def fullname(filenumber):
    """
    Expands the file number to the full file name so it can be found in the folder
    """
    if filenumber<10:
        fullname=filebase+' '+str(filenumber)+'.txt'
    else:
        fullname=filebase+str(filenumber)+'.txt'
    return fullname
######################################################

def all_file_numbers(file_location,IV_temperature_scans):
    """
    This function finds all the file numbers and checks if they are part
    of an IV scan or RvsT and bins them accordingly. It sorts them first based on
    number of rows in the file and if the number of rows is right for an IV file
    it checks what temperature of the ones given in the preamble is close enough
    and saves that file number in a dictionary with the temperature as a key.
    """
    all_filenumbers={}

    for filename in os.listdir(file_location):
        print('Currently checking: '+filename)
        if 'details' in filename:   #To skip the details file that doesn't match the rest
            pass
        elif 'DS_Store' in filename:    #To skip the DS_store file on mac's
            pass
        else:   #open each file in the folder and check how many rows are in it. Bin it accordingly.
            try:
                testingfiles=pd.read_csv(file_location+'/'+filename,delimiter='\t', header=None,skiprows=0)
                #print testingfiles
            except:
                raise Exception(filename+' does not conform to standard. Check through textfile.')
            if len(testingfiles)==row_nr:   #If right number of rows for IV file, check temperature
                #check temperature
                #print(testingfiles[0][1])  #First temperature data in file
                for temperature in IV_temperature_scans:
                    if abs(float(testingfiles[0][1])-temperature)<tempdiff: #If true add to correct temperature file list
                        filename=stripfile(filename)
                        all_filenumbers.setdefault(('file_list_'+str(temperature)+'K'),[]).append(filename)
            elif len(testingfiles)>row_nr:  #If txt file is longer than IV scan then it is RvsT
                filename=stripfile(filename)
                all_filenumbers.setdefault(('file_list_RvsT'),[]).append(filename)
            else:
                print(filename+' is empty/not conforming to standard')
    all_filenumbers['file_list_RvsT']=sorted(all_filenumbers['file_list_RvsT']) #Sort the RvsT file by number
    for temperature in IV_temperature_scans:    #Sort the files in the respective temp bin after file number
        try:
            all_filenumbers['file_list_'+str(temperature)+'K']=sorted(all_filenumbers['file_list_'+str(temperature)+'K'])
        except:
            raise Exception('One of the input IV scan temperatures does not have any data associated with it.')
    return all_filenumbers
#####################################################

def all_data(all_filenumbers):
    """
    This function checks through the all the lists of IV-temperatures and RvsT data
    and concatenates all the data from the respective list to it's own file. It then
    returns a dictionary where the keys are the IV temperatures or RvsT.
    """
    all_data={}
    print('')
    print('Currently reading through all your data.')
    print('Please wait for confirmation. 1 minute expected.')
    for key in all_filenumbers:
        #print(key)
        readfile_list=[]
        for item in all_filenumbers[key]:
            #print item
            wholename=fullname(int(item))
            try:
                readfile=pd.read_csv(file_location+'/'+wholename, header=None, delim_whitespace=True, skiprows=1)
                readfile_list.append(readfile)
                all_data[key]=pd.concat(readfile_list)
            except:
                raise Exception('Could not read file '+wholename+'. Check though textfile.')
        #print key
        #print all_data[key]
        all_data[key].columns=labels
    return all_data
####################################################

#Plot the RvsT (or other) data
def plot_RvsT_graph(all_data,plotx,ploty,titletext,units,unitx,unity,file_location,Sample_name,file_list):
    plot=plt.plot(all_data[file_list][plotx],all_data[file_list][ploty],'.')
    plt.xlabel(plotx+' ('+units[unitx]+')')
    plt.ylabel(ploty+' ('+units[unity]+')')
    plt.title(titletext)
    #plt.ylim(4e5,3e6)
    #plt.xlim(0,140)
    type_plot=file_list.replace('file_list','')
    plot=plt.savefig(file_location+'-python/'+Sample_name+type_plot+'_plot.pdf', format='pdf', dpi=1200)
    plt.close()
    return plot

def plot_IV_graph(all_data,IVplotx1,IVploty1,IVplotx2,IVploty2,IVtitletext,unitx,unity,file_location,Sample_name,temperature):
    plot=plt.plot(all_data['file_list_'+str(temperature)+'K'][IVplotx1],all_data['file_list_'+str(temperature)+'K'][IVploty1],'bo')
    plot=plt.plot(all_data['file_list_'+str(temperature)+'K'][IVplotx2],all_data['file_list_'+str(temperature)+'K'][IVploty2],'bo')
    #plt.yscale('symlog')
    #plt.xscale('symlog')
    plt.xlabel('Voltage ('+IVunitx+')')
    plt.ylabel('Current ('+IVunity+')')
    plt.title(IVtitletext+str(temperature)+'K')
    plot=plt.savefig(file_location+'-python/'+Sample_name+'_IV_'+str(temperature)+'K_plot.pdf', format='pdf', dpi=1200)
    plt.close()
    return plot
###################################################

def save_all_data(all_data,key,file_location,Sample_name,labels):
    data_type=key.strip('file_list_')
    myfile=file_location+'-python/'+Sample_name+'_'+data_type+'_data.txt'
    open(myfile,'w')
    data=all_data[key]
    data.to_csv(myfile, header=labels, index=None, sep=' ', mode='w')
###################################################
"""Here is the order in which things are executed"""
IV_temperature_list=(''.join(str(IV_temperature_scans))).replace('[','').replace(']','')    #Makes a string out of the IV-temp list from preamble

all_filenumbers=all_file_numbers(file_location,IV_temperature_scans) #Gets file numbers
all_data=all_data(all_filenumbers)  #Gets data
plot_RvsT_graph(all_data,plotx,ploty,titletext,units,1,7,file_location,Sample_name,'file_list_RvsT')    #Plots and saves RvsT graph
for temperature in IV_temperature_scans:    #Plots and saves IV-curves graphs
    plot_IV_graph(all_data,IVplotx1,IVploty1,IVplotx2,IVploty2,IVtitletext,IVunitx,IVunity,file_location,Sample_name,temperature)

#Save all the data into separate text files in the same folder as the graphs.
for key in all_data:
    save_all_data(all_data,key,file_location,Sample_name,labels)

print('New datafiles created, graphs plotted. Done.')
