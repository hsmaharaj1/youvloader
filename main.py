"""
Project: YouVLoader
Written by: Himanshu S.
Designed by: Jagannath T.
HS CODES Copyright 2021
"""
from PyQt5 import uic, QtCore, QtWidgets, QtGui
import sys
import os
import pytube
from pytube.extract import video_id
from pytube.cli import on_progress

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

        # Other UI Components
        global check
        check = ""
        # Checking if the Data is entered
        self.download_btn.installEventFilter(self)

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
                self.download_youtube()
            except:
                pass
        return False

    # Methods of Titlebar Buttons
    def closefunc(self):
        self.close()
    def minim(self):
        self.showMinimized()

    # Main Method Utility
    def start_anime(self):
        self.movie_1 = QtGui.QMovie("Resources/downloading.gif")
        self.set_animation.setMovie(self.movie_1)
        self.movie_1.start()

    def progress_func(self, stream=None,chunk=None, bytes_remaining=None):
        self.start_anime()

    def complete_func(self, stream = None, filepath = None):
        self.movie_3 = QtGui.QMovie("Resources/done.gif")
        self.set_animation.setMovie(self.movie_3)
        self.movie_3.start()
        print("Completed!")

    def download(self, qual): # Used in 'selection' method
        selected_stream = yt.streams.get_by_resolution(qual)
        self.progress_func()
        selected_stream.download()

    def selection(self):
        global quality
        quality = self.download_btn.currentText()
        print(quality)
        self.download(quality) # Calls a method called 'download'
    
    def get_input(self):
        return self.input_url.toPlainText()

    def download_youtube(self):
        global check
        if check != self.get_input():
            check = self.get_input()
            self.download_btn.clear()
            enter_url = self.get_input()
            try:
                global yt
                yt = pytube.YouTube(
                    enter_url,
                    on_progress_callback = on_progress, 
                    on_complete_callback = self.complete_func)
                
                self.start_anime()
            except:
                self.input_error()
            VIDEO_TITLE = (yt.title)
            global VIDEO_ID
            VIDEO_ID = (yt.video_id)
            videos = yt.streams.filter(mime_type="video/mp4", progressive="True")

            # Display all the available qualities
            for i in videos:
                # print(i.resolution, i.itag)
                self.download_btn.addItem(i.resolution)
            self.download_btn.currentIndexChanged.connect(self.selection)
        
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
