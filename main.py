from PyQt5 import QtGui, QtCore, Qt, QtWidgets, QtSerialPort
from PyQt5.QtGui import QIntValidator, QIcon
from PyQt5.QtWidgets import *
import math


try:
    import Queue
except:
    import queue as Queue
import sys, time, serial
import struct
from pythonosc import udp_client
import socket
import os, sys, platform

#Printing to self
#https://stackoverflow.com/questions/8356336/how-to-capture-output-of-pythons-interpreter-and-show-in-a-text-widget
from PyQt5 import QtCore

class EmittingStream(QtCore.QObject):

    textWritten = QtCore.pyqtSignal(str)

    def write(self, text):
        self.textWritten.emit(str(text))

if platform.system() == "Windows":
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True) #enable highdpi scaling
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True) #use highdpi icons

#https://blog.aaronhktan.com/posts/2018/05/14/pyqt5-pyinstaller-executable
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

WIN_WIDTH, WIN_HEIGHT = 200, 600  # Window size
SER_TIMEOUT = 0.1  # Timeout for serial Rx
RETURN_CHAR = "\n"  # Char to be sent when Enter key pressed
PASTE_CHAR = "\x16"  # Ctrl code for clipboard paste
baudrate = 921600  # Default baud rate
# portname = "/dev/cu.SLAB_USBtoUART"  # Default port name
hexmode = True  # Flag to enable hex display
VERSION = "0.9"

class Dialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Dialog, self).__init__(parent)
        self.portname_comboBox = QtWidgets.QComboBox()
        # self.baudrate_comboBox = QtWidgets.QComboBox()

        for info in QtSerialPort.QSerialPortInfo.availablePorts():
            self.portname_comboBox.addItem(info.portName())

        # for baudrate in QtSerialPort.QSerialPortInfo.standardBaudRates():
        #     self.baudrate_comboBox.addItem(str(baudrate), baudrate)

        buttonBox = QtWidgets.QDialogButtonBox()
        buttonBox.setOrientation(QtCore.Qt.Horizontal)
        buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        lay = QtWidgets.QFormLayout(self)
        lay.addRow("Port Name:", self.portname_comboBox)
        # lay.addRow("BaudRate:", self.baudrate_comboBox)
        lay.addRow(buttonBox)
        self.setFixedSize(self.sizeHint())

    def get_results(self):
        return self.portname_comboBox.currentText()


