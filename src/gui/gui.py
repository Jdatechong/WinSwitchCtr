import sys

from PySide2 import QtWidgets, QtGui, QtCore

from src.gui.plot_graph import MainWindow

APPLICATION_NAME = "WinSwitchCtr"


class SystemTrayIcon(QtWidgets.QSystemTrayIcon):
    def __init__(self, icon, parent=None, occ_list=None):
        QtWidgets.QSystemTrayIcon.__init__(self, icon, parent)

        self.occ_list = occ_list
        # create main window object
        # must be created here or it gets gc'd for some reason
        self.main_window = MainWindow(occ_list, APPLICATION_NAME)

        # setup system tray properties and menu
        self.setToolTip(f'{APPLICATION_NAME}')
        self.menu = QtWidgets.QMenu(parent)

        # setup menu actions
        open_app = self.menu.addAction(f"Open {APPLICATION_NAME}")
        open_app.triggered.connect(self.on_open_main_window)
        self.menu.addSeparator()
        exit_ = self.menu.addAction("Exit")
        exit_.triggered.connect(lambda: sys.exit())

        self.setContextMenu(self.menu)

        # handles when icon is left clicked
        self.activated.connect(self.on_tray_icon_activated)

        # open main window
        self.on_open_main_window()

        # setup timer to update tooltip
        self.timer = QtCore.QTimer()
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.update_tooltip)
        self.timer.start()

    def on_tray_icon_activated(self, reason):
        # handles left clicks
        if reason == self.DoubleClick:
            self.on_open_main_window()
        if reason == self.Trigger:
            self.setContextMenu(self.menu)

    def on_open_main_window(self):
        self.main_window.show()
        self.main_window.setFocus()

    def update_tooltip(self):
        curr_ttl_cnt = self.occ_list.get_curr_cnt()
        curr_cnt_per_min = 0
        if curr_ttl_cnt != 0:
            curr_cnt_per_min = curr_ttl_cnt / self.occ_list.get_session_run_time_in_minutes()
        newToolTip = '{app_name}\nCount: {cnt}\nPer minute: {cnt_per_min}'. format(
            app_name=APPLICATION_NAME,
            cnt=curr_ttl_cnt,
            cnt_per_min=curr_cnt_per_min
        )
        self.setToolTip(newToolTip)


def main_gui(occ_list=None):
    app = QtWidgets.QApplication(sys.argv)
    # prevents app from quitting when main window is closed
    app.setQuitOnLastWindowClosed(False)
    w = QtWidgets.QWidget()

    tray_icon = SystemTrayIcon(QtGui.QIcon("src/icon.ico"), w, occ_list)
    tray_icon.show()
    sys.exit(app.exec_())
