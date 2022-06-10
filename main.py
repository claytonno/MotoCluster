import queue
import sys, serial, argparse
from tkinter import *
from PIL import ImageTk, Image
from time import sleep
from collections import deque
import time
import os
import numpy as np
from scipy import interpolate

from multiprocessing import Queue, Process
from queue import Empty

maxLen = 10
closeToken = False
# Uncomment below for operation on Raspberry Pi Zero

# arduinoAddr = '/dev/ttyUSB1'
# gpsAddr = '/dev/ttyUSB0'

# Uncomment below for Operation on Windows
arduinoAddr = 'COM3'
gpsAddr = 'COM4'


class SerialCom:
    def __init__(self, data_queue, devAddr, inBaudRate):
        self.data_q = data_queue
        self.devT = devAddr
        self.BaudR = inBaudRate
        self.ser = serial.Serial()

    def setup_serial(self):
        self.serial_port = self.devT
        print('Reading from serial port %s...' % self.devT)
        self.ser = serial.Serial(self.devT, self.BaudR)
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
        if self.devT == gpsAddr:
            # If our GPS Module then set updaterate to 10Hz and set to receive only RMC data line...
            self.ser.write(b'$PMTK314,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0*29\r\n')
            self.ser.flush()
            self.ser.write(b'$PMTK220,100*2F\r\n')
            self.ser.flush()
        if self.devT == arduinoAddr:
            # If our Arduino then reset DTR to avoid any garbage data
            self.ser.setDTR(False)
            time.sleep(1)
            self.ser.reset_input_buffer()
            self.ser.setDTR(True)

        time.sleep(2)  # wait for initialization

    def SerialWork(self):
        global closeToken
        self.setup_serial()
        while True:
            if self.ser.in_waiting() > 0:
                line = self.ser.readline()
                line = line.decode('utf8')
                data = line.split(',')
                self.data_q.put(data)
                if closeToken:
                    self.ser.close()
                    time.sleep(1)
                    return

    # clean up
    def close(self):
        # close serial
        self.ser.reset_input_buffer()
        self.ser.close()


