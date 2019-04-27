# -*- coding: utf-8 -*-
"""
Created on Sat Apr 27 16:13:55 2019

@author: Carol
"""
import numpy as np
import Fetch_Optic as opflow
import smbus
import pdb
import time as t


bus = smbus.SMBus(1)    # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)

MD25_ADDRESS12 = 0x58      #7 bit address (will be left shifted to add the read write bit)
MD25_ADDRESS34 = 0x59 
SOFTWARE_REG = 0x0D
CMD = 0x10
RESET_ENCODERS = 0x20
SPEED1 = 0X00
SPEED2 = 0X01
MODE_SELECTOR = 0X0F
ACCELERATION = 0X0E
VOLT_READ = 0X0A

bus.write_byte_data(MD25_ADDRESS12, MODE_SELECTOR, 1)
bus.write_byte_data(MD25_ADDRESS34, MODE_SELECTOR, 1)

def set_acceleration(x):
    bus.write_byte_data(MD25_ADDRESS12, ACCELERATION, x)
    t.sleep(0.05)
    bus.write_byte_data(MD25_ADDRESS34, ACCELERATION, x)
    print("acceleration set to %d" %(x))
    return

def get_current():
    c = bus.read_byte_data(MD25_ADDRESS12, 0x0B)
    c = c/10.0
    t.sleep(0.05)
    print("current = %dA" %(c))

def get_volt():
    volt58 = bus.read_byte_data(MD25_ADDRESS12, VOLT_READ)
    volt59 = bus.read_byte_data(MD25_ADDRESS34, VOLT_READ)
    volt58 = volt58/10.0
    volt59 = volt59/10.0
    
    print(volt58, volt59)
    if (volt58 < 11.0 or volt59 < 11.0):
        
        print("CHARGE BATTERY")
    
    return() 

def get_software():
    software58 = bus.read_byte_data(MD25_ADDRESS12, SOFTWARE_REG)
    t.sleep(0.05)
    software59 = bus.read_byte_data(MD25_ADDRESS34, SOFTWARE_REG)
    return(software58, software59)

def stop():
    bus.write_byte_data(MD25_ADDRESS12, SPEED1, 0)
    bus.write_byte_data(MD25_ADDRESS12, SPEED2, 0)
    bus.write_byte_data(MD25_ADDRESS34, SPEED1, 0)
    bus.write_byte_data(MD25_ADDRESS34, SPEED2, 0)
    return

def move(xp, yp, x2, y2):
    xe = x2 - xp
    ye = y2 - yp
    
    while((xe**2 + ye**2)**0.5 >= 5):
        Kp = 0.02
        Kd = 0.01
        Ki = 0.005
        
        x1 = opflow.fetch()[0] + xp
        y1 = opflow.fetch()[1] + yp
        
        xe = x2 - x1
        ye = y2 - y1
        
        xpe = 0.0
        ype = 0.0
        xes = 0.0
        yes = 0.0
        
        V = Kp * (xe ** 2 + ye ** 2) ** 0.5 + Kd * (xpe ** 2 + ype ** 2) ** 0.5 + Ki * (xes ** 2 + yes ** 2) ** 0.5
        V = 60 * max(min(1, V), 0)
        th = np.arctan((y2 - y1)/(x2 - x1))
        Vx = V * np.cos(th)
        Vy = V * np.sin(th)
        V1 = 0.5 * ((Vx/np.cos(np.pi/4)) + (Vy/np.sin(np.pi/4)))
        V3 = 0.5 * ((Vx/np.cos(np.pi/4)) + (Vy/np.sin(np.pi/4)))
        V2 = 0.5 * ((-Vx/np.cos(np.pi/4)) + (Vy/np.sin(np.pi/4)))
        V4 = 0.5 * ((-Vx/np.cos(np.pi/4)) + (Vy/np.sin(np.pi/4)))
        
        drive(V1, V2, V3, V4)
        
        xpe = xe
        ype = ye
        xes += xe
        yes += ye
    stop()
    return

def drive(V1, V2, V3, V4):
    
    bus.write_byte_data(MD25_ADDRESS12, SPEED1, int(V1))
    bus.write_byte_data(MD25_ADDRESS12, SPEED2, int(V3))
    bus.write_byte_data(MD25_ADDRESS34, SPEED1, -int(V2))
    bus.write_byte_data(MD25_ADDRESS34, SPEED2, -int(V4))
    
    return