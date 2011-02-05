# coding=utf8

from PyQt4.QtGui import QDialog, QGridLayout, QLabel, QPushButton
from PyQt4.QtCore import SIGNAL

class DialogBox(QDialog):
    
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
        
        grid.addWidget(label, 0, 0, 1, len(options))
        
        position = 0
        for option in options:
            button = QPushButton(option)
            receiver = lambda item = option: self.chooseOption(item)
            self.connect(button, SIGNAL('clicked()'), receiver)
            
            grid.addWidget(button, 1, position)
            position += 1
        
        self.setLayout(grid)
        self.show()
        
    def chooseOption(self, option):
        self.resultReceiver(option)
        self.close()