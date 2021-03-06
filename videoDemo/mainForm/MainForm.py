# -*- coding: utf-8 -*-
"""
Created on Mon Jul 24 08:57:19 2017

@author: ljm
"""


import cv2
from PIL import ImageGrab
import numpy as np
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QAction, QFileDialog,QComboBox)
from PyQt5.QtGui import QImage, QPixmap, QIcon
from PyQt5.QtCore import QMutex, QMutexLocker, QThread, pyqtSignal, Qt
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
from suds.client import Client
import base64
import os.path
from Config import ConfigHander
import requests
from RectangleHander import RecSetForm

rootPath='E:\\Python\\videoDemo\\image\\'


class MainWindow(QMainWindow):
    def __init__(self, parent = None):
        super().__init__()
        self.status = 0 #0 is init status;1 is capture screen
        
        config=ConfigHander('config.conf')
        self.imDirPath= config.getImDirPath()
        self.box= tuple(eval(config.getRectangleSize()))
        self.firstImage=None
        self.count=1
        self.im_video=None
        self.time=0
        self.observer = Observer()
        #self.imageOnCreateEventHander()
        self.initUI()
   
    def initUI(self):
        self.resize(550, 550)
        self.setWindowTitle('鼻内镜影像智能分析系统')
        # self.setWindowFlags(self.windowFlags()|Qt.WindowStaysOnTopHint)
        
        self.image = QImage()
        
        menuDirPath = QAction(QIcon('icon\\browse_tab.png'), '&设置路径', self)
        menuDirPath.setStatusTip('设置目标图像文件夹路径')
        menuDirPath.triggered.connect(self.showPathDialog)
        menuRectangle = QAction(QIcon('icon\\expand_selection.png'), '&设置矩形区域', self)
        menuRectangle.setStatusTip('设置截图的矩形区域')
        menuRectangle.triggered.connect(self.showRecSetForm)
        #菜单
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&文件') #         
        fileMenu.addAction(menuDirPath)
        fileMenu.addAction(menuRectangle)

        #图片
        self.piclabel = QLabel(self)
        
        #初始化按钮
        self.capturebtn = QPushButton('开始')
        self.capturelbe=QLabel('开始/停止:F12')
        self.resultlbe=QLabel('结果：')

        self.combobox = QComboBox(self)
        self.combobox.addItem('从文件夹读取')
        self.combobox.addItem('手动截图')
        self.combobox.addItem('自动截图')
        # 界面布局
        hbox = QHBoxLayout()
        hbox.addWidget(self.combobox)
        hbox.addWidget(self.capturebtn)
        hbox.addWidget(self.capturelbe)
        hbox.addSpacing(30)
        hbox.addWidget(self.resultlbe)
        hbox.addStretch(1)

        vbox = QVBoxLayout()
        vbox.addWidget(self.piclabel)
        #vbox.addStretch(1)
        vbox.addLayout(hbox)
        cetralWidget= QWidget(self)
        cetralWidget.setLayout(vbox)
        self.setCentralWidget(cetralWidget)


        #加载初始页面
        if self.image.load("1.jpg"):
           self.piclabel.setPixmap(QPixmap.fromImage(self.image))
        #设定定时器
        self.timerAuto = Timer('Auto',2) #自动截图
        self.timerManual = Timer('Manual',5)  # 手动截图
        #信号--槽
        self.capturebtn.clicked.connect(self.pauseBegin)
        self.timerAuto._signal.connect(self.captureScreenAuto)
        self.timerManual._signal.connect(self.captureScreenManual)

    def showPathDialog(self):
        dir_path = QFileDialog.getExistingDirectory(self,"选择图像文件夹...", '/')
        self.imDirPath=dir_path
        self.config.setImDirPath(dir_path )

    def showRecSetForm(self):
        self.hide()
        app = RecSetForm()
        app.mainloop()
        config = ConfigHander('config.conf')
        self.box = tuple(eval(config.getRectangleSize()))
        self.show()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_F12:
            self.pauseBegin()
            
    def pauseBegin(self):
        if not self.imDirPath.strip():
            self.showPathDialog()
        self.status,  capturestr = ((1, '停止'), (0,  '开始'))[self.status]
        self.capturebtn.setText(capturestr)
        if self.status is 1:
            if self.combobox.currentText()=='从文件夹读取':
                # self.observer = Observer()
                # self.imageOnCreateEventHander()
                # self.observer.start()
                self.resultlbe.setText(self.combobox.currentText())
            elif self.combobox.currentText()=='手动截图':
                # self.timerManual.start()
                self.resultlbe.setText(self.combobox.currentText())
            elif self.combobox.currentText() == '自动截图':
                # self.timerManual.start()
                self.resultlbe.setText(self.combobox.currentText())
            self.combobox.setDisabled(True)
        else:

            if self.combobox.currentText()=='从文件夹读取':
                pass
                # self.observer.stop()
            elif self.combobox.currentText()=='手动截图':
                pass
                # self.timerManual.stop()
            elif self.combobox.currentText() == '自动截图':
                pass
                # self.timerManual.stop()
            self.combobox.setDisabled(False)

            #self.timer.stop()

    def captureScreenManual(self):

        im = ImageGrab.grab(self.box)
        im.save('134.jpeg')
        #self.piclabel.setPixmap(im)


    def captureScreenAuto(self):
        im = ImageGrab.grab()
        im= np.array(im)
        cv2.cvtColor(im, cv2.COLOR_RGB2BGR, im)
        #im = imutils.resize(im, width=500)
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        #gray = cv2.GaussianBlur(gray, (21, 21), 0)
        if self.firstImage is None:
            self.firstImage = gray
            return
