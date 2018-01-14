from PyQt4 import QtGui, QtCore
from vispy import gloo, app, scene
from vispy.scene import visuals
import numpy as np


class ControlPanel(QtGui.QWidget):
    """
    Widget for editing OBJECT parameters
    """
    signal_objet_changed = QtCore.pyqtSignal(name='objectChanged')

    def __init__(self, parent=None):
        super(ControlPanel, self).__init__(parent)

        self.coord = QtGui.QLabel("0, 0")

        l_cmap = QtGui.QLabel("Cmap ")
        self.cmap = ["lol","lel"]
        # self.cmap = list(get_colormaps().keys())
        self.combo = QtGui.QComboBox(self)
        self.combo.addItems(self.cmap)
        self.combo.currentIndexChanged.connect(self.update_param)

        gbox = QtGui.QGridLayout()
        gbox.addWidget(l_cmap, 0, 0)
        gbox.addWidget(self.combo, 0, 1)
        gbox.addWidget(self.coord, 1, 0)

        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(gbox)
        vbox.addStretch(1.0)

        self.setLayout(vbox)

    def update_param(self, option):
        self.signal_objet_changed.emit()


class scatter(QtGui.QMainWindow):

    def __init__(self, pos, mfc=[0.5,0.5,0.5,0.8], mec=None, mfs=8, mes=1, bgc=[1,1,1],
                scaling_symbol = False, symbol = 'disc', size = (800,600)):
        QtGui.QMainWindow.__init__(self)
        # Create the windows
        self.resize(size[0],size[1]+50)
        self.setWindowTitle("FullControl Alchemist")
        # Create the scatter
        self.canvas = Scatter2DCanvas(pos, mfc=mfc, mec=mec, mfs=mfs, mes=mes, bgc=bgc,
                    scaling_symbol = scaling_symbol, symbol = symbol, size = size)
        self.canvas.create_native()
        self.canvas.native.setParent(self)
        # Create the control panel
        self.control = ControlPanel()

        splitter = QtGui.QSplitter(QtCore.Qt.Vertical)
        splitter.addWidget(self.canvas.native)
        splitter.addWidget(self.control)

        @self.canvas.events.mouse_move.connect
        def change_coord(event):
            if (0.0001<abs(self.canvas.movexy[0])<10000) or (0.0001<abs(self.canvas.movexy[1])<10000):
                self.control.coord.setText(str(np.around(self.canvas.movexy[0],3)) + ", " + str(np.around(self.canvas.movexy[1],3)))
            else :
                self.control.coord.setText(str('%.3e' % self.canvas.movexy[0]) + ", " + str('%.3e' % self.canvas.movexy[1]))

        self.setCentralWidget(splitter)


class Scatter2DCanvas(scene.SceneCanvas):

    def __init__(self, pos, mfc=[0.5,0.5,0.5,0.8], mec=None, mfs=8, mes=1, bgc=[1,1,1],
                scaling_symbol = False, symbol = 'disc', size = (800,600)):
        scene.SceneCanvas.__init__(self, keys=None, show=True, bgcolor=bgc, size=size)
        self.unfreeze()  # allow the creation of new attribute to the class
            # Create the view and the scatter
        self.view = self.central_widget.add_view()
        self.scatter = visuals.Markers(parent=self.view.scene)
        self.scatter.set_data(pos, face_color=mfc, edge_color=mec, scaling = scaling_symbol, size=mfs, edge_width=mes, symbol=symbol)
            # Set the camera properties
        self.view.camera = scene.PanZoomCamera(aspect=1)
        self.view.camera.set_range()
            # Settings for the lines that indicate the position of the cursor
        self.param_tickprop = .01
        self.pressxy = (0,0)
        self.movexy = (0,0)
        tr = self.scene.node_transform(self.scatter)
        win_xmin, win_ymax = tr.map([0,0])[:2]
        win_xmax, win_ymin = tr.map(self.size)[:2]
        win_xsize, win_ysize = win_xmax-win_xmin, win_ymax-win_ymin
        tick_size = self.param_tickprop*win_xsize
            # Create the lines on the border of the viewbox
        self.top_line = scene.visuals.Line(pos=np.array([[win_xmin,win_ymax],[win_xmin,win_ymax-tick_size]]), color=[.2,.2,.2,0.5], width=1, parent = self.view.scene, method='gl')
        self.right_line = scene.visuals.Line(pos=np.array([[win_xmax,win_ymin],[win_xmax-tick_size,win_ymin]]), color=[.2,.2,.2,0.5], width=1, parent = self.view.scene, method='gl')
        self.bottom_line = scene.visuals.Line(pos=np.array([[win_xmax,win_ymin],[win_xmax,win_ymin+tick_size]]), color=[.2,.2,.2,0.5], width=1, parent = self.view.scene, method='gl')
        self.left_line = scene.visuals.Line(pos=np.array([[win_xmin,win_ymax],[win_xmin+tick_size,win_ymax]]), color=[.2,.2,.2,0.5], width=1, parent = self.view.scene, method='gl')
        # Create the cross on the cursor coord
        self.cross_hline = scene.visuals.Line(pos=np.array([[win_xmax,win_ymin],[win_xmax,win_ymin+tick_size]]), color=[0,0,0,1], width=2, parent = self.view.scene, method='gl')
        self.cross_vline = scene.visuals.Line(pos=np.array([[win_xmin,win_ymax],[win_xmin+tick_size,win_ymax]]), color=[0,0,0,1], width=2, parent = self.view.scene, method='gl')
        self.freeze()

        @self.events.mouse_move.connect
        def on_mouse_move(event):
            # Find the cursor position in the windows coordinate
            tr = self.scene.node_transform(self.scatter)
            x, y = tr.map(event.pos)[:2]
            self.movexy = (x,y)
            # Find the min and max for both axis in the windows coordinate
            win_xmin, win_ymax = tr.map([0,0])[:2]
            win_xmax, win_ymin = tr.map(self.size)[:2]
            win_xsize, win_ysize = win_xmax-win_xmin, win_ymax-win_ymin
            tick_size = self.param_tickprop*win_xsize
            #refresh lines
            self.top_line.set_data(pos=np.array([[x,win_ymax],[x,win_ymax-tick_size]]))
            self.right_line.set_data(pos=np.array([[win_xmax,y],[win_xmax-tick_size,y]]))
            self.bottom_line.set_data(pos=np.array([[x,win_ymin],[x,win_ymin+tick_size]]))
            self.left_line.set_data(pos=np.array([[win_xmin,y],[win_xmin+tick_size,y]]))

            self.cross_hline.set_data(pos=np.array([[x-tick_size/2,y],[x+tick_size/2,y]]))
            self.cross_vline.set_data(pos=np.array([[x,y-tick_size/2],[x,y+tick_size/2]]))

        @self.events.mouse_press.connect
        def on_mouse_press(event):
            # Find the cursor position in the windows coordinate
            tr = self.scene.node_transform(self.scatter)
            x, y = tr.map(event.pos)[:2]
            self.pressxy = (x,y)

    def set_data(self, pos, mfc=[0.5,0.5,0.5,0.8], mec=None, mfs=8, mes=1, scaling_symbol=False, symbol = 'disc'):
            self.scatter.set_data(pos, face_color=mfc, edge_color=mec, scaling = scaling_symbol, size=mfs, edge_width=mes, symbol=symbol)
            return self

if __name__ == '__main__':
    appQt = QtGui.QApplication([])
    win = scatter(np.random.random((200,2))*100)
    win.show()
    appQt.exec_()
    #
    # a=Scatter2DCanvas(np.random.random((20,2))*100)
    # app.run()
