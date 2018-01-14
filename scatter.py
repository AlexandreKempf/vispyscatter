from vispy import gloo, app, scene
from vispy.scene import visuals
import numpy as np


def scatter(pos, mfc=[0.5,0.5,0.5,0.8], mec=None, mfs=8, mes=1, bgc=[0.9,0.9,0.9],
            scaling = False, symbol = 'disc'):
    """ Display a scatter plot in 2D or 3D.

    Parameters
    ----------
    pos : array
        The array of locations to display each symbol.
    mfc : Color | ColorArray
        The color used to draw each symbol interior.
    mec : Color | ColorArray
        The color used to draw each symbol outline.
    mfs : float or array
        The symbol size in px.
    mes : float | None
        The width of the symbol outline in pixels.
    bgc : Color
        The color used for the background.
    scaling : bool
        If set to True, marker scales when rezooming.
    symbol : str
        The style of symbol to draw ('disc', 'arrow', 'ring', 'clobber',
        'square', 'diamond', 'vbar', 'hbar', 'cross', 'tailed_arrow', 'x',
        'triangle_up', 'triangle_down', 'star').
    """
    # Create the Canvas, the Scene and the View
    canvas = scene.SceneCanvas(keys='interactive', show=True, bgcolor=bgc)
    view = canvas.central_widget.add_view()
    # Create the scatter plot
    scatter = visuals.Markers()
    scatter.set_data(pos, face_color=mfc, edge_color=mec, scaling = scaling, size=mfs, edge_width=mes, symbol=symbol)
    view.add(scatter)

    # 2D Shape
    if pos.shape[1] == 2:
        # Set the camera properties
        view.camera = scene.PanZoomCamera(aspect=1)
        view.camera.set_range()
        # Create lines to know the position of the cursor
        tr = canvas.scene.node_transform(scatter)
        win_xmin, win_ymax = tr.map([0,0])[:2]
        win_xmax, win_ymin = tr.map(canvas.size)[:2]
        win_xsize, win_ysize = win_xmax-win_xmin, win_ymax-win_ymin
        prop = .015
        tick_size = prop*win_xsize
        top_line = scene.visuals.Line(pos=np.array([[win_xmin,win_ymax],[win_xmin,win_ymax-tick_size]]), color=[.2,.2,.2,0.5], width=1, parent = view.scene, method='gl')
        right_line = scene.visuals.Line(pos=np.array([[win_xmax,win_ymin],[win_xmax-tick_size,win_ymin]]), color=[.2,.2,.2,0.5], width=1, parent = view.scene, method='gl')
        bottom_line = scene.visuals.Line(pos=np.array([[win_xmax,win_ymin],[win_xmax,win_ymin+tick_size]]), color=[.2,.2,.2,0.5], width=1, parent = view.scene, method='gl')
        left_line = scene.visuals.Line(pos=np.array([[win_xmin,win_ymax],[win_xmin+tick_size,win_ymax]]), color=[.2,.2,.2,0.5], width=1, parent = view.scene, method='gl')

        cross_hline = scene.visuals.Line(pos=np.array([[win_xmax,win_ymin],[win_xmax,win_ymin+tick_size]]), color=[0,0,0,1], width=2, parent = view.scene, method='gl')
        cross_vline = scene.visuals.Line(pos=np.array([[win_xmin,win_ymax],[win_xmin+tick_size,win_ymax]]), color=[0,0,0,1], width=2, parent = view.scene, method='gl')

        # TODO: create rectangle around the text
        # Create text to give cursor position
        text_xline = visuals.Text('', bold=False, font_size=12, color=[0,0,0,1],
                    pos=[50,50], anchor_x='left', anchor_y='baseline')
        text_yline = visuals.Text('', bold=False, font_size=12, color=[0,0,0,1],
                    pos=[50,50], anchor_x='left', anchor_y='baseline')

        view.add(text_xline)
        view.add(text_yline)

        # When the mouse move, refresh the cursor position
        @canvas.events.mouse_move.connect
        def on_mouse_move(event):
            # Find the cursor position in the windows coordinate
            tr = canvas.scene.node_transform(scatter)
            x, y = tr.map(event.pos)[:2]
            # Find the min and max for both axis in the windows coordinate
            win_xmin, win_ymax = tr.map([0,0])[:2]
            win_xmax, win_ymin = tr.map(canvas.size)[:2]
            win_xsize, win_ysize = win_xmax-win_xmin, win_ymax-win_ymin
            tick_size = prop*win_xsize
            #refresh
            xtext, ytext = str('%.2e' % x),str('%.2e' % y)
            text_xline.text = xtext
            text_xline.pos = [x,win_ymin]
            text_yline.text = ytext
            text_yline.pos = [win_xmin,y]

            top_line.set_data(pos=np.array([[x,win_ymax],[x,win_ymax-tick_size]]))
            right_line.set_data(pos=np.array([[win_xmax,y],[win_xmax-tick_size,y]]))
            bottom_line.set_data(pos=np.array([[x,win_ymin],[x,win_ymin+tick_size]]))
            left_line.set_data(pos=np.array([[win_xmin,y],[win_xmin+tick_size,y]]))

            cross_hline.set_data(pos=np.array([[x-tick_size/2,y],[x+tick_size/2,y]]))
            cross_vline.set_data(pos=np.array([[x,y-tick_size/2],[x,y+tick_size/2]]))

    # 3D Shape
    elif pos.shape[1] == 3:
        view.camera = 'turntable'

    app.run()


# # Examples :
scatter( np.random.random((500000,2))*100 )
# scatter( np.random.random((1000,3)) )
# scatter( np.random.random((1000,3)), mfc = [1,0,0,1], mfs = 10 )
# scatter( np.random.random((1000,3)), mfc = np.random.random((10000,4)), mfs = 10 )
# scatter( np.random.random((1000,3)), mfc = np.random.random((10000,4)), mfs = np.random.random(10000) )
# scatter( np.random.random((1000,2)), symbol = 'square' )
# scatter( np.random.random((1000,2)), bgc = [0,0,0] )
