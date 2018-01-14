from vispy import scene, app
import numpy as np
from PyQt4 import QtGui, QtCore
from vispy.scene.cameras import MagnifyCamera, Magnify1DCamera

class IMSHOW(QtGui.QWidget):
    def __init__(self, parent=None):
        self.canvas = scene.SceneCanvas(keys='interactive')
        self.canvas.size = 800, 600
        self.canvas.show()
        self.canvas._send_hover_events = True  # temporary workaround

        self.view = self.canvas.central_widget.add_view()
        self.view.camera = scene.PanZoomCamera(aspect=1)
        self.view.camera.flip = (0, 1, 0)
        self.image = scene.visuals.Image(interpolation='nearest', parent=self.view.scene, cmap= "viridis")

        @self.canvas.events.mouse_press.connect
        def mouse_press(event):
            x, y = self.get_position(event)
            return x,y

    def set_data(self,data):
        "Set the image to the widget"
        self.image.set_data(data)
        self.view.camera.set_range()

    def set_aspect(self, aspect):
        "Set the aspect of the image, similar to aspect in matplotlib"
        if self.magnify == True:
            if aspect == "auto":
                self.view.camera = MagnifyCamera(mag=1, size_factor=self.magnify_sizefactor , radius_ratio=self.magnify_radius_ratio)
                self.view.camera.set_range()
            elif aspect == "ratio":
                self.view.camera = MagnifyCamera(mag=1, size_factor=self.magnify_sizefactor, aspect=1, radius_ratio=self.magnify_radius_ratio)
                self.view.camera.set_range()
            else:
                print('I dunno this aspect, please use auto or ratio')
        else:
            if aspect == "auto":
                self.view.camera = scene.PanZoomCamera()
                self.view.camera.set_range()
            elif aspect == "ratio":
                self.view.camera = scene.PanZoomCamera(aspect=1)
                self.view.camera.set_range()
            else:
                print('I dunno this aspect, please use auto or ratio')

    def set_magnify(self,bool,size_factor=0.3,radius_ratio=0.7):
        if bool==True:
            self.view.camera = MagnifyCamera(mag=1, size_factor=size_factor, aspect=1, radius_ratio=radius_ratio)
            self.view.camera.set_range()
            self.magnify = True
            self.magnify_sizefactor = size_factor
            self.magnify_radius_ratio = radius_ratio

        # cbar_widget = scene.ColorBarWidget(cmap="viridis", orientation="right")
        # self.view.add_widget(cbar_widget)
        # cbar_widget.pos = (300, 100)

    def get_position(self,event):
        tr = self.view.node_transform(self.image) #problem here with the coordinate system
        x, y = tr.map(event.pos)[:2]
        return x,y


img_data = np.random.random((4000,125)).astype(np.float32)
alex = IMSHOW()
alex.set_data(img_data)
alex.set_magnify(True)
alex.set_aspect("ratio")
app.run()
