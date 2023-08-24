import gspread
from oauth2client.service_account import ServiceAccountCredentials
import scipy.interpolate as spi
from scipy.optimize import curve_fit
from matplotlib import pyplot as plt
import numpy as np
from random import sample
from haversine import haversine

def create_plot(x,y, styles, marker_s,labels, title):
    plt.figure(figsize=(10,6))
    for i in range(len(x)):
        plt.plot(x[i],y[i],styles[i],markersize=marker_s[i],label=labels[i])
    plt.xlabel('cumulitive distance (km)')
    plt.ylabel('altitude (m)')
    plt.title(title)
    plt.legend(loc=0)
    
def getData():
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
    
    Neajang=np.arange(1775,1882) # 1775th to 1882th rows contains the metadata of Neajang National park 
    # Neajang=np.arange(1775,1775+50)
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

if __name__ == "__main__":
    
    # get metadata 
    y_ori, x_ori = getData() # y means altitude, x means cumlitive distance (km)
    
    # choose altidue randomly
    choice=0 # 1 means that we only use a portion of the data, 0 means that we use all data
    num=8 # the number of samples
    if choice == 1:
        ind=sample(range(0,len(y_ori)),num);ind.sort()
    else:
        ind=range(0,len(y_ori)) 
    y=y_ori[ind]; x=x_ori[ind]
    
    # spline interpolation
    ipo = spi.splrep(x,y,k=1) # make cubic spline (k=3)
    iy = spi.splev(x_ori,ipo)
    
    # curve fitting
    # quadratic polynomial (order 2)
    def func(x,a,b,c):
        return a*x**2+b*x+c 
    popt, pcov =curve_fit(func,x,y)

    # # evaluate(True or False)
    # print(np.allclose(y,iy))

    # plot the graph
    create_plot([x_ori,x_ori,x],[y_ori,iy,y],['bo','r-','y*'],
                [3,3,10],['value','interpolation','selected'],'spline interpolation')
    create_plot([x_ori,x_ori,x],[y_ori,func(x_ori,*popt),y],['bo','r-','y*'],
                [3,3,10],['value','curve_fitting','selected'],'curve_fitting (2nd order of poly)')
    plt.show()
    