# coding=utf8

from PyQt4.QtGui import QCheckBox, QDialog, QGridLayout, QLabel, QPushButton
from PyQt4.QtCore import SIGNAL

class MultiselectionDialogBox(QDialog):
    
    def __init__(self, options, title, text, resultReceiver):
    	
        QDialog.__init__(self)
        self.options = options
        self.resultReceiver = resultReceiver
        
        self.resize(250, 60)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setSizeGripEnabled(False)
        label = QLabel(text)
        
        grid = QGridLayout()
        grid.setSpacing(10)
        
        grid.addWidget(label, 0, 0)
        
        self.checkBoxes = []
        
        position = 1
        for option in options:
            checkbox = QCheckBox(option)
            
            grid.addWidget(checkbox, position, 0)
            self.checkBoxes.append(checkbox)
            position += 1
        
        button = QPushButton('OK')
        
        button.clicked.connect(self.chooseOption)
        grid.addWidget(button, position, 0)
        
        self.setLayout(grid)
        self.show()
        
    def chooseOption(self):
        results = []
        for checkBox in self.checkBoxes:
            if checkBox.isChecked():
                results.append(str(checkBox.text()))
        
        self.resultReceiver(results)
        self.close()