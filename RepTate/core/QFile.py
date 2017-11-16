from PyQt5.QtGui import *
from PyQt5.QtWidgets import QTreeWidgetItem
#from Table import *

class QFile(QTreeWidgetItem):
    """ Each item of a dataset is a wrapper of the QTreeWidgetItem
        It contains the necessary tables and types
    """
    series=0

    def __init__(self, parent=None):
        QTreeWidgetItem.__init__(self, parent)

    def __init__(self, parent=None, itemlist=[], type=0):
        QTreeWidgetItem.__init__(self, parent, itemlist, type)

    def __init__(self, parent=None, itemlist=[], type=0, file_name_short="dummy", file_type=None):
        QTreeWidgetItem.__init__(self, parent, itemlist, type)
        # self.file_name_short = file_name_short
        #Table.__init__(self, file_name_short, file_type)

    def __lt__(self, otherItem):
        column = self.treeWidget().sortColumn()
        try:
            return float( self.text(column) ) > float( otherItem.text(column) )
        except ValueError:
            return self.text(column) > otherItem.text(column)



