import sys, os, io
if hasattr(sys,'frozen'):
    os.environ['PATH']=sys._MEIPASS+';'+os.environ['PATH']
from PyQt5.QtWidgets import QApplication,QWidget,QLabel,QLineEdit,QPushButton,QListWidget,\
                            QVBoxLayout,QHBoxLayout,QGridLayout,\
                            QDialog,QFileDialog,QMessageBox,QAbstractItemView
from PyQt5.QtCore import Qt,QUrl
from PyQt5.QtGui import QIcon
from PyPDF2 import PdfFileMerger

def resource_path(relative_path):
    try:
        base_path=sys._MEIPASS
    except Exception:
        base_path=os.path.abspath('.')
    return os.path.join(base_path,relative_path)

class ListWidget(QListWidget):
    def __init__(self,parent=None):
        super().__init__(parent=None)
        self.setAcceptDrops(True)
        self.setStyleSheet('font-size:25px;')
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
    
    def dragEnterEvent(self,event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            return super().dragEnterEvent(event)

    def dragMoveEvent(self,event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            return super().dragMoveEvent(event)

    def dropEvent(self,event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()

            pdfFiles = []

            for url in event.mimeData().urls():
                if url.isLocalFile():
                    if url.toString().endswith('.pdf'):
                        pdfFiles.append(str(url.toLocalFile()))
            self.addItems(pdfFiles)
        else:
            return super().dropEvent(event)

class output_field(QLineEdit):
    def __init__(self):
        super().__init__()
        self.height=55
        self.setStyleSheet('font-size:30px;')
        self.setFixedHeight(self.height)
    
    def dragEnterEvent(self,event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self,event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()
    
    def dropEvent(self,event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()

            if event.mimeData().urls():
                self.setText(event.mimeData().urls()[0].toLocalFile())
            else:
                event.ignore()

class button(QPushButton):
    def __init__(self,label_text):
        super().__init__()
        self.setText(label_text)
        self.setStyleSheet('''
            font-size: 30px;
            width: 180px;
            height: 50px;
            ''')

class PDFApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('PDF File Merge Utility')
        self.setWindowIcon(QIcon(resource_path('PDF.ico')))
        self.resize(1800,800)
        self.initUI()

    def initUI(self):
        mainLayout= QVBoxLayout()
        outputFolderRow=QHBoxLayout()
        buttonLayout=QHBoxLayout()

        self.outputFile=output_field()
        outputFolderRow.addWidget(self.outputFile)

        self.buttonBrowseOutputFile=button('&Save To')
        self.buttonBrowseOutputFile.clicked.connect(self.populateFileName)
        outputFolderRow.addWidget(self.buttonBrowseOutputFile)

        #listbox widget
        self.pdfListWidget = ListWidget(self)

        #Buttons
        self.buttonDeleteSelect=button('&Delete')
        self.buttonDeleteSelect.clicked.connect(self.deleteSelected)
        buttonLayout.addWidget(self.buttonDeleteSelect, 1, Qt.AlignRight)

        self.buttonMerge=button('&Merge')
        self.buttonMerge.clicked.connect(self.mergeFile)
        buttonLayout.addWidget(self.buttonMerge)

        self.buttonClose=button('&Close')
        self.buttonClose.clicked.connect(QApplication.quit)
        buttonLayout.addWidget(self.buttonClose)

        self.buttonReset=button('&Reset')
        self.buttonReset.clicked.connect(self.clearQueue)
        buttonLayout.addWidget(self.buttonReset)

        mainLayout.addLayout(outputFolderRow)
        mainLayout.addWidget(self.pdfListWidget)
        mainLayout.addLayout(buttonLayout)
        self.setLayout(mainLayout)

    def deleteSelected(self):
        for item in self.pdfListWidget.selectedItems():
            self.pdfListWidget.takeItem(self.pdfListWidget.row(item))

    def clearQueue(self):
        self.pdfListWidget.clear()
        self.outputFile.setText('')
    
    def dialogMessage(self,message):
        dlg=QMessageBox(self)
        dlg.setWindowTitle('PDF Manager')
        dlg.setIcon(QMessageBox.Information)
        dlg.setText(message)
        dlg.show()

    def _getSaveFilePath(self):
        file_save_path, _ =QFileDialog.getSaveFileName(self,'Save PDF file',os.getcwd(),'PDF file (*.pdf)')
        return file_save_path

    def populateFileName(self):
        path=self._getSaveFilePath()
        if path:
            self.outputFile.setText(path)

    def mergeFile(self):
        if not self.outputFile.text():
            self.populateFileName()
            return
        
        if self.pdfListWidget.count()>0:
            pdfMerger=PdfFileMerger()

            try:
                for i in range(self.pdfListWidget.count()):
                    pdfMerger.append(self.pdfListWidget.item(i).text())

                pdfMerger.write(self.outputFile.text())
                # pdfMerger.close()

                # self.pdfListWidget.clear()
                self.dialogMessage('PDF Merge Complete')

            except Exception as e:
                self.dialogMessage(e)
        else:
            self.dialogMessage('Queue is empty')

app= QApplication(sys.argv)
app.setStyle('fusion')

pdfApp=PDFApp()
pdfApp.show()

sys.exit(app.exec_())