# coding=utf8

# Inspired by http://bit.ly/ggQQCM

from PyQt4.QtGui import QAbstractItemDelegate, QLineEdit, QListView
from PyQt4.QtCore import QAbstractListModel, QAbstractTableModel, QEvent, QModelIndex, Qt, QVariant, SIGNAL, SLOT

class AutoCompleteListBox:
        
    class _LineEdit(QLineEdit):
        def __init__(self, *args):
            QLineEdit.__init__(self, *args)
            
        def event(self, event):
            if (event.type()==QEvent.KeyPress) and (event.key()==Qt.Key_Tab):
                self.emit(SIGNAL("tabPressed"))
                return True
            return QLineEdit.event(self, event)
    
    
    class _ListModel(QAbstractListModel): 
        def __init__(self, listData, parent=None, *args):         
            QAbstractTableModel.__init__(self, parent, *args) 
            self.listData = listData
     
        def rowCount(self, parent=QModelIndex()):
            if not self.listData:
                return 0
            return len(self.listData) 
     
        def data(self, index, role): 
            if index.isValid() and role == Qt.DisplayRole:
                return QVariant(self.listData[index.row()][0])
            else: 
                return QVariant()
    
        def replaceList(self, data):
            self.listData = data
            self.reset()
    
    def __init__(self, window, listData):
        self.window = window
        self.listData = listData
    
        self.lineEdit = self._LineEdit()
        self.listBox = QListView()
        
        self.listModel = self._ListModel(listData, window)
        self.listBox.setModel(self.listModel)
        
        self.window.connect(self.lineEdit, SIGNAL("textChanged(QString)"), self._OnTextChanged)
        
    def _OnTextChanged(self):
        if str(self.lineEdit.text()) == '':
            self.listModel.replaceList(self.listData)
            self.subList = []
        else:
            pattern = str(self.lineEdit.text())
            self.subList = [item for item in self.listData if item[0].lower().find(pattern.lower()) >= 0]
            self.listModel.replaceList(self.subList)
                  
    def getLineEdit(self):
        return self.lineEdit
                
    def getListBox(self):
        return self.listBox
    
    def replaceList(self, newList):
        self.subList = []
        self.listData = newList
        self.listModel.replaceList(newList)
    
    def getSelectedItem(self):
        return self.subList[self.listBox.currentItem()][1]
    
def _StringIntersection(string1, string2):
    """ The largest common substring of two strings, anchored at the left. """
    
    newlist = []
    for i, j in zip(string1, string2):
        if i == j:
            newlist.append(i)
        else:
            break
    return ''.join(newlist)
