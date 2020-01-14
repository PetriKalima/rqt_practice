from PyQt5.QtWidgets import QWidget, QLabel, QFrame, QPushButton, QHBoxLayout, \
QVBoxLayout, QScrollArea, QSizePolicy, QGroupBox, QApplication, QStackedWidget, QSlider, QGridLayout, QTabWidget, QTableWidget, QTableWidgetItem, QLineEdit
from PyQt5.QtCore import Qt, QObject, QRunnable, pyqtSignal, pyqtSlot, QSize, QThreadPool, pyqtProperty, QPropertyAnimation
from PyQt5.QtGui import QColor, QPalette, QPixmap, QCursor, QFont

from time import sleep
from functools import partial
import traceback
import sys

from panda_pbd.msg import MoveToEEGoal, MoveToContactActionGoal, UserSyncGoal
from panda_pbd.srv import MoveFingersRequest, ApplyForceFingersRequest

from panda_eup.pbd_interface import PandaPBDInterface
import panda_eup.panda_primitive as pp
#from pbd_interface import PandaPBDInterface
#import panda_primitive as pp

class TestWidget(QWidget):

    def __init__(self, title="Test Widget"):
        super(TestWidget, self).__init__()
        self.threadpool = QThreadPool()
        self.programThreadPool = QThreadPool()
        self.VBox = QVBoxLayout(self)
        self.VBox.setAlignment(Qt.AlignTop)
        self.tabs = MyTabWidget(self)
        self.VBox.addWidget(self.tabs)
        self.primitiveList = {
                              "Move to EE": (MoveToEEGoal, pp.MoveToEE),
                              "Move to contact": (MoveToContactActionGoal, pp.MoveToContact),
                              "UserSync": (UserSyncGoal, pp.UserSync),
                              "Move fingers": (MoveFingersRequest, pp.MoveFingers),
                              "Apply force to fingers": (ApplyForceFingersRequest, pp.ApplyForceFingers)
                              }                    
        self.addButtonActions()
        self.addProgramButtonActions()
        self.addTableButtonActions()
        self.program = pp.PandaProgram()


    def addTableButtonActions(self):
        self.tabs.programPanel.programTable.actionButtons.saveButton.pressed.connect(self.saveProgram)
        self.tabs.programPanel.programTable.actionButtons.resetButton.pressed.connect(self.resetProgram)

    def executeProgramAction(self, fn):
        programWorker = ProgramWorker(fn)
        self.programThreadPool.start(programWorker)

    def addProgramButtonActions(self):
        self.tabs.programPanel.programMenu.buttons[0].pressed.connect(self.addMoveToEE)
        self.tabs.programPanel.programMenu.buttons[1].pressed.connect(self.addMoveToContact)
        self.tabs.programPanel.programMenu.buttons[2].pressed.connect(self.addUserSync)
        self.tabs.programPanel.programMenu.buttons[3].pressed.connect(self.addMoveFingers)
        self.tabs.programPanel.programMenu.buttons[4].pressed.connect(self.addApplyForceFingers)

    def saveProgram(self):
        inputField = self.tabs.programPanel.programTable.actionButtons.inputField
        filename =  inputField.text()
        if filename == '':
            self.program.dump_to_file("~/rqt_ws/src/rqt_mypkg/rqt_practice/Resources", "testprogram.pkl")
        else:
             self.program.dump_to_file("~/rqt_ws/src/rqt_mypkg/rqt_practice/Resources", str(filename) + '.pkl')   
        inputField.clear()     

    def resetProgram(self):
        self.program.primitives = []
        table = self.tabs.programPanel.programTable.programTable
        table.clear()
        table.setRowCount(1)


    def addMoveToEE(self):
        goal = MoveToEEGoal()
        move_to_ee_primitive = pp.MoveToEE()
        move_to_ee_primitive.set_parameter_container(goal)
        self.program.insert_primitive(move_to_ee_primitive, [None, None])
        #print(self.program.primitives)
        table = self.tabs.programPanel.programTable.programTable
        self.insertToTable(table, "Move to EE")

    def addMoveToContact(self):
        goal = MoveToContactActionGoal()
        move_to_contact_primitive = pp.MoveToContact()
        move_to_contact_primitive.set_parameter_container(goal)
        self.program.insert_primitive(move_to_contact_primitive, [None, None])
        table = self.tabs.programPanel.programTable.programTable
        self.insertToTable(table, "Move to contact")

    def addUserSync(self):
        goal = UserSyncGoal()
        usersync_primitive = pp.UserSync()
        usersync_primitive.set_parameter_container(goal)
        self.program.insert_primitive(usersync_primitive, [None, None])
        table = self.tabs.programPanel.programTable.programTable
        self.insertToTable(table, "UserSync")

    def addMoveFingers(self):
        request = MoveFingersRequest()
        #request.width = 0.05
        move_fingers_primitive = pp.MoveFingers()
        #move_fingers_primitive.set_parameter_container(request)
        self.program.insert_primitive(move_fingers_primitive, [None, None])
        table = self.tabs.programPanel.programTable.programTable
        self.insertToTable(table, "Move fingers")    

    def addApplyForceFingers(self):
        goal = ApplyForceFingersRequest()
        apply_force_fingers_primitive = pp.ApplyForceFingers()
        apply_force_fingers_primitive.set_parameter_container(goal)
        self.program.insert_primitive(apply_force_fingers_primitive, [None, None])
        table = self.tabs.programPanel.programTable.programTable
        self.insertToTable(table, "Apply force to fingers")      

    def insertToTable(self, table, label):
        newItem = QTableWidgetItem(label)
        rowNum = table.rowCount()
        if rowNum < len(self.program.primitives):
            table.insertRow(rowNum)
            table.move(rowNum - 1, 0)
            table.setItem(rowNum, 0, newItem)
        else:    
            table.setItem(rowNum - 1, 0, newItem)

    def changeButtonState(self):
        for button in self.tabs.buttons.buttons:
            state = button.isEnabled()
            button.setEnabled(abs(state - 1))        
    
    def addButtonActions(self):
        self.tabs.buttons.buttons[0].pressed.connect(partial(self.workerAction, self.testReturnToStart))
        self.tabs.buttons.buttons[1].pressed.connect(partial(self.workerAction, self.testExecuteAction))
        self.tabs.buttons.buttons[2].pressed.connect(partial(self.workerAction, self.testRevertAction))
        self.tabs.buttons.buttons[3].pressed.connect(partial(self.workerAction, self.testExecuteRest))

    def printResult(self, result):
        print(result)

    def workerAction(self, fn):
        self.changeButtonState()
        worker = Worker(fn)
        worker.signals.result.connect(self.printResult)  
        worker.signals.finished.connect(self.changeButtonState)
        self.threadpool.start(worker) 

    def testReturnToStart(self):
        print("Pretending to return to starting point")
        sleep(5)
        print("Return to start ended")
        return "Sample result from testReturnToStart"

    def testExecuteAction(self):
        print("Pretending to execute an action")
        sleep(5)
        print("Execute action ended")
        return "Sample result from testExecuteAction"

    def testRevertAction(self):
        print("Pretending to revert an action")
        sleep(5)
        print("Revert action ended")
        return "Sample result from testRevertAction"  

    def testExecuteRest(self):
        print("Pretending to execute rest of the program")
        sleep(5)
        print("Execute rest ended")  
        return "Sample result from testExecuteRest"        


