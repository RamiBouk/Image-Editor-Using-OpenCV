import sys
import os
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage, QPalette
from PyQt6.QtWidgets import QLineEdit, QPushButton
from PyQt6.QtWidgets import (QApplication, QMainWindow,QLabel, QWidget, QSlider, QToolBar, QDockWidget, QMessageBox, QFileDialog, QGridLayout,
                             QScrollArea, )
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QPixmap, QImage,  QPalette, QAction

import matplotlib.pyplot as plt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

import numpy as np

from editor import MyEditor

icon_path= 'icons'
class ImageW(QLabel):
    def __init__(self) -> None:
        super(ImageW, self).__init__()
        self.brightness = 0
        self.contrast = 0
        editor=MyEditor()
        self.image= editor.getBuffer()
        height, width = self.image.shape[0:2]
        try:
            channel=self.image.shape[2]
        except Exception as e:
            print(e)
            pass
        bytesPerLine = 3 * width
        qImg = QImage(self.image.data, width, height,
                      bytesPerLine, QImage.Format.Format_BGR888)
        im = QPixmap(qImg)

        self.setPixmap(im)
        self.setScaledContents(True)

    def setState(self):
        self.image=MyEditor().getBuffer()
        height, width = self.image.shape[0:2]
        if len(self.image.shape)==3:
            bytesPerLine = 3 * width
            channel=self.image.shape[2]
            qImg = QImage(self.image.data, width, height,
                      bytesPerLine, QImage.Format.Format_BGR888)
        else:
            bytesPerLine = width
            qImg = QImage(self.image.data, width, height,
                      bytesPerLine, QImage.Format.Format_Grayscale8)
        im = QPixmap(qImg)

        self.setPixmap(im)





class PhotoEditorGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initializeUI()

        self.image = QImage()

    def setState(self):
        self.image_label.setState()
        self.plot()
        self.image_label.resize(
            self.zoom_factor * self.image_label.pixmap().size())

    def initializeUI(self):
        self.setMinimumSize(300, 200)
        self.setWindowTitle("Photo Editor")
        self.showMaximized()

        self.zoom_factor = 1
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)

        self.createMainLabel()
        #self.createEditingBar()
        self.createMenu()
        self.createToolBar()
        self.show()
        self.setState()

    def plot(self):

        # random datah
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        if(len(MyEditor().getBuffer().shape)==3):
            h_b = np.histogram(
                MyEditor().getBuffer()[:,:,0].flatten(),
                256,
                [0, 256])[0]
            h_g = np.histogram(
                MyEditor().getBuffer()[:,:,1].flatten(),
                256,
                [0, 256])[0]
            h_r= np.histogram(
                MyEditor().getBuffer()[:,:,2].flatten(),
                256,
                [0, 256])[0]
            ax.plot(h_b,'b')
            ax.plot(h_g,'g')
            ax.plot(h_r,'r')
        else:
            h, bin = np.histogram(
                MyEditor().getBuffer()[:,:].flatten(),
                256,
                [0, 256])
            ax.plot(h)
        self.canvas.draw()

    def openHistogram(self):
        try:
            self.removeDockWidget(self.editing_bar)
        except Exception as e:
            pass
        # TODO: Add a tab widget for the different editing tools
        self.histogram = QDockWidget("Histogram")
        self.histogram.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea & Qt.DockWidgetArea.RightDockWidgetArea)
        self.histogram.setMinimumWidth(240)
        self.histogram.setMinimumHeight(200)

        # Set layout for dock widget
        editing_grid = QGridLayout()
        editing_grid.addWidget(self.canvas,0,0,1,0)

        container = QWidget()
        container.setLayout(editing_grid)

        self.histogram.setWidget(container)
        self.histogram.show()



    def openBrighContrTools(self):
        try:
            self.removeDockWidget(self.editing_bar)
        except Exception as e:
            print("exception")
        # TODO: Add a tab widget for the different editing tools
        self.editing_bar = QDockWidget("Tools")
        self.editing_bar.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.editing_bar.setMinimumWidth(90)

        brightness_label = QLabel("Brightness")
        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setRange(-255, 255)
        self.brightness_slider.setTickInterval(35)
        self.brightness_slider.setTickPosition(QSlider.TickPosition.TicksAbove)
        self.brightness_slider.valueChanged.connect(
            self.changeBright)

        contrast_label = QLabel("Contrast")
        self.contrast_slider = QSlider(Qt.Orientation.Horizontal)
        self.contrast_slider.setRange(-100, 100)
        self.contrast_slider.setTickInterval(35)
        self.contrast_slider.setTickPosition(QSlider.TickPosition.TicksAbove)
        self.contrast_slider.valueChanged.connect(
            self.changeContrast)

        # Set layout for dock widget
        editing_grid = QGridLayout()
        editing_grid.addWidget(brightness_label, 1, 0)
        editing_grid.addWidget(self.brightness_slider, 4, 0, 1, 0)
        editing_grid.addWidget(contrast_label, 5, 0)
        editing_grid.addWidget(self.contrast_slider, 6, 0, 1, 0)
        editing_grid.setRowStretch(7, 10)

        container = QWidget()
        container.setLayout(editing_grid)

        self.editing_bar.setWidget(container)

        self.addDockWidget(
            Qt.DockWidgetArea.LeftDockWidgetArea, self.editing_bar)





    def openFilterTools(self):
        try:
            print
            self.removeDockWidget(self.editing_bar)
        except Exception as e:
            print("exception")
        # TODO: Add a tab widget for the different editing tools
        self.editing_bar = QDockWidget("Apply filters")
        self.editing_bar.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.editing_bar.setMinimumWidth(90)

        run_sobel = QPushButton("Sobel")
        run_sobel.clicked.connect(self.applySobel)

        run_Laplacian = QPushButton("Laplacian")
        run_Laplacian.clicked.connect(self.applyLaplacian)

        run_LoG = QPushButton("Laplacian of gaussian")
        run_LoG.clicked.connect(self.applyLoG)

        self.valuesp = QLineEdit()

        run_saltpepper = QPushButton("run")
        run_saltpepper.clicked.connect(self.applySaltPepper)

        self.valuegaussian_mean = QLineEdit()
        self.valuegaussian_variance = QLineEdit()
        self.valueMblur = QLineEdit()
        self.valueAblur = QLineEdit()
        self.value_seuil = QLineEdit()
        self.valuegblur = QLineEdit()
        run_bin = QPushButton("to binary")
        run_bin.clicked.connect(self.toBinary)

        run_gaussian = QPushButton("gaussian")
        run_gaussian.clicked.connect(self.applyGaussian)

        run_gblur = QPushButton("gaussian blur")
        run_gblur.clicked.connect(self.applyGblur)

        run_mblur = QPushButton("median blur")
        run_mblur.clicked.connect(self.applyMblur)

        run_ablur = QPushButton("average blur")
        run_ablur.clicked.connect(self.applyAblur)

        # Set layout for dock widget
        editing_grid = QGridLayout()
        label=QLabel('edge detection')
        label.setFixedHeight(20)
        editing_grid.addWidget(label, 1, 0)
        editing_grid.addWidget(run_sobel, 2, 0)
        editing_grid.addWidget(run_Laplacian, 3, 0)
        editing_grid.addWidget(run_LoG, 4, 0)
        label2=QLabel('salt pepper')
        label2.setFixedHeight(20)
        editing_grid.addWidget(label2, 5, 0)
        editing_grid.addWidget(self.valuesp, 6, 0)
        editing_grid.addWidget(run_saltpepper, 7, 0)
        label3=QLabel('Gaussian blur')
        label3.setFixedHeight(20)
        editing_grid.addWidget(label3, 8, 0)
        editing_grid.addWidget(self.valuegaussian_mean, 9, 0)
        editing_grid.addWidget(self.valuegaussian_variance, 10, 0)
        editing_grid.addWidget(run_gaussian, 11, 0)
        label4=QLabel('Thresholdig')
        label4.setFixedHeight(20)
        editing_grid.addWidget(label4, 12, 0)
        editing_grid.addWidget(self.value_seuil, 13, 0)
        editing_grid.addWidget(run_bin, 14, 0)
        label5=QLabel('Remove noise')
        label5.setFixedHeight(20)
        editing_grid.addWidget(label5, 15, 0)
        editing_grid.addWidget(self.valuegblur, 16, 0)
        editing_grid.addWidget(run_gblur, 17, 0)
        editing_grid.addWidget(self.valueMblur, 18, 0)
        editing_grid.addWidget(run_mblur, 19, 0)
        editing_grid.addWidget(self.valueAblur, 20, 0)
        editing_grid.addWidget(run_ablur, 21, 0)
        container = QWidget()
        container.setLayout(editing_grid)

        self.editing_bar.setWidget(container)

        self.addDockWidget(
            Qt.DockWidgetArea.LeftDockWidgetArea, self.editing_bar)





    def openImage(self):
        """Load a new image into the """
        image_file, _ = QFileDialog.getOpenFileName(self, "Open Image",
                                                    "", "PNG Files (*.png);;JPG Files (*.jpeg *.jpg );;Bitmap Files (*.bmp);;\
                GIF Files (*.gif)")
        print(image_file)

        if image_file:
            # Reset values when opening an image
            print(image_file)
            MyEditor().openImage(image_file)
            self.setState()

           #    Qt.KeepAspectRatio, Qt.SmoothTransformation))
        elif image_file == "":
            # User selected Cancel
            pass
        else:
            QMessageBox.information(self, "Error",
                                    "Unable to open image.", QMessageBox.Ok)

    def saveImage(self):
        """Save the image displayed in the label."""
        image_file, ext = QFileDialog.getSaveFileName(self, "Save Image",
                                                        "",
                                                        ".png;;.jpg;;.bmp;;\
                                                         .gif")
        MyEditor().saveFile(image_file+ext)




    def undo(self):
        MyEditor().undo()
        self.setState()

    def redo(self):
        MyEditor().redo()
        self.setState()

    def save(self):
        MyEditor().save()
        self.setState()

    def equalize(self):
        MyEditor().contrastEq()
        MyEditor().save()
        self.plot()
        self.setState()

    def rotate(self):
        MyEditor().rotate()
        MyEditor().save()
        self.image_label.resize(
            1 * self.image_label.pixmap().size())
        self.setState()

    def flipHorizontal(self):
        MyEditor().flipHorizontal()
        MyEditor().save()
        self.setState()

    def flipVertical(self):
        MyEditor().flipVerical()
        MyEditor().save()
        self.setState()

    def faceRecognize(self):
        MyEditor().face_recongnize()
        MyEditor().save()
        self.setState()

    def applySobel(self):
        MyEditor().applyFilter("Sobel")
        MyEditor().save()
        self.setState()

    def applyLaplacian(self):
        MyEditor().applyFilter("Laplacian")
        MyEditor().save()
        self.setState()

    def applyLoG(self):
        MyEditor().applyFilter("LoG")
        MyEditor().save()
        self.setState()

    def applySaltPepper(self):
        MyEditor().applyFilter("salt&pepper",[self.valuesp.text()])
        MyEditor().save()
        self.setState()

    def applyGaussian(self):
        MyEditor().applyFilter("gaussian",[self.valuegaussian_mean.text(),self.valuegaussian_variance.text()])
        MyEditor().save()
        self.setState()

    def applyGblur(self):
        MyEditor().applyFilter("gblur",[self.valuegblur.text()])
        MyEditor().save()
        self.setState()

    def applyMblur(self):
        MyEditor().applyFilter("mblur",[self.valueMblur.text()])
        MyEditor().save()
        self.setState()

    def applyAblur(self):
        MyEditor().applyFilter("ablur",[self.valueAblur.text()])
        MyEditor().save()
        self.setState()



    def rgb2gray(self):
        MyEditor().rgb2gray()
        MyEditor().save()
        self.setState()

    def toBinary(self):
        try:
            MyEditor().toBinary([self.value_seuil.text()])
        except:
            MyEditor().toBinary()
        MyEditor().save()
        self.setState()

    def createMenu(self):
        """Set up the menubar."""
        # Actions for Photo Editor menu
        about_act = QAction('About', self)
  #      about_act.triggered.connect(self.aboutDialog)

        self.exit_act = QAction(
            QIcon(os.path.join(icon_path, "exit.png")), 'Quit Photo Editor', self)
        self.exit_act.setShortcut('Ctrl+Q')
   #     self.exit_act.triggered.connect(self.close)

        # Actions for File menu
        self.new_act = QAction(
            QIcon(os.path.join(icon_path, "new.png")), 'New...')

        self.open_file = QAction(
            QIcon(os.path.join(icon_path, "open.png")), 'Open...', self)
        self.open_file.setShortcut('Ctrl+O')
        self.open_file.triggered.connect(self.openImage)

        self.open_bright = QAction(
            QIcon(os.path.join(icon_path, "brightness.png")), 'Brightness', self)
        self.open_bright.setShortcut('Ctrl+B')
        self.open_bright.triggered.connect(self.openBrighContrTools)

        self.rgb2gray_act = QAction(
            QIcon(os.path.join(icon_path, "grayscale.png")), 'To Gray', self)
        self.rgb2gray_act.triggered.connect(self.rgb2gray)

        self.open_filters = QAction(
            QIcon(os.path.join(icon_path, "filter.png")), 'Filters', self)
        self.open_filters.setShortcut('Ctrl+f')
        self.open_filters.triggered.connect(self.openFilterTools)

        self.undo_act = QAction(
            QIcon(os.path.join(icon_path, "undo.png")), "Undo", self)
        self.undo_act.setShortcut('Ctrl+U')
        self.undo_act.triggered.connect(self.undo)

        self.redo_act = QAction(
            QIcon(os.path.join(icon_path, "redo.png")), "Redo", self)
        self.redo_act.setShortcut('Ctrl+R')
        self.redo_act.triggered.connect(self.redo)

        self.save_act = QAction(
            QIcon(os.path.join(icon_path, "save.png")), "Save", self)
        self.save_act.setShortcut('Ctrl+S')
        self.save_act.triggered.connect(self.saveImage)

        self.equalize_act = QAction(
            QIcon(os.path.join(icon_path, "flatten.png")), "Equalize", self)
        self.equalize_act.triggered.connect(self.equalize)


        self.rotate_act = QAction(
            QIcon(os.path.join(icon_path, "rotate90_cw.png")), 'Rotate', self)
        self.rotate_act.triggered.connect(self.rotate)

        self.flip_horizontal = QAction(
            QIcon(os.path.join(icon_path, "flip_horizontal.png")), 'Flip Horizontal', self)
        self.flip_horizontal.triggered.connect(self.flipHorizontal)

        self.flip_vertical = QAction(
            QIcon(os.path.join(icon_path, "flip_vertical.png")), 'Flip Vertical', self)
        self.flip_vertical.triggered.connect(
             self.flipVertical)

        self.face_recongnize = QAction(
                QIcon(os.path.join(icon_path, "rec.jpg")), 'Face Recognize', self)
        self.face_recongnize.triggered.connect(
             self.faceRecognize)

        self.bi_act = QAction(
            QIcon(os.path.join(icon_path, "binary.png")), "To BW", self)
        self.bi_act.triggered.connect(self.toBinary)

        # Actions for Edit menu
        self.zoom_in_act = QAction(
            QIcon(os.path.join(icon_path, "zoom_in.png")), 'Zoom In', self)
        self.zoom_in_act.setShortcut('Ctrl++')
        self.zoom_in_act.triggered.connect(lambda: self.zoomOnImage(1.25))
        self.zoom_in_act.setEnabled(True)

        self.zoom_out_act = QAction(
            QIcon(os.path.join(icon_path, "zoom_out.png")), 'Zoom Out', self)
        self.zoom_out_act.setShortcut('Ctrl+-')
        self.zoom_out_act.triggered.connect(lambda: self.zoomOnImage(0.8))
        self.zoom_out_act.setEnabled(True)

        self.normal_size_Act = QAction("Normal Size", self)
        self.normal_size_Act.setShortcut('Ctrl+=')
        self.normal_size_Act.setEnabled(False)


        # Create menubar
        menu_bar = self.menuBar()
        menu_bar.setNativeMenuBar(False)

        # Create Photo Editor menu and add actions

        tool_menu = menu_bar.addMenu('')
        tool_menu.addAction(self.flip_horizontal)
        tool_menu.addAction(self.flip_vertical)
        tool_menu.addAction(self.zoom_in_act)
        tool_menu.addAction(self.zoom_out_act)
        tool_menu.addAction(self.bi_act)
        self.openHistogram()

    def createToolBar(self):
        """Set up the toolbar."""
        tool_bar = QToolBar("Main Toolbar")
        tool_bar.setIconSize(QSize(26, 26))
        self.addToolBar(tool_bar)

        # Add actions to the toolbar
        tool_bar.addAction(self.open_file)
        tool_bar.addAction(self.open_filters)
        tool_bar.addAction(self.open_bright)
        tool_bar.addAction(self.equalize_act)
        tool_bar.addAction(self.rgb2gray_act)
        tool_bar.addAction(self.face_recongnize)
        tool_bar.addSeparator()
        tool_bar.addAction(self.bi_act)
        tool_bar.addAction(self.rotate_act)
        tool_bar.addAction(self.flip_horizontal)
        tool_bar.addAction(self.flip_vertical)
        tool_bar.addSeparator()
        tool_bar.addSeparator()
        tool_bar.addSeparator()
        tool_bar.addAction(self.zoom_in_act)
        tool_bar.addAction(self.zoom_out_act)
        tool_bar.addSeparator()
        tool_bar.addSeparator()
        tool_bar.addSeparator()
        tool_bar.addAction(self.undo_act)
        tool_bar.addAction(self.redo_act)
        tool_bar.addSeparator()
        tool_bar.addSeparator()
        tool_bar.addSeparator()
        tool_bar.addAction(self.save_act)

    def createMainLabel(self):
        """Create an instance of the imageLabel class and set it 
           as the main window's central widget."""
        self.image_label = ImageW()
        self.image_label.resize(self.image_label.pixmap().size())

        self.scroll_area = QScrollArea()
        self.scroll_area.setBackgroundRole(QPalette.ColorRole.Dark)
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.scroll_area.setWidget(self.image_label)

        self.setCentralWidget(self.scroll_area)


    def updateActions(self):
        """Update the values of menu and toolbar items when an image 
        is loaded."""
        self.save_act.setEnabled(True)
        self.revert_act.setEnabled(True)
        self.zoom_in_act.setEnabled(True)
        self.zoom_out_act.setEnabled(True)
        self.normal_size_Act.setEnabled(True)
        self.bi_act.setEnabled(True)

    def zoomOnImage(self, zoom_value):
        """Zoom in and zoom out."""
        self.zoom_factor *= zoom_value
        self.image_label.resize(
            self.zoom_factor * self.image_label.pixmap().size())

        self.adjustScrollBar(
            self.scroll_area.horizontalScrollBar(), zoom_value)
        self.adjustScrollBar(self.scroll_area.verticalScrollBar(), zoom_value)

        self.zoom_in_act.setEnabled(self.zoom_factor < 4.0)
        self.zoom_out_act.setEnabled(self.zoom_factor > 0.333)

    def normalSize(self):
        """View image with its normal dimensions."""
        self.image_label.adjustSize()
        self.zoom_factor = 1.0

    def adjustScrollBar(self, scroll_bar, value):
        """Adjust the scrollbar when zooming in or out."""
        scroll_bar.setValue(int(value * scroll_bar.value()) +
                            int((value - 1) * scroll_bar.pageStep()/2))

    def aboutDialog(self):
        QMessageBox.about(self, "About Photo Editor",
                          "Photo Editor\nVersion 0.2\n\nCreated by Joshua Willman")

    def keyPressEvent(self, event):
        """Handle key press events."""
        pass


    def changeBright(self,brightness):
        MyEditor().changeBright(brightness)
        self.setState()

    def changeContrast(self,contrast):
        MyEditor().changeContr(contrast)
        self.setState()



if __name__ == '__main__':
    MyEditor().openImage("./images/default.png")
    app = QApplication(sys.argv)
    mainWindow = PhotoEditorGUI()
    mainWindow.show()
    app.exec()
