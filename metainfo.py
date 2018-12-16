from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

menuAction = QAction()

print(menuAction.metaObject().classInfoCount())#0
print(menuAction.metaObject().indexOfMethod('activate()'))#-1
print('methodCount: ' + str(menuAction.metaObject().methodCount()))#17
print('propertyCount: ' + str(menuAction.metaObject().propertyCount()))
for i in range(1, 18):
    print(menuAction.metaObject().method(i).name())

##print(menuAction.metaObject().method(1).name())#QMetaMethod object 0x7f90929cdac8
##print(menuAction.metaObject().method(2).name())
##print(menuAction.metaObject().method(3).name())
##print(menuAction.metaObject().method(4).name())
#menuAction.triggered.connect(print)
print(menuAction.metaObject().indexOfSignal('triggered()'))
