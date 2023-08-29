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
    choice=args.ch 
    num=args.ch_num # the number of samples
    if choice == 1:
        ind=sample(range(1,len(y_ori)-2),num-2);ind.sort()
        ind.insert(0,0); ind.append(len(y_ori)-1)
    elif choice == 2:
        ind=np.linspace(0,len(y_ori)-1,num); ind=ind.astype(np.int32)
    else:
        ind=range(0,len(y_ori)-1) 
    y=y_ori[ind]; x=x_ori[ind]
    x_n=np.linspace(0,x_ori[-1],len(y_ori)*2)
    
    # spline interpolation
    ipo = spi.splrep(x,y,k=3) # make cubic spline (k=3)
    iy=spi.splev(x_n,ipo,der=0)
    
    # curve fitting
    # quadratic polynomial (order 2)
    def func(x,a,b,c):
        return a*x**2+b*x+c 
    popt, pcov =curve_fit(func,x,y)

    # plot the graph
    create_plot([x_ori,x_n,x],[y_ori,iy,y],['bo','r-','y*'],
                [3,3,10],['value','interpolation','selected'],'spline interpolation')
    create_plot([x_ori,x_ori,x],[y_ori,func(x_ori,*popt),y],['bo','r-','y*'],
                [3,3,10],['value','curve_fitting','selected'],'curve_fitting (2nd order of poly)')
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--num_len', type=int, default=100, help='the length of data')
    parser.add_argument('--ch', type=int, default=2, help='1:select ch_num values randomly, 2:select ch_num values evenly, 3: use full dataset' )
    parser.add_argument('--ch_num', type=int, default=50, help='# the number of selected samples randomly' )
    args=parser.parse_args()
    runMain(args)
    
    
    