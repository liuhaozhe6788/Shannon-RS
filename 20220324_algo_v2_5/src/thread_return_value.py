import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import time


class WorkerSignals(QObject):
    progress = pyqtSignal(int)


class Worker(QRunnable):

    def __init__(self):
        super(Worker, self).__init__()
        self.signals = WorkerSignals()

    def run(self):
        total_n = 1000
        for n in range(total_n):
            progress_pc = int(100*float(n)/total_n)
            self.signals.progress.emit(progress_pc)
            time.sleep(0.01)


class MainWindow(QMainWindow):

    def __init__(self, *args, **kargs):
        super(MainWindow, self).__init__(*args, **kargs)

        layout = QVBoxLayout()

        self.bar = QProgressBar()

        button = QPushButton("START IT UP")
        button.pressed.connect(self.execute)

        layout.addWidget(self.bar)
        layout.addWidget(button)

        w = QWidget()
        w.setLayout(layout)

        self.setCentralWidget(w)

        self.show()

        self.threadpool = QThreadPool()

    def execute(self):
        worker = Worker()
        worker.signals.progress.connect(self.update_progress)

        self.threadpool.start(worker)

    def update_progress(self, progress):
        self.bar.setValue(progress)


app = QApplication(sys.argv)
window = MainWindow()
app.exec_()