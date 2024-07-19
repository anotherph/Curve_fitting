import numpy as np
import matplotlib.pyplot as plt
# from scipy.interpolate import CubicSpline
import scipy.interpolate as spi
import csv
import argparse

def loadData(str_dir):
    Data=np.empty((0,3))
    f=open(str_dir)
    rdr=csv.reader(f)
    for i,line in enumerate(rdr):
        if i==0:
            continue
        else: 
            temp=np.array(line);temp=np.reshape(temp,(1,3))
            Data=np.append(Data,temp,axis=0)
    len_series=i
    f.close()

def getData(self): # set the length of series
    tp=np.arange(self.st,self.st+self.num_len)
    al=self.Data[tp,0] # '0' means column 1: altitude
    al=al.astype(np.float64)
    dist = np.linspace(0,10,len(al))
    return al, dist

def runMain(args):
    # get metadata
    dir = "info_national_park.csv"
    st=loadData(dir)
    # num_len = len(st)+1
    global y_ori, x_ori
    y_ori, x_ori = getData() # y means altitude, x means cumlitive distance (km)
    
    # select data
    ind=np.linspace(0,len(y_ori)-1,self.num); ind=ind.astype(np.int32)
    global y, x, x_n
    y=y_ori[ind]; x=x_ori[ind]
    x_n=np.linspace(0,x_ori[-1],len(y_ori)*5)
    
    # spline interpolation
    global ipo, iy
    ipo = spi.splrep(x,y,k=3) # make cubic spline (k=3)
    iy=spi.splev(x_n,ipo,der=0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument('--sheetName', type=str, required=True, help='Your name')
    args = parser.parse_args()
    runMain(args)