class TestButtons(QWidget):

    def __init__(self, parent):
        super(TestButtons, self).__init__(parent)
        self.parent = parent
        self.buttonLayout = QHBoxLayout(self)
        self.buttonLayout.setAlignment(Qt.AlignCenter)
        self.buttons = []
        labels = ["Return to start", "Execute action", "Revert action", "Execute rest"]
        self.addTestButtons(labels)

    def addTestButtons(self, labels):
        for i in range(4):
            button = QPushButton(labels[i])
            sizePolicy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
            button.setSizePolicy(sizePolicy)
            self.buttonLayout.addWidget(button)
            self.buttons.append(button)
             

class MyTabWidget(QWidget):

    def __init__(self, parent):
        super(MyTabWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)
        
        # Initialize tab screen
        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        #self.tabs.resize(300,200)
        
        # Add tabs
        self.tabs.addTab(self.tab1,"Run Programs")
        self.tabs.addTab(self.tab2,"Create Programs")
        
        # Create first tab
        self.tab1.layout = QVBoxLayout(self)
        #self.pushButton1 = QPushButton("PyQt5 button")
        self.buttons = TestButtons(self.tab1)
        self.tab1.layout.addWidget(self.buttons)
        self.tab1.setLayout(self.tab1.layout)
        
        self.tab2.layout = QVBoxLayout(self)
        self.programPanel = ProgramPanel(self.tab2)
        self.tab2.layout.addWidget(self.programPanel)
        self.tab2.setLayout(self.tab2.layout)

        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

