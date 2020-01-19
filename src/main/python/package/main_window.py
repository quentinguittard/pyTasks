from PySide2 import QtWidgets, QtCore, QtGui

import package.api.task
import platform


COLORS = {False: (235, 64, 52), True: (160, 237, 83)}


class TaskItem(QtWidgets.QListWidgetItem):
    """This is a class to create a custom task item."""

    def __init__(self, name, done, list_widget):
        """The constructor of the custom task item.

        :param name: The name of the task.
        :param done: The status of the task.
        :param list_widget: The list widget containing all the tasks.
        :type name: str
        :type done: bool
        :type list_widget: QtWidgets.QListWidgetItem
        """
        super().__init__(name)

        self.list_widget = list_widget
        self.done = done
        self.name = name

        self.setSizeHint(QtCore.QSize(self.sizeHint().width(), 50))
        self.list_widget.addItem(self)
        self.set_background_color()

    def toggle_state(self):
        """Set the state of the task."""
        self.done = not self.done
        package.api.task.set_tasks_status(name=self.name, done=self.done)
        self.set_background_color()

    def set_background_color(self):
        """Define the style of the task item."""
        color = COLORS.get(self.done)
        self.setBackgroundColor(QtGui.QColor(*color))
        color_str = ",".join(map(str, color))
        stylesheet = f"""QListView::item:selected {{background: rgb({color_str});
                                                    color: rgb(0, 0, 0);}}"""
        self.list_widget.setStyleSheet(stylesheet)


class MainWindow(QtWidgets.QWidget):
    """This is a class to create the window of the application."""

    def __init__(self, ctx):
        """The constructor of the window.

        :param ctx: The context of the application.
        :type ctx: ApplicationContext
        """
        super().__init__()
        self.ctx = ctx
        self.setup_ui()
        self.get_tasks()
        self.center_under_tray()

    def setup_ui(self):
        """Setup the user interface of the application."""
        self.create_widgets()
        self.create_layouts()
        self.create_tray_icon()
        self.modify_widgets()
        self.add_widgets_to_layouts()
        self.setup_connections()

    def create_widgets(self):
        """Create the widgets of the application."""
        self.lw_tasks = QtWidgets.QListWidget()
        self.btn_add = QtWidgets.QPushButton()
        self.btn_clean = QtWidgets.QPushButton()
        self.btn_quit = QtWidgets.QPushButton()

    def create_tray_icon(self):
        self.tray = QtWidgets.QSystemTrayIcon()
        icon_path = self.ctx.get_resource("icon.png")
        self.tray.setIcon(QtGui.QIcon(icon_path))
        self.tray.setVisible(True)

    def modify_widgets(self):
        """Modify the style of the widgets."""
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.setStyleSheet("border: none;")
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)

        self.btn_add.setIcon(QtGui.QIcon(self.ctx.get_resource("add.svg")))
        self.btn_quit.setIcon(QtGui.QIcon(self.ctx.get_resource("close.svg")))
        self.btn_clean.setIcon(QtGui.QIcon(self.ctx.get_resource("clean.svg")))

        self.btn_add.setFixedSize(36, 36)
        self.btn_quit.setFixedSize(36, 36)
        self.btn_clean.setFixedSize(36, 36)

        self.lw_tasks.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.lw_tasks.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

    def create_layouts(self):
        """Create the layouts of the user interface."""
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.layout_buttons = QtWidgets.QHBoxLayout()

    def add_widgets_to_layouts(self):
        """Add created widgets to the user interface layout."""
        self.main_layout.addWidget(self.lw_tasks)
        self.main_layout.addLayout(self.layout_buttons)

        self.layout_buttons.addWidget(self.btn_add)
        self.layout_buttons.addStretch()
        self.layout_buttons.addWidget(self.btn_clean)
        self.layout_buttons.addWidget(self.btn_quit)

    def setup_connections(self):
        """Setup the connections."""
        self.btn_add.clicked.connect(self.add_task)
        self.btn_clean.clicked.connect(self.clean_task)
        self.btn_quit.clicked.connect(self.close)
        self.lw_tasks.itemClicked.connect(lambda lw_item: lw_item.toggle_state())
        self.tray.activated.connect(self.tray_icon_click)

    def add_task(self):
        """Add a task to the list."""
        task_name, ok = QtWidgets.QInputDialog.getText(self, "Add a task", "Task name:")
        if ok and task_name:
            package.api.task.add_task(name=task_name)
            self.get_tasks()

    def clean_task(self):
        """Clean the done tasks from the list."""
        for i in range(self.lw_tasks.count()):
            lw_item = self.lw_tasks.item(i)
            if lw_item.done:
                package.api.task.remove_task(name=lw_item.name)

        self.get_tasks()
        self.lw_tasks.repaint()

    def get_tasks(self):
        """Get all the saved tasks."""
        self.lw_tasks.clear()
        tasks = package.api.task.get_tasks()
        for task_name, done in tasks.items():
            TaskItem(name=task_name, done=done, list_widget=self.lw_tasks)

    def tray_icon_click(self):
        """Show or hide the tasks list."""
        if self.isHidden():
            self.showNormal()
        else:
            self.hide()

    def center_under_tray(self):
        """Center the tasks window under the tray for Unix and on the top for Windows."""
        tray_x = self.tray.geometry().x()
        tray_y = self.tray.geometry().y()
        w, h = self.sizeHint().toTuple()
        if platform.system() == "Windows":
            self.move(tray_x - (w * 0.5), tray_y - (h + 25))
        else:
            self.move(tray_x - (w * 0.5), 25)