# Main widget
class MyWidget(QWidget):

    def __init__(self, *args):
        QWidget.__init__(self, *args)
        sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)

        layout = QVBoxLayout()

        menubar = QMenuBar()
        layout.addWidget(menubar)
        self.logging = QAction("Show/Hide Log", self)
        self.logging.setShortcut("Ctrl+L")
        self.logging.triggered.connect(self.show_hide_logging)
        advancedMenu = menubar.addMenu("Advanced")
        advancedMenu.addAction(self.logging)


        ip_box = QFormLayout()

        self.port_readout = QLineEdit()
        self.port_readout.setEnabled(False)
        self.port_readout.setReadOnly(True)

        self.portname = None
        self.configure_btn = QPushButton("Select Serial Port")
        self.configure_btn.clicked.connect(self.open_dialog)

        self.ip_address_box = QLineEdit(socket.gethostbyname(socket.gethostname()))

        self.port_box = QLineEdit("1234")
        self.port_box.setValidator(QIntValidator())

        self.format_label = QLabel("Format Settings")

        self.ptr_cb = QComboBox()
        self.ptr_cb.addItems(["Raw Integers", "Cumulative Radians", "Finite Radians"])
        #tbd add connection here

        self.fiz_cb = QComboBox()
        self.fiz_cb.addItems(["Raw Integers", "Float"])
        # tbd add connection here

        ip_box.addWidget(QLabel("Serial Port Settings"))
        ip_box.addRow("Port", self.port_readout)
        ip_box.addWidget(self.configure_btn)
        ip_box.addWidget(QLabel("OSC Settings"))
        ip_box.addRow("IP Address", self.ip_address_box)
        ip_box.addRow("Port", self.port_box)
        ip_box.addWidget(self.format_label)
        ip_box.addRow("Pan/Tilt/Roll", self.ptr_cb)
        ip_box.addRow("Focus/Iris/Zoom", self.fiz_cb)



        self.start_button = QPushButton("Start")
        self.start_button.released.connect(self.start_communication)
        self.start_button.setEnabled(False)

        self.stop_button = QPushButton("Stop")
        self.stop_button.released.connect(self.stop_communication)
        self.stop_button.setEnabled(False)

        io_box = QGridLayout()

        self.pan_l = QLabel("Pan")
        self.pan_address = QLineEdit("/pan")
        self.pan_readout = QLineEdit()
        self.pan_readout.setReadOnly(True)
        self.pan_readout.setMaxLength(9)
        self.pan_enable = QCheckBox()
        self.pan_enable.setChecked(True)

        self.tilt_l = QLabel("Tilt")
        self.tilt_address = QLineEdit("/tilt")
        self.tilt_readout = QLineEdit()
        self.tilt_readout.setReadOnly(True)
        self.tilt_readout.setMaxLength(9)
        self.tilt_enable = QCheckBox()
        self.tilt_enable.setChecked(True)

        self.roll_l = QLabel("Roll")
        self.roll_address = QLineEdit("/roll")
        self.roll_readout = QLineEdit()
        self.roll_readout.setReadOnly(True)
        self.roll_readout.setMaxLength(9)
        self.roll_enable = QCheckBox()
        self.roll_enable.setChecked(True)

        self.c1_l = QLabel("Custom 1")
        self.c1_address = QLineEdit("/custom_1")
        self.c1_readout = QLineEdit()
        self.c1_readout.setReadOnly(True)
        self.c1_readout.setMaxLength(9)
        self.c1_enable = QCheckBox()
        self.c1_enable.setChecked(False)

        self.focus_l = QLabel("Focus")
        self.focus_address = QLineEdit("/focus")
        self.focus_readout = QLineEdit()
        self.focus_readout.setReadOnly(True)
        self.focus_readout.setMaxLength(9)
        self.focus_enable = QCheckBox()
        self.focus_enable.setChecked(False)

        self.iris_l = QLabel("Iris")
        self.iris_address = QLineEdit("/iris")
        self.iris_readout = QLineEdit()
        self.iris_readout.setReadOnly(True)
        self.iris_readout.setMaxLength(9)
        self.iris_enable = QCheckBox()
        self.iris_enable.setChecked(False)

        self.zoom_l = QLabel("Zoom")
        self.zoom_address = QLineEdit("/zoom")
        self.zoom_readout = QLineEdit()
        self.zoom_readout.setReadOnly(True)
        self.zoom_readout.setMaxLength(9)
        self.zoom_enable = QCheckBox()
        self.zoom_enable.setChecked(False)

        self.c2_l = QLabel("Custom 2")
        self.c2_address = QLineEdit("/custom_2")
        self.c2_readout = QLineEdit()
        self.c2_readout.setReadOnly(True)
        self.c2_readout.setMaxLength(9)
        self.c2_enable = QCheckBox()
        self.c2_enable.setChecked(False)

        row = 0
        io_box.addWidget(self.pan_l, row, 0)
        io_box.addWidget(self.pan_address, row, 1)
        io_box.addWidget(self.pan_readout, row, 2)
        io_box.addWidget(self.pan_enable, row, 3)

        row = row+1
        io_box.addWidget(self.tilt_l, row, 0)
        io_box.addWidget(self.tilt_address, row, 1)
        io_box.addWidget(self.tilt_readout, row, 2)
        io_box.addWidget(self.tilt_enable, row, 3)

        row = row+1
        io_box.addWidget(self.roll_l, row, 0)
        io_box.addWidget(self.roll_address, row, 1)
        io_box.addWidget(self.roll_readout, row, 2)
        io_box.addWidget(self.roll_enable, row, 3)

        # row = row+1
        # io_box.addWidget(self.c1_l, row, 0)
        # io_box.addWidget(self.c1_address, row, 1)
        # io_box.addWidget(self.c1_readout, row, 2)
        # io_box.addWidget(self.c1_enable, row, 3)

        row = row + 1
        io_box.addWidget(self.focus_l, row, 0)
        io_box.addWidget(self.focus_address, row, 1)
        io_box.addWidget(self.focus_readout, row, 2)
        io_box.addWidget(self.focus_enable, row, 3)

        row = row + 1
        io_box.addWidget(self.iris_l, row, 0)
        io_box.addWidget(self.iris_address, row, 1)
        io_box.addWidget(self.iris_readout, row, 2)
        io_box.addWidget(self.iris_enable, row, 3)

        row = row + 1
        io_box.addWidget(self.zoom_l, row, 0)
        io_box.addWidget(self.zoom_address, row, 1)
        io_box.addWidget(self.zoom_readout, row, 2)
        io_box.addWidget(self.zoom_enable, row, 3)

        # row = row + 1
        # io_box.addWidget(self.c2_l, row, 0)
        # io_box.addWidget(self.c2_address, row, 1)
        # io_box.addWidget(self.c2_readout, row, 2)
        # io_box.addWidget(self.c2_enable, row, 3)

        # status_box = QGridLayout()

        self.status_icon = QLabel("•")
        self.status_icon.setStyleSheet("color:yellow; font: 95pt;")
        self.status_icon.setAlignment(Qt.Qt.AlignCenter)
        self.status_text = QLabel("Standing by")
        self.status_text.setAlignment(Qt.Qt.AlignCenter)

        layout.addLayout(ip_box)
        # layout.addLayout(status_box)
        layout.addWidget(self.status_icon)
        layout.addWidget(self.status_text)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        layout.addLayout(io_box)

        self.log = QTextEdit()
        layout.addWidget(self.log)
        self.log.hide()

        self.setLayout(layout)
        self.resize(WIN_WIDTH, WIN_HEIGHT)  # Set window size

        self.log_toggled = False

    def show_hide_logging(self):
        if self.log_toggled:
            self.log_toggled = False
            self.log.hide()
        else:
            self.log_toggled = True
            self.log.show()

    def normalOutputWritten(self, text):
        """Append text to the QTextEdit."""
        # Maybe QTextEdit.append() works as well, but this is how I do it:
        cursor = self.log.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.log.setTextCursor(cursor)
        self.log.ensureCursorVisible()

    @QtCore.pyqtSlot()
    def open_dialog(self):
        dialog = Dialog()
        if dialog.exec_():
            self.portname = dialog.get_results()
            self.port_readout.setText(self.portname)
            self.start_button.setEnabled(True)
            self.start_button.repaint()
            self.port_readout.repaint()
            app.processEvents()

    def start_communication(self):
        ptrfiz_labels = [None] * 6
        ptrfiz_labels[0] = self.pan_address.text()
        ptrfiz_labels[1] = self.tilt_address.text()
        ptrfiz_labels[2] = self.roll_address.text()
        ptrfiz_labels[3] = self.focus_address.text()
        ptrfiz_labels[4] = self.iris_address.text()
        ptrfiz_labels[5] = self.zoom_address.text()
        ptrfiz_enables = [False] * 6
        ptrfiz_enables[0] = self.pan_enable.isChecked()
        ptrfiz_enables[1] = self.tilt_enable.isChecked()
        ptrfiz_enables[2] = self.roll_enable.isChecked()
        ptrfiz_enables[3] = self.focus_enable.isChecked()
        ptrfiz_enables[4] = self.iris_enable.isChecked()
        ptrfiz_enables[5] = self.zoom_enable.isChecked()
        ptr_format = self.ptr_cb.currentText()
        fiz_format = self.fiz_cb.currentText()
        self.serth = SerialThread(self.portname, baudrate, self.ip_address_box.text(), int(self.port_box.text()), ptrfiz_labels, ptrfiz_enables, ptr_format, fiz_format)  # Start serial thread
        self.serth.in_data.connect(self.incoming_data)
        self.serth.running_state.connect(self.update_state)
        self.serth.start()

    def stop_communication(self):
        if self.serth.running:
            self.serth.running = False
            self.serth.wait()
            self.toggleUI(True)

    def update_state(self, state):
        if state == "Active":
            self.status_icon.setStyleSheet("color: green; font:95pt")
            self.status_icon.repaint()
            self.status_text.setText("Serial/OSC Active")
            self.status_text.repaint()
            self.toggleUI(False)
        else:
            self.status_icon.setStyleSheet("color: red; font:95pt")
            self.status_icon.repaint()
            self.status_text.setText(state)
            self.status_text.repaint()
            self.toggleUI(True)
        # print(state)

    def incoming_data(self, in_data):  # Text display update handler
        self.pan_readout.setText(str(in_data[0]))
        self.tilt_readout.setText(str(in_data[1]))
        self.roll_readout.setText(str(in_data[2]))
        self.focus_readout.setText(str(in_data[3]))
        self.iris_readout.setText(str(in_data[4]))
        self.zoom_readout.setText(str(in_data[5]))

    def closeEvent(self, event):  # Window closing
        self.serth.running = False  # Wait until serial thread terminates
        self.serth.wait()

    def toggleUI(self, state):
        self.configure_btn.setEnabled(state)
        self.configure_btn.repaint()
        self.ip_address_box.setEnabled(state)
        self.ip_address_box.repaint()
        self.port_box.setEnabled(state)
        self.port_box.repaint()
        self.ptr_cb.setEnabled(state)
        self.ptr_cb.repaint()
        self.fiz_cb.setEnabled(state)
        self.fiz_cb.repaint()
        self.pan_address.setReadOnly(not state)
        self.pan_address.setEnabled(state)
        self.pan_address.repaint()
        self.pan_enable.setEnabled(state)
        self.pan_enable.repaint()
        self.tilt_address.setReadOnly(not state)
        self.tilt_address.setEnabled(state)
        self.tilt_address.repaint()
        self.tilt_enable.setEnabled(state)
        self.tilt_enable.repaint()
        self.roll_address.setReadOnly(not state)
        self.roll_address.setEnabled(state)
        self.roll_address.repaint()
        self.roll_enable.setEnabled(state)
        self.roll_enable.repaint()
        self.focus_address.setReadOnly(not state)
        self.focus_address.setEnabled(state)
        self.focus_address.repaint()
        self.focus_enable.setEnabled(state)
        self.focus_enable.repaint()
        self.iris_address.setReadOnly(not state)
        self.iris_address.setEnabled(state)
        self.iris_address.repaint()
        self.iris_enable.setEnabled(state)
        self.iris_enable.repaint()
        self.zoom_address.setReadOnly(not state)
        self.zoom_address.setEnabled(state)
        self.zoom_address.repaint()
        self.zoom_enable.setEnabled(state)
        self.zoom_enable.repaint()
        self.start_button.setEnabled(state)
        self.start_button.repaint()
        self.stop_button.setEnabled(not state)
        self.stop_button.repaint()
        app.processEvents()


