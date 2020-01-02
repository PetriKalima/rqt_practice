from PyQt5.QtWidgets import QWidget, QLabel, QFrame, QPushButton, QHBoxLayout, QVBoxLayout, QScrollArea, QSizePolicy, QGroupBox, QApplication, QStackedWidget, QSlider, QGridLayout, QTabWidget
from PyQt5.QtCore import Qt, QObject, QRunnable, pyqtSignal, pyqtSlot, QSize, QThreadPool, pyqtProperty, QPropertyAnimation
from PyQt5.QtGui import QColor, QPalette, QPixmap, QCursor, QFont

class TestWidget(QWidget):

    def __init__(self, title="Test Widget"):
        super(TestWidget, self).__init__()
        self.VBox = QVBoxLayout(self)
        self.VBox.setAlignment(Qt.AlignTop)
        #self.addButtons()
        #self.VBox.addWidget(self.buttonWidget)
        tabs = MyTabWidget(self)
        self.VBox.addWidget(tabs)



class TestButtons(QWidget):

    def __init__(self, parent):
        super(TestButtons, self).__init__(parent)
        self.buttonLayout = QHBoxLayout(self)
        self.buttonLayout.setAlignment(Qt.AlignCenter)
        self.addButtons()

    def addButtons(self):
        for i in range(4):
            button = QPushButton("Test button " + str(i))
            sizePolicy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
            button.setSizePolicy(sizePolicy)
            self.buttonLayout.addWidget(button)    

class MyTabWidget(QWidget):

    def __init__(self, parent):
        super(MyTabWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)
        
        # Initialize tab screen
        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tabs.resize(300,200)
        
        # Add tabs
        self.tabs.addTab(self.tab1,"Run Programs")
        self.tabs.addTab(self.tab2,"Create Programs")
        
        # Create first tab
        self.tab1.layout = QVBoxLayout(self)
        #self.pushButton1 = QPushButton("PyQt5 button")
        buttons = TestButtons(self)
        self.tab1.layout.addWidget(buttons)
        self.tab1.setLayout(self.tab1.layout)
        
        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)