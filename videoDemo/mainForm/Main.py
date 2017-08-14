# -*- coding: utf-8 -*-
"""
Created on Fri Jul 28 16:14:02 2017

@author: ljm
"""
import sys
from PyQt5.QtWidgets import QApplication
from MainForm import MainWindow

if __name__ == "__main__" :
    
    if not QApplication.instance():
         app = QApplication(sys.argv)
    else:
         app = QApplication.instance()
    #app = QApplication.instance()
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())