# plot class
class SpeedoTachPlot:
    # constr
    def __init__(self, data_queue_gps, data_queue_arduino):

        # Calculate Temperature Coeffecient
        self.temps = np.array([20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170])  # temp
        self.resistances = np.array(
            [2031, 1286, 843.9, 569.9, 388, 277.8, 200, 146.7, 108, 82.7, 63.5, 49.3, 38.9, 30.4, 24.4,
             19.8])  # resistance

        self.resistances_rev = self.resistances[::-1]
        self.temps_rev = self.temps[::-1]
        self.interp_fit = interpolate.UnivariateSpline(self.resistances_rev, self.temps_rev, s=1)

        # open serial port
        self.NumberOfData_gps = 13
        self.NumberOfData_arduino = 6
        self.root = Tk()
        self.root.geometry("800x640")
        self.root.title = "Cluster"
        self.root.attributes('-fullscreen', True)
        # self.root.config(cursor="none")
        self.canvas = Canvas(
            self.root,
            height=480,
            width=800,
            bg="#666666"
        )
        self.canvas.config(highlightbackground="black")
        self.root.configure(bg="#666666")
        self.height = 400
        self.width = 750
        self.x = 15
        self.y = 100

        self.r = self.canvas.create_rectangle(self.x, self.y, self.x + self.width - self.width, self.y + self.height,
                                              fill='aqua',
                                              outline="aqua")
        self.rmax = self.canvas.create_rectangle(self.width + 200, self.y, self.width + 400, self.y + self.height,
                                                 fill='red',
                                                 outline="red")

        self.img = Image.open("ClusterVector.png")
        self.resized = self.img.resize((800, 480), Image.ANTIALIAS)
        self.img2 = ImageTk.PhotoImage(self.resized)
        self.canvas.create_image(0, 0, anchor=NW, image=self.img2)
        self.s = self.canvas.create_text(145, 145, fill="#666666", font=("ExcludedItalic", 100),
                                         text="0")
        self.temperature = self.canvas.create_text(645, 25, fill="#666666", font=("ExcludedItalic", 35),
                                                   text="0")

        self.canvas.pack(fill=BOTH, expand=1)

        Button(self.canvas, text="Quit", command=self.root.destroy).pack()

        self.canvas.pack(fill=BOTH, expand=1)

        self.data_q_gps = data_queue_gps
        self.data_q_arduino = data_queue_arduino

        self.databuf_gps = [deque() for i in range(self.NumberOfData_gps)]
        self.databuf_arduino = [deque() for i in range(self.NumberOfData_arduino)]

        self.t0 = time.time()
        self.t = deque([0.0] * maxLen)

        self.Speedometer = deque([0.0] * maxLen)
        self.RPM = deque([0.0] * maxLen)
        self.prevRPM = 0.0
        self.CoolantTemp = deque([0.0] * maxLen)
        self.Resistance = 0
        # show plot
        self.root.after(1, self.update)
        self.root.mainloop()

    # add to buffer
    def addtobuf(self, buf, val):
        if len(buf) < maxLen:
            buf.append(val)
        else:
            buf.pop()
            buf.appendleft(val)

    # add data
    def add(self, data, indatabuf, innumofdata):
        assert (len(data) == innumofdata)
        t = time.time() - self.t0
        # self.addtobuf(self.t, t, indatabuf)

        for i in range(innumofdata):
            self.addtobuf(indatabuf[i], data[i])

    # update plotaddToBuf
    def update(self):
        while not self.data_q_arduino.empty():
            data = self.data_q_arduino.get(False)
            if len(data) == self.NumberOfData_arduino:
                self.add(data, self.databuf_arduino, self.NumberOfData_arduino)
                out_data = self.databuf_arduino[4]
                if float(out_data[0]) == 0:
                    rpm1 = 0
                else:
                    rpm1 = int(60000000 / float(out_data[0]))
                # Average the RPM across the current pulse and the previous pulse
                rpm1 = (self.prevRPM + rpm1) / 2
                self.prevRPM = rpm1
                x0, y0, x1, y1 = self.canvas.coords(self.r)
                # 750 = max width of rectangle(below) and 10000 is the max rpm
                # so to get it to scale to the rectangle width we need to take RPM1 and multiply it by that factor
                x1 = x0 + (750 / 10000) * rpm1
                # print("{}{}".format('Engine Speed: ', rpm1))
                self.canvas.coords(self.r, x0, y0, x1, y1)
                if rpm1 >= 10000:
                    x0, y0, x1, y1 = self.canvas.coords(self.rmax)
                    x0 = self.width
                    self.canvas.coords(self.rmax, x0, y0, x1, y1)
                else:
                    x0, y0, x1, y1 = self.canvas.coords(self.rmax)
                    x0 = self.width + 200
                    self.canvas.coords(self.rmax, x0, y0, x1, y1)
                out_data = self.databuf_arduino[5]
                try:
                    TempResistance = float(out_data[0])
                except ValueError:
                    TempResistance = self.Resistance
                self.Resistance = TempResistance
                if TempResistance == 0:
                    self.canvas.itemconfig(self.temperature, text='>170')
                elif TempResistance > 2030:
                    self.canvas.itemconfig(self.temperature, text='<20')
                else:
                    finalTemp = int(self.interp_fit(TempResistance))
                    self.canvas.itemconfig(self.temperature, text=finalTemp)

        while not self.data_q_gps.empty():
            data = self.data_q_gps.get(False)
            if len(data) == self.NumberOfData_gps:
                self.add(data, self.databuf_gps, self.NumberOfData_gps)
                out_data = self.databuf_gps[7]
                # if float(out_data)>=1
                speed = int(float(out_data[0]) * 1.825)  # Speed in knots * 1.825 for KM/H
                if speed > 5:
                    self.canvas.itemconfig(self.s, text=speed)
                else:
                    self.canvas.itemconfig(self.s, text='0')
        data = None
        self.root.after(1, self.update)


# main() function
if __name__ == '__main__':

    data_q_arduino = Queue()
    data_q_gps = Queue()

    # Start our Two Serial Processes one for GPS one for Arduino
    serialcomarduino = SerialCom(data_q_arduino, arduinoAddr, 9600)
    serialcomgps = SerialCom(data_q_gps, gpsAddr, 9600)
    arduino_process = Process(target=serialcomarduino.SerialWork, args=())
    gps_process = Process(target=serialcomgps.SerialWork, args=())
    arduino_process.start()
    gps_process.start()

    # set up tk window
    if os.environ.get('DISPLAY', '') == '':
        print('no display found. Using :0.0')
        os.environ.__setitem__('DISPLAY', ':0.0')

    speedotachPlot = SpeedoTachPlot(data_q_gps, data_q_arduino)
    # show plot
    # clean up
    print('exiting.')
    closeToken = True
    arduino_process.kill()
    gps_process.kill()
    # speedotachPlot.close()
