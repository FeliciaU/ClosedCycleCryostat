# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 16:05:07 2015

@author: feliciaullstad


Python script intended be automated and to take a collection of raw datafiles with R vs T data
from the cryostat and concatenate to produce one R vs T datafile and IV-files
as well as a good graph and an info file and store this in a new folder.
"""

import matplotlib.pyplot as plt
import pandas as pd
import os
import string




plt.close("all")    #Closes plots from previous run

#######################################################
#Settings for this data
filebase='F24-30_09_2016_'    #Base name of files that need to be read. Copy txt file name and remove everything after final underscore.
file_location='/home/feliciaullstad/Desktop/Google_Drive/PhD/SmN data/Cryostat/F24'

#Must be strings
Sample_name='F24'

Cryostat_program='RvsT' #Import from details file
IV_temperature_scans=[] #Write in the temperatures you used to do IV-scans
IV_temperature_list=(''.join(str(IV_temperature_scans))).replace('[','').replace(']','')    #string

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
IVtitletext='Voltage vs. current for sample '+Sample_name+' at '
######################################################
#Find out which file numbers we want to use for RvsT plot
#and which ones we want for IV plots

#Find all files in file location
#Open them all with skiprow 0 to avoid getting wrong column count
    #if the have one line do nothing
    #if they have 3 lines - check temperature - bin that file number to IV scan at that temperature
    #if they have more than 3 lines - bin that file number to R vs T


def stripfile(filename):    #Strips the file name to just the file number
    filename=string.replace(filename,filebase,'')
    filename=string.replace(filename,'.txt','')
    if '~' in filename:
        filename=string.replace(filename,'~','')
    filename=int(filename)
    return filename

def fullname(filenumber):   #Expands the file number to a full file name
    if filenumber<10:
        fullname=filebase+' '+str(filenumber)+'.txt'
    else:
        fullname=filebase+str(filenumber)+'.txt'
    return fullname

#Create dictinary with keys of file_list_290K etc and the lists as arguments
def all_file_numbers(file_location,IV_temperature_scans):   #Finds all the file numbers and checks if they are part of IV scan or RvsT and bins them accordingly
    all_filenumbers={}

    for filename in os.listdir(file_location):
        print filename
        if 'details' not in filename:   #To skip the details file that doesn't match the rest
            testingfiles=pd.read_csv(file_location+'/'+filename, header=None, delim_whitespace=True,skiprows=0)
            #print testingfiles
            if len(testingfiles)==6:
                #check temperature
                #print testingfiles[0][1]  #temperature data in file
                #for temperature in IV_temperature_scans:
                   # all_files['file_list_'+str(temperature)+'K']=[]
                for temperature in IV_temperature_scans:
                    if abs(float(testingfiles[0][1])-temperature)<1:
                        filename=stripfile(filename)
                        all_filenumbers.setdefault(('file_list_'+str(temperature)+'K'),[]).append(filename)
                    #sorted(all_files.items(), key='file_list_'+str(temperature)+'K')
            elif len(testingfiles)>6:
                filename=stripfile(filename)
                all_filenumbers.setdefault(('file_list_RvsT'),[]).append(filename)
    all_filenumbers['file_list_RvsT']=sorted(all_filenumbers['file_list_RvsT'])
    for temperature in IV_temperature_scans:
        try:
            all_filenumbers['file_list_'+str(temperature)+'K']=sorted(all_filenumbers['file_list_'+str(temperature)+'K'])
        except:
            raise Exception('One of the input IV scan temperatures does not have any data associated with it.')
    return all_filenumbers
#####################################################
#Making a list of the used RvsT file names
def all_data(all_filenumbers):
    all_data={}
    for key in all_filenumbers:
        readfile_list=[]
        for item in all_filenumbers[key]:
            #print item
            wholename=fullname(int(item))
            readfile=pd.read_csv(file_location+'/'+wholename, header=None, delim_whitespace=True, skiprows=1)
            readfile_list.append(readfile)
        all_data[key]=pd.concat(readfile_list)
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
    plt.xlabel('Voltage ('+IVunitx+')')
    plt.ylabel('Current ('+IVunity+')')
    plt.title(IVtitletext+str(temperature)+'K')
    plot=plt.savefig(file_location+'-python/'+Sample_name+'_IV_'+str(temperature)+'K_plot.pdf', format='pdf', dpi=1200)
    plt.close()
    return plot
###################################################

#Make new folder
#Save the info and graph in one pdf
#Save the graph only as pdf
#Save the created data frames to textfiles


def save_all_data(all_data,key,file_location,Sample_name,labels):
    data_type=key.strip('file_list_')
    myfile=file_location+'-python/'+'/'+Sample_name+'_'+data_type+'_data.txt'
    open(myfile,'w')
    data=all_data[key]
    data.to_csv(myfile, header=labels, index=None, sep=' ', mode='w')



all_filenumbers=all_file_numbers(file_location,IV_temperature_scans)
all_data=all_data(all_filenumbers)
plot_RvsT_graph(all_data,plotx,ploty,titletext,units,1,7,file_location,Sample_name,'file_list_RvsT')
for temperature in IV_temperature_scans:
    plot_IV_graph(all_data,IVplotx1,IVploty1,IVplotx2,IVploty2,IVtitletext,IVunitx,IVunity,file_location,Sample_name,temperature)

#print_info_sheet_cryofolder(file_location,Sample_name,Cryostat_run_date,Cryostat_program,IV_temperature_list,IV_temperature_scans)

#Save all the data into text files in the same folder as the graphs.
for key in all_data:
    save_all_data(all_data,key,file_location,Sample_name,labels)

print 'New datafiles created, graphs plotted.'
