An Open-Source Motorcycle Cluster for Speedometer/Tachometer/Temperature

//June 6, 2022

The purpose of this project was that I had a 1998 Kawasaki KX250 2-Stroke dirt bike that was licensed for the street but in order to be safely operated on the street required several things, one of which was a speedometer.

Rather than purchasing an off the shelf solution which can be quite limited, I wanted to see if I could build my own solution from scratch which could not only be universal to gasoline motorcycles, but could easily be expanded on.

Moto-Cluster has a few physical components:

Tachometer/Temperature Circuit is comprised of: a. Arduino Nano b. Printed PCB to solder the Arduino, 555 timer, sparkplug capacitive pickup wire, thermistor and other components indicated in the Fritzing Schematic.

GPS Circuit is comprised of: a. Adafruit Ultimate GPS Breakout Module (note that #1 and #2 could be combined into a single unit if using a standalone PA1616D GPS module, a ATMega chip like the 1284P with two serial ports, for a single hardware unit for the motorcycle.

A future version potentially uses this and a bluetooth interface, which would replace the wired RPI/Screen with a Iphone or Android Device.

Raspberry Pi 4 running Raspbian Buster(will likely work with raspberry Pi 3 as well, maybe 2, not sure but have not tested) WILL NOT work with RPI Zero, as the UI needs threading support.

Pimoroni Hyperpixel 4 Capacitive touch screen display

3D printed Case to house everything

It also has a program written in Python using Tkinter which is the touchscreen UI for the cluster which runs on the Rapsberry Pi.

Once assembled, you will be able to get spark plug readings from capacitive coupling on the motorcycle, temperature readings from the coolant, and speed from the GPS, and have it display in real time on the Raspberry Pi display. The capabilities of this system could be greatly expanded with the existing sensors, but right now it focuses on the core functionality of a motorcycle cluster.

Python to run on Pi --> main.py

C running on Arduino Nano --> RPMTemperature_Sketch_Updated.ino

Fritzing Hardware Schematic for Arduino, and associated circuit for capacitive RPM pickup, Thermistor --> MotoCluster - Schematic and PCB.fzz

Case Design in Fusion 360 for 3D printing --> Cluster Case v3.f3d

Video Demo Link: https://youtube.com/shorts/iFWvjbjNgWQ
