#!/usr/bin/env python3

import sys, logging, os
from PyQt5 import QtGui, QtWidgets, QtCore


class ImageViewerGraphicView(QtWidgets.QGraphicsView):
    def __init__(self, parent=None):
        super().__init__()
        self.fit_in_view = True
        
        self.verticalScrollBar().setEnabled(False)
        self.horizontalScrollBar().setEnabled(False)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        
        self.installEventFilter(self)
        
    def eventFilter(self, object, event):
        if event.type() == QtCore.QEvent.KeyPress:
            if event.key() == QtCore.Qt.Key_F:
                if self.fit_in_view:
                    self.fit_in_view = False
                    self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
                else:
                    self.fit_in_view = True
                    self.fitInView(self.sceneRect(), QtCore.Qt.KeepAspectRatio)
                    self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
                    
        return QtWidgets.QWidget.eventFilter(self, object, event)


class ImageViewerGraphicScene(QtWidgets.QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__()
        self._parent = parent
        self.mouse_move = None
        self.mouse_drag = None
        
        self.rightclic_press = False
        self.middleclic_press = False
        self.leftclic_press = False
        
        self.mouse_pos_init = None
        self.widget_x_pos = None
        self.widget_y_pos = None
        self.widget_width = None
        self.widget_height = None
        self.widget_center_init = None
        
        self.installEventFilter(self)
    
    def eventFilter(self, object, event):
        mouse_pos = QtGui.QCursor().pos()
        x = mouse_pos.x()
        y = mouse_pos.y()
        
        if event.type() == QtCore.QEvent.GraphicsSceneMousePress:        
            self.mouse_pos_init = mouse_pos
            self.widget_x_pos = self._parent.pos().x()
            self.widget_y_pos = self._parent.pos().y()
            self.widget_width = self._parent.width()
            self.widget_height = self._parent.height()
            self.widget_center_init = self._parent.frameGeometry().center()
            
            if event.buttons() == QtCore.Qt.LeftButton:
                self.leftclic_press = True
            elif event.buttons() == QtCore.Qt.MiddleButton:
                self.middleclic_press = True
            elif event.buttons() == QtCore.Qt.RightButton:
                self.rightclic_press = True
        
        elif event.type() == QtCore.QEvent.GraphicsSceneMouseMove:
            self.mouse_move = True
        
        elif event.type() == QtCore.QEvent.GraphicsSceneMouseRelease:
            self.mouse_move = False
            self.rightclic_press = False
            self.middleclic_press = False
            self.leftclic_press = False
        
        elif event.type() == QtCore.QEvent.KeyPress:
            if event.key() == QtCore.Qt.Key_Escape:
                self._parent.close()
        
        self.mouse_drag = (self.leftclic_press and self.mouse_move)\
                        or (self.middleclic_press and self.mouse_move)\
                        or (self.rightclic_press and self.mouse_move)
        
        if self.mouse_drag:
            x_init = self.mouse_pos_init.x()
            y_init = self.mouse_pos_init.y()
            diff_x = x-x_init
            diff_y = y-y_init
            center_x_init = self.widget_center_init.x()
            center_y_init = self.widget_center_init.y()
            
            # DRAG MOVE
            if self.middleclic_press:
                self._parent.move(self.widget_x_pos+diff_x,
                                  self.widget_y_pos+diff_y)
            
            # RESIZE
            elif self.rightclic_press:
                # RIGHT
                if x_init > center_x_init:
                    # UP
                    if y_init < center_y_init:
                        self._parent.move(self.widget_x_pos,
                                          self.widget_y_pos+diff_y)
                        self._parent.resize(self.widget_width+diff_x,
                                            self.widget_height-diff_y)
                    # BOTTOM
                    else:
                        self._parent.resize(self.widget_width+diff_x,
                                            self.widget_height+diff_y)
                # LEFT
                else:
                    if y_init < center_y_init:
                        self._parent.move(self.widget_x_pos+diff_x,
                                          self.widget_y_pos+diff_y)
                        self._parent.resize(self.widget_width-diff_x,
                                            self.widget_height-diff_y)
                    # BOTTOM
                    else:
                        self._parent.move(self.widget_x_pos+diff_x,
                                          self.widget_y_pos)
                        self._parent.resize(self.widget_width-diff_x,
                                            self.widget_height+diff_y)
        
        return QtWidgets.QWidget.eventFilter(self, object, event)


class ImageViewerWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        
        self.pixmap = None
        self.scene = ImageViewerGraphicScene(parent=self)
        self.view = ImageViewerGraphicView(parent=self)
        
        self.installEventFilter(self)
        self.initUI()
        
    def initUI(self):
        self.resize(720, 300)
        self.setWindowTitle('Image Viewer')
        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)
        
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.view)
        hlayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(hlayout)
        
        self.show()
    
    def closeEvent(self, event):
        self.deleteLater()
    
    def resizeEvent(self, event):
        if self.view.fit_in_view:
            self.view.fitInView(self.scene.sceneRect(),
                                QtCore.Qt.KeepAspectRatio)
    
    def mouseDoubleClickEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            self.close()
    
    def wheelEvent(self, event):
        delta = event.angleDelta() / 120
        delta = delta.y()
        scale = 1.05
        if delta >= 1:
            self.view.scale(scale, scale)
        else:
            self.view.scale(1/scale, 1/scale)
        
        if self.view.fit_in_view:
            self.view.fit_in_view = False
            self.view.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
    
    def set_image(self, image_path):
        self.pixmap = QtGui.QPixmap(image_path)
        self.scene.addPixmap(self.pixmap)
        self.view.setScene(self.scene)
        if self.view.fit_in_view:
            self.view.fitInView(self.scene.sceneRect(),
                                QtCore.Qt.KeepAspectRatio)


def set_stylesheet(app, style_path):
    file_qss = QtCore.QFile(style_path)
    if file_qss.exists():
        file_qss.open(QtCore.QFile.ReadOnly)
        styleSheet = QtCore.QTextStream(file_qss).readAll()
        app.setStyleSheet(styleSheet)
        file_qss.close()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    #app.setStyle('Plastique')
    set_stylesheet(app, 'style.qss')
    viewer = ImageViewerWidget()
    viewer.set_image('/home/vincentg/image.png')
    sys.exit(app.exec())
