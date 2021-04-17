import matplotlib
from matplotlib.dates import DateFormatter
from PySide2 import QtCore, QtWidgets, QtGui
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
matplotlib.use('Qt5Agg')


winTitle = 'WinSwitchCtr'


class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=200, height=800, dpi=900):
        self.parent = parent
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, occ_list=None, win_title='WinSwitchCtr', *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowIcon(QtGui.QIcon('src/icon.png'))
        self.setWindowTitle(win_title)
        self.canvas = MplCanvas(self, width=100, height=100, dpi=100)
        # setup window layout
        layout = QtWidgets.QHBoxLayout()

        # adding canvas to the layout
        layout.addWidget(self.canvas)

        # todo: add save and load graph features
        '''
        
        # adding button to the layout
        self.button = QtWidgets.QPushButton('Save')
        self.button.clicked.connect(occ_list.save_df_to_storage)
        layout.addWidget(self.button)
        
        '''

        # add session information to the layout
        self.sessionInformation = QtWidgets.QLabel()
        self.sessionInformation.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.sessionInformation.setAlignment(QtCore.Qt.AlignTop)
        self.sessionInformation.setStyleSheet('padding :15px')
        layout.addWidget(self.sessionInformation)

        # bundle all of these widgets into a single central widget
        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # get the occ list and update data
        self.occ_list = occ_list
        self.data = self.occ_list.get_occ_list()
        self.update_graph()

        # setup occ_list to trigger the graph redraw every switch
        self.occ_list.set_update_graph(self.update_graph)

        # setup a timer to trigger the stats redraw
        self.timer = QtCore.QTimer()
        self.timer.setInterval(250)  # redraws every quarter second (increase to reduce jerkyness when moving window)
        self.timer.timeout.connect(self.update_stats)
        self.timer.start()

    def update_stats(self):
        curr_ttl_cnt = self.occ_list.get_curr_cnt()
        curr_cnt_per_min = 0
        if curr_ttl_cnt != 0:
            curr_cnt_per_min = curr_ttl_cnt / self.occ_list.get_session_run_time_in_minutes()
        self.sessionInformation.setText('Statistics:\n This session:\n  Total number of switches:\n  %d\n\n  Switches '
                                        'per minute:\n   %f' % (curr_ttl_cnt, curr_cnt_per_min))

    def update_graph(self):
        # get and init data
        self.data = self.occ_list.get_occ_list()

        # clear the canvas
        self.canvas.axes.cla()
        top_lim = self.occ_list.get_max_cnt()
        bot_lim = 0
        top_padding = 1

        date_formatter = DateFormatter("%I:%M %p")
        # format y axis
        self.canvas.axes.set_ylim(bottom=bot_lim, top=top_lim + top_padding)
        self.canvas.axes.set_ylabel('Window switches per minute')
        self.canvas.axes.set_yticks(range(bot_lim, int(top_lim + 1)))

        # format x axis
        self.canvas.axes.set_xticks(self.data.index)
        self.canvas.axes.xaxis.set_major_formatter(date_formatter)
        self.canvas.axes.locator_params(axis='x', tight=True, nbins=16)
        self.canvas.axes.locator_params(axis='y', tight=True, nbins=29)

        # plot the data
        self.data.plot(ax=self.canvas.axes, grid=True, x_compat=True, style='o-g', legend=None)

        # trigger the canvas to update and redraw
        self.canvas.draw()

    # overrides show to fix edge case bug with window scaling
    def show(self):
        QtWidgets.QMainWindow.show(self)
        self.resize(1003, 620)