class TableActionButtons(QWidget):

    def __init__(self, parent):
        super(TableActionButtons, self).__init__(parent)
        self.layout = QHBoxLayout(self)
        self.saveButton = QPushButton("Save Program")
        self.inputField = QLineEdit()
        self.inputField.setPlaceholderText("Enter name for saved file")
        self.resetButton = QPushButton("Reset Program")
        self.saveButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.layout.addWidget(self.saveButton)
        self.layout.addWidget(self.inputField)
        self.layout.addWidget(self.resetButton)        

class ProgramTable(QWidget):

    def __init__(self, parent):
        super(ProgramTable, self).__init__(parent)
        self.createProgramTable()
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.programTable)
        self.actionButtons = TableActionButtons(self)
        self.layout.addWidget(self.actionButtons)


    def createProgramTable(self) :
        self.programTable = QTableWidget()
        self.programTable.setRowCount(1)
        self.programTable.setColumnCount(1)
        self.programTable.move(0,0)
    

class ProgramMenu(QWidget):

    def __init__(self, parent):
        super(ProgramMenu, self).__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignTop)
        self.addLabel()
        self.buttons = []
        self.addProgramButtons()

    def addLabel(self):
        titleText = QLabel("Add primitives for the program")
        titleText.setAlignment(Qt.AlignTop)
        self.layout.addWidget(titleText)  

    def addProgramButtons(self):
        labels = ["Move to EE", "Move to contact", "UserSync", "Move fingers", "Apply force to fingers"]
        for label in labels:
            newButton = QPushButton(label)
            sizePolicy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
            #newButton.setSizePolicy(sizePolicy)
            self.buttons.append(newButton)
            self.layout.addWidget(newButton)


class ProgramPanel(QWidget):

    def __init__(self, parent):
        super(ProgramPanel, self).__init__(parent)
        self.layout = QHBoxLayout(self)
        self.programTable = ProgramTable(self)
        self.programMenu = ProgramMenu(self)
        self.layout.addWidget(self.programTable)
        self.layout.addWidget(self.programMenu)
        #self.tablelayout = QVBoxLayout(self.layout)
        #self.tablelayout.addWidget(self.programTable)
        #self.layout.addWidget(self.tablelayout)

class ProgramWorker(QRunnable):

    def __init__(self, fn, *args, **kwargs):
        super(ProgramWorker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    @pyqtSlot()
    def run(self):
        '''
        Run chosen function with given args and kwargs
        '''
        self.fn(*self.args, **self.kwargs)        


class WorkerSignals(QObject):

    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)


class Worker(QRunnable):

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        '''
        Run chosen function with given args and kwargs
        '''
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()    

