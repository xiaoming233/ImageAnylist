# -*- coding: utf-8 -*-
"""
Created on Wed Jul 12 16:55:49 2017

@author: ljm
"""

import sys
import cv2
from PIL import ImageGrab
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QLabel,QPushButton
#from PyQt5.QtGui import QImage,QPixmap
from PyQt5.QtCore import QMutex,QMutexLocker,QThread,pyqtSignal,Qt


#this is important for capturing/displaying images
import time


rootPath='E:\\Python\\videoDemo\\image\\'


class MainWindow(QWidget):
    def __init__(self, parent = None):
        QWidget.__init__(self)
        self.resize(180, 15)
        self.setWindowTitle('screen capture')
        self.status = 0 #0 is init status;1 is capture screen

        self.firstImage=None
        self.count=1
        self.im_video=None
        self.time=0
        
        #初始化按钮
        self.capturebtn = QPushButton('capture')
        self.label=QLabel('capture/pause:F12')
        # 界面布局
        hbox = QHBoxLayout()
        hbox.addWidget(self.capturebtn)
        hbox.addWidget(self.label)
        
        self.setLayout(hbox)
        
        
        #设定定时器
        self.timer = Timer() #录制视频 
        
        #信号--槽
        self.capturebtn.clicked.connect(self.PauseBegin)
        self.timer._signal.connect(self.CaptureScreen)
        
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
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())