# Thread to handle incoming &amp; outgoing serial data
class SerialThread(QtCore.QThread):
    in_data = QtCore.pyqtSignal(object)
    # aux_data = QtCore.pyqtSignal(object)
    running_state = QtCore.pyqtSignal(object)

    def __init__(self, serial_port, serial_baud, osc_ip, osc_port, ptrfiz_labels, ptrfiz_enables, ptr_format, fiz_format):  # Initialise with serial port details
        QtCore.QThread.__init__(self)
        self.serial_port, self.serial_baud, self.osc_ip, self.osc_port, self.ptrfiz_labels, self.ptrfiz_enables, self.ptr_format, self.fiz_format = serial_port, serial_baud, osc_ip, osc_port, ptrfiz_labels, ptrfiz_enables, ptr_format, fiz_format
        if platform.system() == "Windows":
            self.serial_port = self.serial_port
        else:
            self.serial_port = "/dev/" + self.serial_port
        self.running = True
        #these arrays hold the main data from the wheels
        self.ptrfiz_data_labels = ["pan", "tilt", "roll", "focus", "iris", "zoom"] #this is not used here, but helpful to remember
        self.ptrfiz_data_raw = [None] * 6
        self.ptrfiz_data_processed = [None] * 6

    def run(self):  # Run serial reader thread
        print("Opening Serial %s at %u baud" % (self.serial_port, self.serial_baud))
        print("Opening OSC %s :%u" % (self.osc_ip, self.osc_port))
        try:
            self.ser = serial.Serial(self.serial_port, self.serial_baud, timeout=SER_TIMEOUT)
            time.sleep(SER_TIMEOUT * 1.2)
            self.ser.flushInput()
            self.osc = udp_client.SimpleUDPClient(self.osc_ip, self.osc_port)
            self.running_state.emit("Active")
        except serial.SerialException as e:
            self.running_state.emit("Serial:Failure")
            print("Serial:Failure")
            self.ser = None
            self.osc = None
        except:
            self.running_state.emit("OSC:Failure")
            print("OSC:Failure")
            self.osc = None
            self.ser = None
        if not self.ser:
            print("Serial:Failure")
            self.running = False
        while self.running:
            self.ptrfiz_new = False
            try:
                s = self.ser.read_until(b';!;')         #read data from port
            except serial.SerialException as e:
                print("Serial:Failure")
                self.running_state.emit("Serial:Failure")
                self.running = False
            if s:                                   #if data
                fmt = '>cccccBBiiiiiHHHBBBBbbbbbbbbbbbbbbBBBBccc'  # this is the format of the packet data
                if len(s) == struct.calcsize(fmt):  # compare structure to length
                    self.data = list(struct.unpack(fmt, s))  # unpack
                    # the data is not parsed and ready to remap
                    self.ptrfiz_new = True  # mark new data
                    self.ptrfiz_data_raw[0] = self.data[7]  # pan
                    self.ptrfiz_data_raw[1] = self.data[8]  # tilt
                    self.ptrfiz_data_raw[2] = self.data[9]  # roll
                    self.ptrfiz_data_raw[3] = self.data[12]  # focus
                    self.ptrfiz_data_raw[4] = self.data[13]  # iris
                    self.ptrfiz_data_raw[5] = self.data[14]  # zoom
                    self.data[29] = self.data[29] - 128  # special: modify rssi data for formatting
                    self.data[30] = self.data[30] - 128  # special: modify snr data for formatting
                    #process the PTR data
                    if self.ptr_format == "Raw Integers":
                        self.ptrfiz_data_processed[0] = self.ptrfiz_data_raw[0] #raw
                        self.ptrfiz_data_processed[1] = self.ptrfiz_data_raw[1] #raw
                        self.ptrfiz_data_processed[2] = self.ptrfiz_data_raw[2] #raw
                    elif self.ptr_format == "Cumulative Radians":
                        self.ptrfiz_data_processed[0] = math.radians((self.ptrfiz_data_raw[0] / 1000))
                        self.ptrfiz_data_processed[1] = math.radians((self.ptrfiz_data_raw[1] / 1000))
                        self.ptrfiz_data_processed[2] = math.radians((self.ptrfiz_data_raw[2] / 1000))
                    elif self.ptr_format == "Finite Radians":
                        self.ptrfiz_data_processed[0] = math.radians((self.ptrfiz_data_raw[0] / 1000))
                        self.ptrfiz_data_processed[1] = math.radians((self.ptrfiz_data_raw[1] / 1000))
                        self.ptrfiz_data_processed[2] = math.radians((self.ptrfiz_data_raw[2] / 1000))
                        while self.ptrfiz_data_processed[0] > math.pi:
                            self.ptrfiz_data_processed[0] = self.ptrfiz_data_processed[0] - 2 * math.pi
                        while self.ptrfiz_data_processed[0] <= -math.pi:
                            self.ptrfiz_data_processed[0] = self.ptrfiz_data_processed[0] + 2 * math.pi
                        while self.ptrfiz_data_processed[1] > math.pi:
                            self.ptrfiz_data_processed[1] = self.ptrfiz_data_processed[1] - 2 * math.pi
                        while self.ptrfiz_data_processed[1] <= -math.pi:
                            self.ptrfiz_data_processed[1] = self.ptrfiz_data_processed[1] + 2 * math.pi
                        while self.ptrfiz_data_processed[2] > math.pi:
                            self.ptrfiz_data_processed[2] = self.ptrfiz_data_processed[0] - 2 * math.pi
                        while self.ptrfiz_data_processed[2] <= -math.pi:
                            self.ptrfiz_data_processed[2] = self.ptrfiz_data_processed[0] + 2 * math.pi
                    #process FIZ data
                    if self.fiz_format == "Raw Integers":
                        self.ptrfiz_data_processed[3] = self.ptrfiz_data_raw[3] #raw
                        self.ptrfiz_data_processed[4] = self.ptrfiz_data_raw[4] #raw
                        self.ptrfiz_data_processed[5] = self.ptrfiz_data_raw[5] #raw
                    if self.fiz_format == "Float":
                        self.ptrfiz_data_processed[3] = (self.ptrfiz_data_raw[3] / 65535) #raw
                        self.ptrfiz_data_processed[4] = (self.ptrfiz_data_raw[4] / 65535)#raw
                        self.ptrfiz_data_processed[5] = (self.ptrfiz_data_raw[5] / 65535) #raw

                    #output data
                    for num in range(len(self.ptrfiz_data_raw)):
                        if self.ptrfiz_enables[num]:            #if active, output
                            self.osc.send_message(self.ptrfiz_labels[num], self.ptrfiz_data_processed[num]) #send messages

                    #emit for UI thread
                    self.in_data.emit(self.ptrfiz_data_processed)

                else:
                    print("Error:"+str(len(s))+" vs "+str(struct.calcsize(fmt)))
                    #this issue is caused when the checksum = b';' and there are (b';;;;')

        if self.ser:  # Close serial port when thread finished
            self.running_state.emit("Stopped")
            self.ser.close()
            self.ser = None


if __name__ == "__main__":
    app = QApplication([])
    w = MyWidget()
    w.setWindowTitle('Inertia Wheels to OSC')
    if platform.system() == "Windows":
        app.setWindowIcon(QIcon(resource_path('icon.ico')))
        w.setWindowIcon(QIcon(resource_path('icon.ico')))
    else:
        app.setWindowIcon(QIcon(resource_path('icon.icns')))
        w.setWindowIcon(QIcon(resource_path('icon.icns')))
    w.show()
    sys.exit(app.exec_())
