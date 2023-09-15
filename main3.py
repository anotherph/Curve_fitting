## predict the forward altitude
## time series prediction(?) 

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import scipy.interpolate as spi
from scipy.optimize import curve_fit
from matplotlib import pyplot as plt
from drawnow import drawnow, figure
import numpy as np
from random import sample
from haversine import haversine
import argparse

def create_plot(x,y, styles, marker_s,labels, title):
    for i in range(len(x)):
        plt.plot(x[i],y[i],styles[i],markersize=marker_s[i],label=labels[i])
    plt.xlabel('cumulitive distance (km)')
    plt.ylabel('altitude (m)')
    plt.title(title)
    plt.legend(loc=0)
    plt.ylim(150,1000)
        
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
    # al=al/max(al)
    
    # calculate the distance 
    lo=data[Neajang,12]; lo=lo.astype(np.float64)# '12' means column M, longtitude
    la=data[Neajang,13]; la=la.astype(np.float64)# '13' means column N, latitude
    lalo =[la, lo]; lalo=np.array(lalo)
    dist=[0] # initial cumlitive distance is 0
    for i in range(len(Neajang)-1):
        dist.append(haversine(lalo[:,i],lalo[:,i+1], unit='km'))
    dist=np.array(dist)
    dist=np.cumsum(dist)
    dist=np.linspace(0,num_len-1,num_len) # evenly spaced number
    return al, dist


def runMain(args):
    # get metadata
    num_len = args.num_len
    num_p=args.num_p
    y_ori, x_ori = getData(num_len) # y means altitude, x means cumlitive distance (km)

    # select data
    ind=range(0,len(y_ori)-1) 
    y=y_ori[ind]; x=x_ori[ind]

    # quadratic polynomial (order 2)
    def func(x,a,b,c):
        return a*x**2+b*x+c 

    ### make interpolation using sliding window ###
    num=int(len(y_ori)/args.intav) # the number of samples
    x_t=[]; y_t=[]; x_s=[]; y_s=[]; y_p=[]; y_e=[]
    
    def run_plot(): # we need this def to use drawnow function
        if args.me == 0: 
            create_plot([x_ori,x_t,x_s],[y_ori,y_t,y_s],['bo','r-s','y*'],[3,5,10],['value','interpolation','selected'],'spline interpolation')
        elif args.me == 1:
            create_plot([x_ori,x_t,x_s],[y_ori,y_t,y_s],['bo','r-s','y*'],[3,5,10],['value','interpolation','selected'],'curve fitting')
          
    ind_t=np.linspace(0,len(y_ori)-2,num); ind_t=ind_t.astype(np.int32)
    
    fig = plt.figure(1)

    for ix in range(num):
        temp=ind_t[ix:ix+num_p] # index to be applied 
        temp_p=ind_t[ix:ix+(num_p+1)] # index to predict value
        if len(temp)<num_p: # the last one
            break
        
        if args.me == 0:        
            # spline-interpolation
            ipo = spi.splrep(x[temp],y[temp],k=3) # make cubic spline (k=3)
            x_n=x[temp_p]
            iy=spi.splev(x_n,ipo)
        elif args.me == 1:
            # curve-fitting
            popt, pcov =curve_fit(func,x[temp],y[temp])
            x_n=x[temp_p]
            iy=func(x_n,*popt)
        
        if args.sh == 0:
            # draw the trace
            if ix==0:
                x_t=np.append(x_t,x_n)
                y_t=np.append(y_t,iy)
                x_s=np.append(x_s,x[temp])
                y_s=np.append(y_s,y[temp])
                y_e=np.append(y_e,np.zeros(num_p))
            else:
                x_tm=max(x_t)
                x_t=np.append(x_t,x_n[x_n>x_tm])
                y_t=np.append(y_t,iy[x_n>x_tm])
                x_s=np.append(x_s,x[temp[-1]])
                y_s=np.append(y_s,y[temp[-1]])
                y_e=np.append(y_e,np.abs(y[temp[-1]]-y_t[-2])) # y[temp[-1]] - measurement , y_t[-2] - prediction
        else:
            # draw the instance
            x_t=x_n
            y_t=iy
            x_s=x[temp]
            y_s=y[temp]
            # y_e=np.append(y_e,np.zeros(8))  
            if ix==args.sh:
                break      
        # drawnow(run_plot)
    run_plot()
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--num_len', type=int, default=100, help='the number of total data')
    parser.add_argument('--intav', type=int, default=2, help='the intervals of dataset')
    parser.add_argument('--num_p', type=int, default=4, help='the number of data to predict next value')
    parser.add_argument('--me', type=int, default=1, help='interpolation method, 0:spline (cubic), 1:curve-fitting (2nd order poly)')
    parser.add_argument('--sh', type=int, default=0, help='show cumultive gragh (0), show nth instance (n)')
    args=parser.parse_args()
    runMain(args)
    
    
    