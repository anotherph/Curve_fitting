# refer to blow about using PyQt5
# https://studyingrabbit.tistory.com/19
# https://stella47.tistory.com/428
# https://newbie-developer.tistory.com/149

# load .csv file

import sys
import numpy as np
import csv
from PyQt5.QtWidgets import *

import matplotlib
matplotlib.use('Qt5Agg')
# matplotlib.use('tkAgg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

import gspread
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
        fig.subplots_adjust(left=0.1, bottom=0.05, right=0.95, top=0.95, wspace=0.05, hspace=0.25)
        fig.set_size_inches(10,20)
        super(MplCanvas, self).__init__(fig)
        
class second(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui() # set UI
        self.setWindowTitle("graph")
        self.setGeometry(500,100,1000,1300)
        
    def init_ui(self):
        self.sc = MplCanvas()
        toolbar = NavigationToolbar(self.sc, self)

        layout = QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self.sc)
        
        self.setLayout(layout)
        self.show()
        # self.setFixedSize(1000,1200)
        # do something!!
        
        self.sc.axes1.cla()
        self.sc.axes2.cla()
        x1=[x_ori,x_n,x_n,x]
        y1=[y_ori,iy,iy+offset,y]
        x2=[x_ori,x_n,x_n,x]
        y2=[y_ori,iy_cf,iy_cf+offset,y]
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

class Main(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui() # set UI
        self.setWindowTitle("주행고도")
        # self.setGeometry(500,100,1000,1300)
        
    ############ UI setting ############    

    def init_ui(self):
        
        btn1 = QPushButton("load .CSV File",self)
        btn1.clicked.connect(self.btn_fun_FileLoad)
        
        pushbutton = QPushButton("create the graph!")
        pushbutton.clicked.connect(self.button_clicked)
        
        self.combobox_r1 = QLabel(self)
        self.combobox_r1.setText('Here, show the length of series')
        self.combobox_r2 = QLabel(self)
        self.combobox_r2.setText("")
        combobox_ex1 = QLabel("start point of series")
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

        layout = QVBoxLayout()
        layout.addWidget(btn1)
        layout.addWidget(self.combobox_r1)
        layout.addWidget(self.combobox_r2)
        layout.addWidget(combobox_)
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
        
    def btn_fun_FileLoad(self):        
        fname=QFileDialog.getOpenFileName(self)        
        # print(fname[0]) # directory of loaded data
        self.loadData(fname[0])
        str1="The data has been successfully loaded!! "+" (length:" + str(self.len_series)+")"
        self.combobox_r1.setText(str1)
        str2="start and end of series must be " +str(0) + " to " + str(self.len_series-1)
        self.combobox_r2.setText(str2)
               
    def button_clicked(self):
        self.runMain()

    def set_graph1(self, item):
        # self.st = int(item)
        try:
            self.st = int(item)
        except ValueError:
            pass
        else:
            pass
        
    def set_graph2(self, item):
        # self.en = int(item)
        try:
            self.en = int(item)
        except ValueError:
            pass
        else:
            pass
        
    def set_graph3(self, item):
        # self.num = int(item)   
        try:
            self.num = int(item)
        except ValueError:
            pass
        else:
            pass
    
    def set_graph4(self, item):
        global offset
        # offset = int(item)   
        try:
            offset = int(item)
        except ValueError:
            pass
        else:
            pass

    def create_plot(self):
        self.win_2()
    
    def win_2(self):
        window_2=second()
        window_2.exec_()
    
    def loadData(self,str_dir):
        self.Data=np.empty((0,3))
        f=open(str_dir)
        rdr=csv.reader(f)
        for i,line in enumerate(rdr):
            if i==0:
                continue
            else: 
                temp=np.array(line);temp=np.reshape(temp,(1,3))
                self.Data=np.append(self.Data,temp,axis=0)
        self.len_series=i
        f.close()
    
    def getData(self): # set the length of series
        Neajang=np.arange(self.st,self.st+self.num_len)
        al=self.Data[Neajang,0] # '0' means column 1: altitude
        al=al.astype(np.float64)
        dist = np.linspace(0,10,len(al))
        return al, dist

    def runMain(self):
        # get metadata
        st=self.st
        self.num_len = self.en-self.st+1
        global y_ori, x_ori
        y_ori, x_ori = self.getData() # y means altitude, x means cumlitive distance (km)
        
        # select data
        ind=np.linspace(0,len(y_ori)-1,self.num); ind=ind.astype(np.int32)
        global y, x, x_n
        y=y_ori[ind]; x=x_ori[ind]
        x_n=np.linspace(0,x_ori[-1],len(y_ori)*5)
        
        # spline interpolation
        global ipo, iy
        ipo = spi.splrep(x,y,k=3) # make cubic spline (k=3)
        iy=spi.splev(x_n,ipo,der=0)
        
        # curve fitting
        # quadratic polynomial (order 2)
        def func(x,a,b,c):
            return a*x**2+b*x+c
        global popt, pcov, iy_cf
        popt, pcov =curve_fit(func,x,y)
        iy_cf=func(x_n,*popt)
        
        self.create_plot()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = Main()
    sys.exit(app.exec_())