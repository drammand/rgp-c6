import sys
import os
import platform
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtPrintSupport import *
import helpform
import newimagedlg
import qrc_resources

__version__ = "1.0.0"

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.image = QImage()
        self.dirty = False
        self.filename = None
        self.mirroredvertically = False
        self.mirroredhorizontally = False
        self.imageLabel = QLabel()
        self.imageLabel.setMinimumSize(200, 200)
        self.imageLabel.setAlignment(Qt.AlignCenter)
        self.imageLabel.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.setCentralWidget(self.imageLabel)

        logDockWidget = QDockWidget('Log', self)
        logDockWidget.setObjectName('LogDockWidget')
        logDockWidget.setAllowedAreas(Qt.LeftDockWidgetArea |
                                      Qt.RightDockWidgetArea)
        self.listWidget = QListWidget()
        logDockWidget.setWidget(self.listWidget)
        self.addDockWidget(Qt.RightDockWidgetArea, logDockWidget)

        self.printer = None

        self.sizeLabel = QLabel()
        self.sizeLabel.setFrameStyle(QFrame.StyledPanel|QFrame.Sunken)
        status = self.statusBar()
        status.setSizeGripEnabled(False)
        status.addPermanentWidget(self.sizeLabel)
        status.showMessage('Ready', 5000)

        fileNewAction = self.createAction("&New...", self.fileNew,
                                        QKeySequence.New, "filenew", "Create an image file")
        fileOpenAction = self.createAction("&Open...", self.fileOpen,
                                        QKeySequence.Open, "fileopen", "Open an existing image file")
        fileSaveAction = self.createAction("&Save", self.fileSave,
                                        QKeySequence.Save, "filesave", "Save the image")
        fileSaveAsAction = self.createAction("Save &As...", self.fileSaveAs, icon="filesaveas",
                                             tip="Save the image using a new name")
        filePrintAction = self.createAction("&Print", self.filePrint,
                                            QKeySequence.Print, "fileprint", "Print the image")
        fileQuitAction = self.createAction("&Quit", self.close,
                                            "Ctrl+Q", "filequit", "Close the application")
        editInvertAction = self.createAction("&Invert",self.editInvert, "Ctrl+I", "editinvert",
                                            "Invert the image's colors", True, "toggled(bool)")
        editSwapRedAndBlueAction = self.createAction(
                                            "Sw&ap Red and Blue", self.editSwapRedAndBlue,
                                            "Ctrl+A", "editswap",
                                            "Swap the image's red and blue color components",
                                            True, "toggled(bool)")
        editZoomAction = self.createAction("&Zoom...", self.editZoom,
                                            "Alt+Z", "editzoom", "Zoom the image")
        mirrorGroup = QActionGroup(self)
        editUnMirrorAction = self.createAction("&Unmirror",
                                               self.editUnMirror, "Ctrl+U", "editunmirror",
                                               "Unmirror the image", True, "toggled(bool)")
        mirrorGroup.addAction(editUnMirrorAction)
        editMirrorHorizontalAction = self.createAction(
                                            "Mirror &Horizontally", self.editMirrorHorizontal,
                                            "Ctrl+H", "editmirrorhoriz",
                                            "Horizontally mirror the image", True, "toggled(bool)")
        mirrorGroup.addAction(editMirrorHorizontalAction)
        editMirrorVerticalAction = self.createAction(
                                            "Mirror &Vertically", self.editMirrorVertical,
                                            "Ctrl+V", "editmirrorvert",
                                            "Vertically mirror the image", True, "toggled(bool)")
        mirrorGroup.addAction(editMirrorVerticalAction)
        editUnMirrorAction.setChecked(True)
        helpAboutAction = self.createAction("&About Image Changer",
                                            self.helpAbout)
        helpHelpAction = self.createAction("&Help", self.helpHelp,
                                           QKeySequence.HelpContents)

        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenuActions = (fileNewAction, fileOpenAction,
                                fileSaveAction, fileSaveAsAction, None,
                                filePrintAction, fileQuitAction)
        self.fileMenu.aboutToShow.connect(self.updateFileMenu)
        editMenu = self.menuBar().addMenu("&Edit")
        self.addActions(editMenu, (editInvertAction,
                                   editSwapRedAndBlueAction, editZoomAction))
        mirrorMenu = editMenu.addMenu(QIcon(":/editmirror.png"),
                                      "&Mirror")
        self.addActions(mirrorMenu, (editUnMirrorAction,
                                     editMirrorHorizontalAction, editMirrorVerticalAction))
        helpMenu = self.menuBar().addMenu("&Help")
        self.addActions(helpMenu, (helpAboutAction, helpHelpAction))

        fileToolbar = self.addToolBar("File")
        fileToolbar.setObjectName("FileToolBar")
        self.addActions(fileToolbar, (fileNewAction, fileOpenAction,
                                      fileSaveAsAction))
        editToolbar = self.addToolBar("Edit")
        editToolbar.setObjectName("EditToolBar")
        self.addActions(editToolbar, (editInvertAction,
                                      editSwapRedAndBlueAction, editUnMirrorAction,
                                      editMirrorVerticalAction,
                                      editMirrorHorizontalAction))
        self.zoomSpinBox = QSpinBox()
        self.zoomSpinBox.setRange(1, 400)
        self.zoomSpinBox.setSuffix(" %")
        self.zoomSpinBox.setValue(100)
        self.zoomSpinBox.setToolTip("Zoom the image")
        self.zoomSpinBox.setStatusTip(self.zoomSpinBox.toolTip())
        self.zoomSpinBox.setFocusPolicy(Qt.NoFocus)
        self.zoomSpinBox.valueChanged[int].connect(self.showImage)
        editToolbar.addWidget(self.zoomSpinBox)

        self.addActions(self.imageLabel, (editInvertAction,
                                          editSwapRedAndBlueAction, editUnMirrorAction,
                                          editMirrorVerticalAction, editMirrorHorizontalAction))

        self.resetableActions = ((editInvertAction, False),
                                 (editSwapRedAndBlueAction, False),
                                 (editUnMirrorAction, True))

        settings = QSettings()
        self.recentFiles = []
        if settings.value("RecentFiles"):
            self.recentFiles = settings.value('RecentFiles')
        size = settings.value("MainWindow/Size", QVariant(QSize(600, 500)))
        self.resize(size)
        position = settings.value("MainWindow/Position", QVariant(QPoint(0, 0)))
        self.move(position)
        if settings.value('MainWindow/State'):
            self.restoreState(QByteArray(settings.value("MainWindow/State")))

        self.setWindowTitle("Image Changer")
        self.updateFileMenu()
        QTimer.singleShot(0, self.loadInitialFile)

    def createAction(self, text, slot=None, shortcut=None, icon=None,
                     tip=None, checkable=False, signal='triggered'):
        action = QAction(text, self)
        if signal == 'triggered':
            actSignal = action.triggered
        elif signal == 'toggled':
            actSignal = action.toggled
        elif signal == 'hovered':
            actSignal = action.hovered
        elif signal == 'changed':
            actSignal = action.changed
        else:
            actSignal = action.triggered
        if icon is not None:
            action.setIcon(QIcon(':/%s.png' % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            actSignal.connect(slot)
        if checkable:
            action.setCheckable(True)
        return action

    def addActions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def closeEvent(self, event):
        if self.okToContinue():
            settings = QSettings()
            filename = QVariant(self.filename) \
                if self.filename is not None else QVariant()
            settings.setValue("LastFile", filename)
            recentFiles = QVariant(self.recentFiles) \
                if self.recentFiles else QVariant()
            settings.setValue("RecentFiles", recentFiles)
            settings.setValue("MainWindow/Size", QVariant(self.size()))
            settings.setValue("MainWindow/Position",
                              QVariant(self.pos()))
            settings.setValue("MainWindow/State",
                              QVariant(self.saveState()))
        else:
            event.ignore()

    def okToContinue(self):
        if self.dirty:
            reply = QMessageBox.question(self,
                                         "Image Changer - Unsaved Changes",
                                         "Save unsaved changes?",
                                         QMessageBox.Yes | QMessageBox.No |
                                         QMessageBox.Cancel)
            if reply == QMessageBox.Cancel:
                return False
            elif reply == QMessageBox.Yes:
                self.fileSave()
        return True

    def loadInitialFile(self):
        settings = QSettings()
        if settings.value('LastFile'):
            fname = settings.value("LastFile")
            if fname and QFile.exists(fname):
                self.loadFile(fname)

    def updateStatus(self, message):
        self.statusBar().showMessage(message, 5000)
        self.listWidget.addItem(message)
        if self.filename is not None:
            self.setWindowTitle("Image Changer - %s[*]" % \
                                os.path.basename(self.filename))
        elif not self.image.isNull():
            self.setWindowTitle("Image Changer - Unnamed[*]")
        else:
            self.setWindowTitle("Image Changer[*]")
        self.setWindowModified(self.dirty)

    def updateFileMenu(self):
        self.fileMenu.clear()
        self.addActions(self.fileMenu, self.fileMenuActions[:-1])
        current = self.filename \
            if self.filename is not None else None
        recentFiles = []
        for fname in self.recentFiles:
            if fname != current and QFile.exists(fname):
                recentFiles.append(fname)
        if recentFiles:
            self.fileMenu.addSeparator()
            for i, fname in enumerate(recentFiles):
                action = QAction(QIcon(":/icon.png"), "&{0}{1}".format(
                    i + 1, QFileInfo(fname).fileName()), self)
                action.setData(fname)
                action.triggered.connect(self.loadFile)
                self.fileMenu.addAction(action)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.fileMenuActions[-1])

    def fileNew(self):
        if not self.okToContinue():
            return
        dialog = newimagedlg.NewImageDlg(self)
        if dialog.exec_():
            self.addRecentFile(self.filename)
            self.image = QImage()
            for action, check in self.resetableActions:
                action.setChecked(check)
            self.image = dialog.image()
            self.filename = None
            self.dirty = True
            self.showImage()
            self.sizeLabel.setText("{0} x {1}".format(self.image.width(),
                                                self.image.height()))
            self.updateStatus("Created new image")

    def fileOpen(self):
        if not self.okToContinue():
            return
        dir = os.path.dirname(self.filename) \
            if self.filename is not None else "."
        formats = ["*.{0}".format(format.data().decode('ascii').lower()) \
                   for format in QImageReader.supportedImageFormats()]
        fname, ext = QFileDialog.getOpenFileName(self, "Image Changer - Choose Image", dir,
                                                  "Image files {0}".format(" ".join(formats)))
        if fname:
            self.loadFile(fname)

    def loadFile(self, fname=None):
        if fname is None:
            action = self.sender()
            if isinstance(action, QAction):
                fname = action.data().toString()
                if not self.okToContinue():
                    return
            else:
                return
        if fname:
            self.filename = None
            image = QImage(fname)
            if image.isNull():
                message = "Failed to read %s" % fname
            else:
                self.addRecentFile(fname)
                self.image = QImage()
                for action, check in self.resetableActions:
                    action.setChecked(check)
                self.image = image
                self.filename = fname
                self.showImage()
                self.dirty = False
                self.sizeLabel.setText("%d x %d" % (
                    image.width(), image.height()))
                message = "Loaded %s" % os.path.basename(fname)
            self.updateStatus(message)

    def addRecentFile(self, fname):
        if fname is None:
            return
        if fname not in self.recentFiles:
            self.recentFiles.insert(0, fname)
            if len(self.recentFiles) > 9:
                self.recentFiles = self.recentFiles[:9]

    def fileSave(self):
        if self.image.isNull():
            return
        if self.filename is None:
            self.fileSaveAs()
        else:
            if self.image.save(self.filename, None):
                self.updateStatus("Saved as %s" % self.filename)
                self.dirty = False
            else:
                self.updateStatus("Failed to save %s" % self.filename)

    def fileSaveAs(self):
        if self.image.isNull():
            return
        fname = self.filename if self.filename is not None else "."
        formats = ["*.%s" % format.lower() \
                   for format in QImageWriter.supportedImageFormats()]
        fname = QFileDialog.getSaveFileName(self,
                                                    "Image Changer - Save Image", fname,
                                                    "Image files (%s)" % " ".join(formats))
        if fname:
            if "." not in fname:
                fname += ".png"
            self.addRecentFile(fname)
            self.filename = fname
            self.fileSave()

    def filePrint(self):
        if self.image.isNull():
            return
        if self.printer is None:
            self.printer = QPrinter(QPrinter.HighResolution)
            self.printer.setPageSize(QPrinter.Letter)
        form = QPrintDialog(self.printer, self)
        if form.exec_():
            painter = QPainter(self.printer)
            rect = painter.viewport()
            size = self.image.size()
            size.scale(rect.size(), Qt.KeepAspectRatio)
            painter.setViewport(rect.x(), rect.y(), size.width(),
                                size.height())
            painter.drawImage(0, 0, self.image)

    def editInvert(self, on):
        if self.image.isNull():
            return
        self.image.invertPixels()
        self.showImage()
        self.dirty = True
        self.updateStatus("Inverted" if on else "Uninverted")

    def editSwapRedAndBlue(self, on):
        if self.image.isNull():
            return
        self.image = self.image.rgbSwapped()
        self.showImage()
        self.dirty = True
        self.updateStatus("Swapped Red and Blue" \
                              if on else "Unswapped Red and Blue")

    def editUnMirror(self, on):
        if self.image.isNull():
            return
        if self.mirroredhorizontally:
            self.editMirrorHorizontal(False)
        if self.mirroredvertically:
            self.editMirrorVertical(False)

    def editMirrorHorizontal(self, on):
        if self.image.isNull():
            return
        self.image = self.image.mirrored(True, False)
        self.showImage()
        self.mirroredhorizontally = not self.mirroredhorizontally
        self.dirty = True
        self.updateStatus("Mirrored Horizontally" \
                              if on else "Unmirrored Horizontally")

    def editMirrorVertical(self, on):
        if self.image.isNull():
            return
        self.image = self.image.mirrored(False, True)
        self.showImage()
        self.mirroredvertically = not self.mirroredvertically
        self.dirty = True
        self.updateStatus("Mirrored Vertically" \
                              if on else "Unmirrored Vertically")

    def editZoom(self):
        if self.image.isNull():
            return
        percent, ok = QInputDialog.getInt(self,
                                              "Image Changer - Zoom", "Percent:",
                                              self.zoomSpinBox.value(), 1, 400)
        if ok:
            self.zoomSpinBox.setValue(percent)

    def showImage(self, percent=None):
        if self.image.isNull():
            return
        if percent is None:
            percent = self.zoomSpinBox.value()
        factor = percent / 100.0
        width = self.image.width() * factor
        height = self.image.height() * factor
        image = self.image.scaled(width, height, Qt.KeepAspectRatio)
        self.imageLabel.setPixmap(QPixmap.fromImage(image))

    def helpAbout(self):
        QMessageBox.about(self, "About Image Changer",
                          """<b>Image Changer</b> v %s
                          <p>Copyright &copy; 2007 Qtrac Ltd. 
                          All rights reserved.
                          <p>This application can be used to perform
                          simple image manipulations.
                          <p>Python %s - Qt %s - PyQt %s on %s""" % (
                              __version__, platform.python_version(),
                              QT_VERSION_STR, PYQT_VERSION_STR, platform.system()))

    def helpHelp(self):
        form = helpform.HelpForm("index.html", self)
        form.show()


def main():
    app = QApplication(sys.argv)
    app.setOrganizationName("Qtrac Ltd.")
    app.setOrganizationDomain("qtrac.eu")
    app.setApplicationName("Image Changer")
    app.setWindowIcon(QIcon(":/icon.png"))
    form = MainWindow()
    form.show()
    app.exec_()


main()












