# -*- coding: utf-8 -*-
"""
Created on Mon Jul 24 08:57:19 2017

@author: ljm
"""

import sys
import cv2
from PIL import ImageGrab
import numpy as np
from PyQt5.QtWidgets import (QMainWindow,QApplication, QWidget, QVBoxLayout,QHBoxLayout,
                             QLabel,QPushButton,QAction,qApp,QFileDialog)
from PyQt5.QtGui import QImage,QPixmap,QIcon
from PyQt5.QtCore import QMutex,QMutexLocker,QThread,pyqtSignal,Qt
import time
import ImagePathHander as imp

rootPath='E:\\Python\\videoDemo\\image\\'


class MainWindow(QMainWindow):
    def __init__(self, parent = None):
        QWidget.__init__(self)
        self.resize(550, 550)
        self.setWindowTitle('鼻内镜影像智能分析系统')
        self.setWindowFlags(self.windowFlags()|Qt.WindowStaysOnTopHint)
        self.status = 0 #0 is init status;1 is capture screen
        
        self.imPath=imp.ImagePath('path.conf')
        self.imgeDirPath=self.imPath.getPath
        self.firstImage=None
        self.count=1
        self.im_video=None
        self.time=0
        self.image = QImage()
        
        menuAction = QAction(QIcon('C:\\Users\\ljm\\Anaconda3\\Lib\\site-packages\\spyder\\images\\actions\\browse_tab.png'), '&设置路径', self)
        menuAction.setStatusTip('设置目标文件夹路径')
        menuAction.triggered.connect(self.showPathDialog)

        #菜单
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&文件')
        fileMenu.addAction(menuAction)
        #图片
        self.piclabel = QLabel('pic')
        
        #初始化按钮
        self.capturebtn = QPushButton('capture')
        self.label=QLabel('capture/pause:F12')
        
        # 界面布局
        hbox = QHBoxLayout()
        hbox.addWidget(self.capturebtn)
        hbox.addWidget(self.label)
        
        vbox = QVBoxLayout()
        vbox.addWidget(self.piclabel)
        vbox.addLayout(hbox)
        self.setLayout(vbox)
        
        #加载初始页面
        if self.image.load("1.jpg"):  
            self.piclabel.setPixmap(QPixmap.fromImage(self.image))
        #设定定时器
        self.timer = Timer() #录制视频 
        
        #信号--槽
        self.capturebtn.clicked.connect(self.PauseBegin)
        self.timer._signal.connect(self.CaptureScreen)
        
    def showPathDialog(self):
        dir_path = QFileDialog.getExistingDirectory(self,"选择图像文件夹...",'./')
        self.imgeDirPath=dir_path
        self.imPath=imp.ImagePath('path.conf')
        self.imPath.setPath(dir_path )
    def keyPressEvent(self, e):
        if e.key() == Qt.Key_F12:
            self.PauseBegin()
            
    def PauseBegin(self):
        self.status,  capturestr = ((1, 'pause'), (0,  'capture'))[self.status]
        self.capturebtn.setText(capturestr)
        if self.status is 1:#状态0，截屏           
            self.timer.start()
        else:
            self.timer.stop()
        
        
    def CaptureScreen(self):
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
        
            
    
class Timer(QThread):
    _signal= pyqtSignal(str)
    def __init__(self, signal = "updateTime", parent=None):
        super(Timer, self).__init__(parent)
        self.stoped = False
        self.signal = signal
        self.mutex = QMutex()


    def run(self):
        with QMutexLocker(self.mutex):
            self.stoped = False
        while True:
            if self.stoped:
                return
            self._signal.emit(self.signal)
            time.sleep(2) #40毫秒发送一次信号，每秒25帧
    
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


    
    
if __name__ == "__main__" :
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance() 
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())