#==============================================================================
#         if self.time>3:
#             self.time=0
#             self.firstImage = gray
#             return
#==============================================================================
        imageDelta = cv2.absdiff(self.firstImage, gray)
        thresh = cv2.threshold(imageDelta, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]
     
        # 扩展阀值图像填充孔洞，然后找到阀值图像上的轮廓
        thresh = cv2.dilate(thresh, None, iterations=2)
        _a,cnts,_b= cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        # 遍历轮廓
        for c in cnts:
            # if the contour is too small, ignore it
            (x, y, w, h) = cv2.boundingRect(c)
            if w<100 or h<100:
                continue
            
            self.im_video=im[y: y + h,x:x + w]
            #cv2.rectangle(im, (x, y), (x + w, y + h), (0, 255, 0), 2)
            #cv2.imshow("im_video", im_video)
            #cv2.imwrite(rootPath+str(count)+'.jpg',im_video)
        #cv2.imshow("image", im)
        #cv2.imshow("Thresh", thresh)
        #cv2.imshow("Image Delta", ImageDelta)
        if self.im_video is not None :
            #cv2.imshow("im_video", im_video)
            cv2.imwrite(rootPath+str(self.count)+'.jpg',self.im_video)
        self.count+=1
        self.time+=1

    def imageOnCreateEvent(self, event):
        if not event.is_directory:
            #fileUpload=FileUpload(event.src_path);
            #fileUpload.start()
            # file = open(event.src_path, 'rb')
            # file_data = base64.b64encode(file.read())
            # client = Client('http://localhost:9000/?wsdl')
            # client.service.add(os.path.basename(event.src_path), file_data)
            try:
                url = 'http://localhost:8088'
                # path = u'test2.jpg'
                # print(path)
                with open(event.src_path, 'rb') as im:
                    files = {'file': im}
                r = requests.post(url, files=files)
                print(r.content)
            except:
                pass
            self.piclabel.setPixmap(QPixmap(event.src_path))

    def imageOnCreateEventHander(self):
        #监测图像文件的生成
        self.fileEventHander = FileSystemEventHandler()
        self.fileEventHander.on_created = self.imageOnCreateEvent
        self.observer.schedule(self.fileEventHander, self.imDirPath, recursive=True)

        
            
    
class Timer(QThread):
    _signal= pyqtSignal(str)
    def __init__(self, signal = "Timer", period=0.04,parent=None):
        super(Timer, self).__init__(parent)
        self.stoped = False
        self.signal = signal
        self.mutex = QMutex()
        self.period=period

    def run(self):
        with QMutexLocker(self.mutex):
            self.stoped = False
        while True:
            if self.stoped:
                return
            self._signal.emit(self.signal)
            time.sleep(self.period) #默认40毫秒发送一次信号，每秒25帧
    
    def stop(self):
        with QMutexLocker(self.mutex):
            self.stoped = True
        
    def isStoped(self):    
        with QMutexLocker(self.mutex):
            return self.stoped

#==============================================================================
# class KeyPress(QThread):
#     _signal= pyqtSignal()
#     def __init__(self, parent=None):
#         super(Timer, self).__init__(parent)
#         self.stoped = False 
#     def onKeyboardEvent(self,event): 
#         if event.Key=='f12':
#             self._signal.emit()
#             
#     def run(self):
#         self.hm.KeyDown = self.onKeyboardEvent
#         self.hm.HookKeyboard()
#         pythoncom.PumpMessages()
#==============================================================================
class FileUpload(QThread):

    def __init__(self, file_path, parent=None):
        super(FileUpload, self).__init__(parent)
        self.file_path = file_path

    def run(self):
        file = open(self.file_path, 'rb')
        file_data = base64.b64encode(file.read())
        client = Client('http://localhost:9000/?wsdl')
        client.service.add(os.path.basename(self.file_path), file_data)

    
    
