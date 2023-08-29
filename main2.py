## apply spline interpolation to every 4 frame data

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import scipy.interpolate as spi
from scipy.optimize import curve_fit
from matplotlib import pyplot as plt
import numpy as np
from random import sample
from haversine import haversine
import argparse

def create_plot(x,y, styles, marker_s,labels, title):
    plt.figure(figsize=(10,6))
    for i in range(len(x)):
        plt.plot(x[i],y[i],styles[i],markersize=marker_s[i],label=labels[i])
    plt.xlabel('cumulitive distance (km)')
    plt.ylabel('altitude (m)')
    plt.title(title)
    plt.legend(loc=0)
    
def getData(num_len):
    # read from google spreadsheets
    # return altitude and cumultive distance calculated from the latitude and londitude
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    json = './main-analog-396807-a46944180f2f.json' # use your token of google project API
    credentials = ServiceAccountCredentials.from_json_keyfile_name(json, scope)
    gc = gspread.authorize(credentials)
    sheet_url = 'https://docs.google.com/spreadsheets/d/1Iqe0q47iLu8NBKJCrabAixPVY1tq-uFkQIXWEVTqtV0/edit?pli=1#gid=0'
    doc = gc.open_by_url(sheet_url)
    worksheet = doc.worksheet('sheet1')
    data=worksheet.get_all_values()
    data=np.array(data)
    
    # Neajang=np.arange(1775,1882) # 1775th to 1882th rows contains the metadata of Neajang National park 
    Neajang=np.arange(1775,1775+num_len)
    al=data[Neajang,11] # '11' means column L
    al=al.astype(np.float64)
    
    # calculate the distance 
    lo=data[Neajang,12]; lo=lo.astype(np.float64)# '12' means column M, longtitude
    la=data[Neajang,13]; la=la.astype(np.float64)# '13' means column N, latitude
    lalo =[la, lo]; lalo=np.array(lalo)
    dist=[0] # initial cumlitive distance is 0
    for i in range(len(Neajang)-1):
        dist.append(haversine(lalo[:,i],lalo[:,i+1], unit='km'))
    dist=np.array(dist)
    dist=np.cumsum(dist)
    return al, dist

def runMain(args):
    # get metadata
    num_len = args.num_len
    y_ori, x_ori = getData(num_len) # y means altitude, x means cumlitive distance (km)
    
    # select data
    ind=range(0,len(y_ori)-1) 
    y=y_ori[ind]; x=x_ori[ind]
    
    ### make interpolation using sliding window ###
    # spline interpolation
    num=int(len(y_ori)/args.intav) # the number of samples
    x_t=[]; y_t=[]; x_s=[]; y_s=[]
    ind_t=np.linspace(0,len(y_ori)-2,num); ind_t=ind_t.astype(np.int32)
    for ix in range(num):
        temp=ind_t[ix:ix+4]
        if len(temp)<4:
            break
        print(temp)
        ipo = spi.splrep(x[temp],y[temp],k=3) # make cubic spline (k=3)
        x_n=np.linspace(x[temp[0]],x[temp[-1]],num*5)
        iy=spi.splev(x_n,ipo)
 
        # if ix == 4:
        #     break
        
        if ix==1:
            x_t=np.append(x_t,x_n)
            y_t=np.append(y_t,iy)
            x_s=np.append(x_s,x[temp])
            y_s=np.append(y_s,y[temp])
        else:
            x_tm=max(x_t)
            x_t=np.append(x_t,x_n[x_n>x_tm])
            y_t=np.append(y_t,iy[x_n>x_tm])
            x_s=np.append(x_s,x[temp[-1]]) # we use 4 frame and move 1 frame, thus the last one is added 
            y_s=np.append(y_s,y[temp[-1]])
        
    # plot the graph
    create_plot([x_ori,x_t,x_s],[y_ori,y_t,y_s],['bo','r-','y*'],
                [3,3,10],['value','interpolation','selected'],'spline interpolation')
    plt.show()
    
    ### make interpolation every 4 frame ### 
    # spline interpolation
    num=int(len(y_ori)/args.intav) # the number of samples
    x_t=[]; y_t=[]; x_s=[]; y_s=[]
    ind_t=np.linspace(0,len(y_ori)-2,num); ind_t=ind_t.astype(np.int32)
    for ix in range(num):
        temp=ind_t[4*ix:4*ix+4]
        if len(temp)<4:
            break
        print(temp)
        ipo = spi.splrep(x[temp],y[temp],k=3) # make cubic spline (k=3)
        x_n=np.linspace(x[temp[0]],x[temp[-1]],num*5)
        iy=spi.splev(x_n,ipo)
        x_t=np.append(x_t,x_n)
        y_t=np.append(y_t,iy)
        x_s=np.append(x_s,x[temp])
        y_s=np.append(y_s,y[temp])
        
    # plot the graph
    create_plot([x_ori,x_t,x_s],[y_ori,y_t,y_s],['bo','r-','y*'],
                [3,3,10],['value','interpolation','selected'],'spline interpolation')
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--num_len', type=int, default=100, help='the length of data')
    parser.add_argument('--intav', type=int, default=2, help='the intervals of dataset') # 
    args=parser.parse_args()
    runMain(args)
    
    
    