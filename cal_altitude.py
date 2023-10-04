# refer to blow about using PyQt5
# https://studyingrabbit.tistory.com/19
# https://stella47.tistory.com/428
# https://newbie-developer.tistory.com/149

import sys
import numpy as np
from PyQt5.QtWidgets import *

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import scipy.interpolate as spi
from scipy.optimize import curve_fit
from matplotlib import pyplot as plt
from random import sample
from haversine import haversine
import argparse

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self):
        fig = Figure()
        self.axes1 = fig.add_subplot(211)
        self.axes2 = fig.add_subplot(212)
        # fig.subplots_adjust(left=0.125, bottom=0.1, right=0.9, top=0.9, wspace=0.1, hspace=0.35)
        fig.subplots_adjust(left=0.1, bottom=0.05, right=0.95, top=0.95, wspace=0.05, hspace=0.25)
        fig.set_size_inches(10,20)
        super(MplCanvas, self).__init__(fig)

class Main(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui() # set UI
        self.setWindowTitle("주행고도")
        self.setGeometry(500,100,1000,1200)
        # self.setFixedSize(1000,1200)
        
    ############ UI setting ############    

    def init_ui(self):
        self.sc = MplCanvas()
        toolbar = NavigationToolbar(self.sc, self)
        
        pushbutton = QPushButton("create the graph!")
        pushbutton.clicked.connect(self.button_clicked)
        
        combobox_ex1 = QLabel("start point of series (length of series: 100)")
        combobox_ex2 = QLabel("end point of series")
        combobox_ex3 = QLabel("number of data-points in series")
        combobox_ex4 = QLabel("offset (m), press enter-key or button below to run program")
        combobox_ = QLabel("")
        
        textedit1 = QLineEdit(self)
        textedit1.textChanged.connect(self.set_graph1)
        
        textedit2 = QLineEdit(self)
        textedit2.textChanged.connect(self.set_graph2)
        
        textedit3 = QLineEdit(self)
        textedit3.textChanged.connect(self.set_graph3)
        
        textedit4 = QLineEdit(self)
        textedit4.textChanged.connect(self.set_graph4)
        textedit4.returnPressed.connect(self.button_clicked)

        layout = QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self.sc)
        
        layout.addWidget(combobox_ex1)
        layout.addWidget(textedit1)
        layout.addWidget(combobox_ex2)
        layout.addWidget(textedit2)
        layout.addWidget(combobox_ex3)
        layout.addWidget(textedit3)
        layout.addWidget(combobox_ex4)
        layout.addWidget(textedit4)
        layout.addWidget(combobox_)
        layout.addWidget(pushbutton)
        
        self.setLayout(layout)
        self.show()
        
    def button_clicked(self):
        self.runMain()

    def set_graph1(self, item):
        self.st = int(item)
        
    def set_graph2(self, item):
        self.en = int(item)
        
    def set_graph3(self, item):
        self.num = int(item)   
    
    def set_graph4(self, item):
        self.offset = int(item)   

    def create_plot(self):
        self.sc.axes1.cla()
        self.sc.axes2.cla()
        x1=[self.x_ori,self.x_n,self.x_n,self.x]
        y1=[self.y_ori,self.iy,self.iy+self.offset,self.y]
        x2=[self.x_ori,self.x_n,self.x_n,self.x]
        y2=[self.y_ori,self.iy_cf,self.iy_cf+self.offset,self.y]
        styles=['bo','r-.','r-','y*']
        marker_s=[3,3,5,10]
        labels1=['data','fit','fit+offset','selected']
        labels2=['data','fit','fit+offset','selected']
        for i in range(len(x1)):
            self.sc.axes1.plot(x1[i],y1[i],styles[i],markersize=marker_s[i],label=labels1[i])
            self.sc.axes2.plot(x2[i],y2[i],styles[i],markersize=marker_s[i],label=labels2[i])
        self.sc.axes1.set_xlabel('cumulitive distance (km)')
        self.sc.axes1.set_ylabel('altitude (m)')
        self.sc.axes1.set_title('spline interpolation')
        self.sc.axes1.legend()
        self.sc.axes1.grid()
        self.sc.axes2.set_xlabel('cumulitive distance (km)')
        self.sc.axes2.set_ylabel('altitude (m)')
        self.sc.axes2.set_title('curve_fitting (2nd order of polynomial)')
        self.sc.axes2.legend()
        self.sc.axes2.grid()  
        self.sc.draw()
    
    def getData(self):
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
        Neajang=np.arange(1775+self.st,1775+self.st+self.num_len)
        al=data[Neajang,11] # '11' means column L
        al=al.astype(np.float64)
        
        dist = np.linspace(0,10,len(al))
        # # calculate the distance 
        # lo=data[Neajang,12]; lo=lo.astype(np.float64)# '12' means column M, longtitude
        # la=data[Neajang,13]; la=la.astype(np.float64)# '13' means column N, latitude
        # lalo =[la, lo]; lalo=np.array(lalo)
        # dist=[0] # initial cumlitive distance is 0
        # for i in range(len(Neajang)-1):
        #     dist.append(haversine(lalo[:,i],lalo[:,i+1], unit='km'))
        # dist=np.array(dist)
        # dist=np.cumsum(dist)
        return al, dist

    def runMain(self):
        # get metadata
        st=self.st
        self.num_len = self.en-self.st+1
        y_ori, x_ori = self.getData() # y means altitude, x means cumlitive distance (km)
        
        # select data
        ind=np.linspace(0,len(y_ori)-1,self.num); ind=ind.astype(np.int32)
        y=y_ori[ind]; x=x_ori[ind]
        x_n=np.linspace(0,x_ori[-1],len(y_ori)*5)
        
        # spline interpolation
        ipo = spi.splrep(x,y,k=3) # make cubic spline (k=3)
        iy=spi.splev(x_n,ipo,der=0)
        
        # curve fitting
        # quadratic polynomial (order 2)
        def func(x,a,b,c):
            return a*x**2+b*x+c 
        popt, pcov =curve_fit(func,x,y)
        iy_cf=func(x_n,*popt)
        
        self.x_ori=x_ori;self.y_ori=y_ori
        self.x_n=x_n
        self.x=x;self.y=y
        self.iy=iy;self.iy_cf=iy_cf
        
        self.create_plot()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = Main()
    sys.exit(app.exec_())