# -*- coding: utf-8 -*-
"""
Created on Fri Jul 14 10:17:06 2017

@author: ljm
"""
from PIL import ImageGrab
import cv2
import numpy as np
import imutils

rootPath='E:\\Python\\videoDemo\\image\\'
firstImage=None
count=1
im_video=None
time=0

cv2.namedWindow('image', cv2.WINDOW_AUTOSIZE)
key = cv2.waitKey(0) & 0xFF
im = ImageGrab.grab()
im= np.array(im)
cv2.cvtColor(im, cv2.COLOR_RGB2BGR, im)
#im = imutils.resize(im, width=500)
gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
#gray = cv2.GaussianBlur(gray, (21, 21), 0)
if firstImage is None:
    firstImage = gray
if key == ord("s"):
    while True:    
        im = ImageGrab.grab()
        im= np.array(im)
        cv2.cvtColor(im, cv2.COLOR_RGB2BGR, im)
        #im = imutils.resize(im, width=500)
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        if firstImage is None:
            firstImage = gray
            continue
        if time>3:
            time=0
            firstImage = gray
            continue
        ImageDelta = cv2.absdiff(firstImage, gray)
        thresh = cv2.threshold(ImageDelta, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]
     
        # 扩展阀值图像填充孔洞，然后找到阀值图像上的轮廓
        thresh = cv2.dilate(thresh, None, iterations=2)
        _a,cnts,_b= cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        # 遍历轮廓
        for c in cnts:
            # if the contour is too small, ignore it
            (x, y, w, h) = cv2.boundingRect(c)
            if w<100 or h<100:
                continue
            
            im_video=im[y: y + h,x:x + w]
            #cv2.rectangle(im, (x, y), (x + w, y + h), (0, 255, 0), 2)
            #cv2.imshow("im_video", im_video)
            #cv2.imwrite(rootPath+str(count)+'.jpg',im_video)
        #cv2.imshow("image", im)
        #cv2.imshow("Thresh", thresh)
        #cv2.imshow("Image Delta", ImageDelta)
        if im_video is not None :
            #cv2.imshow("im_video", im_video)
            cv2.imwrite(rootPath+str(count)+'.jpg',im_video)
        count+=1
        time+=1
        key = cv2.waitKey(1000) & 0xFF
        # 如果q键被按下，跳出循环
        if key == ord("q"):
            break
cv2.destroyAllWindows()