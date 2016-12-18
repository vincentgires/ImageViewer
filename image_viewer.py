#!/usr/bin/env python3

import sys, logging, os
from PyQt5 import QtGui, QtWidgets, QtCore


class IMAGE_VIEWER_View(QtWidgets.QGraphicsView):
    def __init__(self, parent=None):
        super().__init__()

class IMAGE_VIEWER_Scene(QtWidgets.QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__()
        self._parent = parent
        self.mouse_press = None
        self.mouse_move = None
        self.mouse_drag = None
        self.installEventFilter(self)

    def eventFilter(self, object, event):
        mouse_pos = QtGui.QCursor().pos()
        x = mouse_pos.x()
        y = mouse_pos.y()
        
        if event.type() == QtCore.QEvent.GraphicsSceneMousePress:        
            self.mouse_press = True
            
            if event.buttons() == QtCore.Qt.LeftButton or event.buttons() == QtCore.Qt.MiddleButton:
                self.mouse_pos_init = mouse_pos
                self.widget_x_pos = self._parent.pos().x()
                self.widget_y_pos = self._parent.pos().y()
            elif event.buttons() == QtCore.Qt.RightButton:
                self.widget_width = self._parent.width()
                self.widget_height = self._parent.height()
                
                
            
        elif event.type() == QtCore.QEvent.GraphicsSceneMouseMove:
            self.mouse_move = True
                
            
        elif event.type() == QtCore.QEvent.GraphicsSceneMouseRelease:
            self.mouse_press = False
            self.mouse_move = False
            
        elif event.type() == QtCore.QEvent.KeyPress:
            if event.key() == QtCore.Qt.Key_Escape:
                self._parent.close()
        
        self.mouse_drag = (self.mouse_press and self.mouse_move)
        if self.mouse_drag:
            x_init = self.mouse_pos_init.x()
            y_init = self.mouse_pos_init.y()
            diff_x = x-x_init
            diff_y = y-y_init
            
            if event.buttons() == QtCore.Qt.LeftButton or event.buttons() == QtCore.Qt.MiddleButton:
                self._parent.move(self.widget_x_pos+diff_x, self.widget_y_pos+diff_y)
                
            elif event.buttons() == QtCore.Qt.RightButton:
                self._parent.resize(self.widget_width+diff_x, self.widget_height+diff_y)
            
            
        return True

class IMAGE_VIEWER_Widget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        
        self.widget_close = None
        self.pixmap = None
        self.scene = IMAGE_VIEWER_Scene(parent=self)
        self.view = IMAGE_VIEWER_View(parent=self)
        
        self.installEventFilter(self)
        
        self.initUI()
        
        
    def initUI(self):
        #self.setGeometry(2000, 300, 720, 300)
        self.resize(720, 300)
        #self.move(QtWidgets.QDesktopWidget().availableGeometry().center())
        
        self.setWindowTitle("Image Viewer")
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)
        
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.view)
        self.setLayout(hlayout)
        
        self.show()
    
    def closeEvent(self, event):
        self.widget_close = True
    
    def resizeEvent(self, event):
        self.view.fitInView(self.scene.sceneRect(), QtCore.Qt.KeepAspectRatio)
    
    def mouseDoubleClickEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            #QtCore.QCoreApplication.instance().quit()
            self.close()
        
    '''
    def mousePressEvent(self, event):
        print ('mousePress')
        self.offset = event.pos()

    def mouseMoveEvent(self, event):
        print ('mouseMove')
        if event.buttons() == QtCore.Qt.LeftButton:
            print ("Left click drag")
        elif event.buttons() == QtCore.Qt.RightButton:
            print ("Right click drag")
    '''

    def setImage(self, image_path):
        self.pixmap = QtGui.QPixmap(image_path)
        
        self.scene.addPixmap(self.pixmap)
        self.view.setScene(self.scene)
        
        self.view.fitInView(self.scene.sceneRect(), QtCore.Qt.KeepAspectRatio)
        
        
        
        
        

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    #nw_utils.setStyleSheet(app)
    
    viewer = IMAGE_VIEWER_Widget()
    #viewer.setImage("//NWAVE/PROJECTS/SOB/RENDER_COMPO/ref_grading/200/comp/int/final/200_0060_int_ref_grading_final_l.0596.jpg")
    viewer.setImage("/home/vincent/branch.png")
    
    
    sys.exit(app.exec())

