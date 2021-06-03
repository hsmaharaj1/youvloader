"""
Project: YouVLoader
Written by: Himanshu S.
Designed by: Jagannath T.
HS CODES Copyright 2021
"""

from PyQt5 import uic, QtCore, QtWidgets, QtGui
import sys
from os import path
import pytube
from pytube.cli import on_progress

# For Fixing the Bug of placeHolder Text in PyQT5
import types
def paintEvent(self, event):
    painter = QtWidgets.QStylePainter(self)
    painter.setPen(self.palette().color(QtGui.QPalette.Text))
    
    # draw the combobox frame, focusrect and selected etc.
    opt = QtWidgets.QStyleOptionComboBox()
    self.initStyleOption(opt)
    painter.drawComplexControl(QtWidgets.QStyle.CC_ComboBox, opt)
    
    if self.currentIndex() < 0:
        opt.palette.setBrush(
            QtGui.QPalette.ButtonText,
            opt.palette.brush(QtGui.QPalette.ButtonText).color().lighter(),
        )
        if self.placeholderText():
            opt.currentText = self.placeholderText()
    
    # draw the icon and text
    painter.drawControl(QtWidgets.QStyle.CE_ComboBoxLabel, opt)

class WorkerSignals(QtCore.QObject):
    finished = QtCore.pyqtSignal()

class Worker(QtCore.QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
    
    @QtCore.pyqtSlot()
    def run(self):
        global quality
        self.fn(self.args)
        self.signals.finished.emit()
        
    
class MWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MWindow, self).__init__()
        uic.loadUi("Resources/template.ui", self)
        self.offset = None
        self.stop = False
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        # Handling the Events to create the effects on the Buttons
        self.closebtn.installEventFilter(self)
        self.minimize.installEventFilter(self)

        self.closebtn.clicked.connect(self.closefunc) 
        self.minimize.clicked.connect(self.minim)

        # Other Members and Components
        global CHECK
        CHECK = ""
        global TF
        TF = 0
        self.pool = QtCore.QThreadPool.globalInstance()
        
        # Checking if the Data is entered
        self.download_btn.installEventFilter(self)
        self.download_btn.paintEvent = types.MethodType(paintEvent, self.download_btn)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.offset = event.pos()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.offset is not None and event.buttons() == QtCore.Qt.LeftButton:
            self.move(self.pos() + event.pos() - self.offset)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.offset = None
        super().mouseReleaseEvent(event)
    
    # Hovering Effect Testing
    def eventFilter(self, object, event):
        if event.type() == QtCore.QEvent.Enter:
            if object is self.closebtn:
                self.closebtn.setText("X")
            if object is self.minimize:
                self.minimize.setText("-")
            self.stop = True
            return True
        elif event.type() == QtCore.QEvent.Leave:
            self.closebtn.setText("")
            self.minimize.setText("")
            self.stop = False

        # This is for Handling Download btn click
        elif object is self.download_btn and event.type() == QtCore.QEvent.MouseButtonPress:
            try:
                self.initYoutube()
            except:
                pass
        return False

    # Methods of Titlebar Buttons
    def closefunc(self):
        self.close()
    def minim(self):
        self.showMinimized()

    # Main Methods Utility
    def start_anime(self):
        self.movie_1 = QtGui.QMovie("Resources/downloading.gif")
        self.set_animation.setMovie(self.movie_1)
        self.movie_1.start()
        
    def loadTime(self, b):
        self.movie_2 = QtGui.QMovie("Resources/loading.gif")
        self.set_animation.setMovie(self.movie_2)
        self.movie_2.setSpeed(140)
        if b == 1:
            self.movie_2.start()
        elif b == 0:
            self.movie_2.stop()

    def progress_func(self, stream=None,chunk=None, bytes_remaining=None):
        self.start_anime()
    
    # For Animating at the end of the Download
    def complete_func(self, stream = None, filepath = None):
        self.movie_3 = QtGui.QMovie("Resources/done.gif")
        self.set_animation.setMovie(self.movie_3)
        self.movie_3.start()
        print("Completed!")
    
    # Pompt the User to select the saving location
    def askLocation(self):
        location = QtWidgets.QFileDialog.getExistingDirectory(self, "Save Location", "", QtWidgets.QFileDialog.ShowDirsOnly)
        if location:
            return location
        else:
            self.download_btn.setCurrentIndex(-1)
            self.loadTime(0)
            self.showPop()

    def download_created(self, _): # Used in 'selection' method
        try:
            global YT
            global QUALITY
            selected_stream = YT.streams.get_by_resolution(QUALITY)
            global PATH
            self.download_btn.setCurrentIndex(-1)
            selected_stream.download(PATH)
        except:
            self.download_btn.setCurrentIndex(-1)
            self.showPop()
        
    # This gets the quality that the user chooses
    def selection(self):
        global QUALITY
        QUALITY = self.download_btn.currentText()
        if self.download_btn.currentIndex() != -1:
            try:
                global PATH
                PATH = self.askLocation() + "/"
                self.loadTime(0)
                self.start_anime()
                worker = Worker(self.download_created)
                self.pool.start(worker)
                worker.signals.finished.connect(self.complete_func)
            except TypeError:
                self.download_btn.setCurrentIndex(-1)
                return
    
    def initYoutube(self):
        global CHECK
        global TF
        if CHECK != self.get_input():
            self.loadTime(1)
            worker1 = Worker(self.download_youtube)
            self.pool.start(worker1)
            worker1.signals.finished.connect(self.showPop)
            if TF == 1:
                self.loadTime(0)
                self.input_error()
                TF = 0
                
    def get_input(self):
        return self.input_url.toPlainText()

    def showPop(self):
        self.download_btn.showPopup()
    
    def hidePop(self):
        self.download_btn.hidePopup()
    
    # Fetching the details about the Link from Youtube
    def download_youtube(self, _):
        global CHECK
        global TF
        CHECK = self.get_input()
        self.download_btn.clear()
        enter_url = self.get_input()
        global YT
        try:
            YT = pytube.YouTube(
                enter_url,
                on_progress_callback = on_progress, 
                on_complete_callback = self.complete_func)
            videos = YT.streams.filter(mime_type="video/mp4", progressive="True")
            for i in videos:
                self.download_btn.addItem(str(i.resolution))
            TF = 0
        except:
            TF = 1
        # Display all the available qualities
        self.download_btn.currentIndexChanged.connect(self.selection)
    
    # Error message prompt
    def input_error(self):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText("Opps!! Retry Again")
        msg.setWindowTitle("INFO")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec()

App = QtWidgets.QApplication(sys.argv)
window = MWindow()
window.show()
App.exec_()
