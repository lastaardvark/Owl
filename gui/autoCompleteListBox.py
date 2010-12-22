# coding=utf8

# Inspired by http://bit.ly/ggQQCM

from PyQt4.QtGui import QAbstractItemDelegate, QLineEdit, QListView
from PyQt4.QtCore import QAbstractListModel, QAbstractTableModel, QEvent, QModelIndex, Qt, QVariant, SIGNAL, SLOT

class AutoCompleteListBox:
    """
        This contains a QLineEdit and a QListView.
        
        The QListView is populated with the given data.
        When the text of QLineEdit changes, the QListView
        is filtered to keep only those containing a substring of
        the text. If QLineEdit is emptied, all data is returned to the
        QListView. 
    """
    
    class _ListModel(QAbstractListModel):
        """
            A list model that uses a list of tuples (x, y) where
            x is the string representation to show in the list, and 
            y is an object to store against it.
        """
        
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
        """
            Create the list box and line edit.
        """
        
        self.window = window
        self.listData = listData
    
        self.lineEdit = QLineEdit()
        self.listBox = QListView()
        
        self.listModel = self._ListModel(listData, window)
        self.listBox.setModel(self.listModel)
        
        self.window.connect(self.lineEdit, SIGNAL("textChanged(QString)"), self._OnTextChanged)
        
    def _OnTextChanged(self):
        """
            When self.lineEdit’s text has changed, use the new text to filter
            self.listData, and put the result in the list box.
        """
        
        if str(self.lineEdit.text()) == '':
            self.listModel.replaceList(self.listData)
            self.subList = self.listData
        else:
            pattern = str(self.lineEdit.text())
            self.subList = [item for item in self.listData if item[0].lower().find(pattern.lower()) >= 0]
            self.listModel.replaceList(self.subList)
                  
    def getLineEdit(self):
        """
            The QLineEdit object used to filter the list box.
        """
        
        return self.lineEdit
                
    def getListBox(self):
        """
            The QListView object
        """
        
        return self.listBox
    
    def replaceList(self, newList):
        """
            Replaces the data in the listbox with a new list.
        """
        
        self.subList = newList
        self.listData = newList
        self.listModel.replaceList(newList)
    
    def getSelectedItems(self):
        """
            Returns the objects associated with the selected list items.
        """
        
        if self.listBox.selectedIndexes():
            return [self.subList[index.row()][1] for index in self.listBox.selectedIndexes()]
        else:
            return None
    
def _StringIntersection(string1, string2):
    """
        Returns the largest common substring of two strings, anchored at the left.
    """
    
    newlist = []
    for i, j in zip(string1, string2):
        if i == j:
            newlist.append(i)
        else:
            break
    return ''.join(newlist)
