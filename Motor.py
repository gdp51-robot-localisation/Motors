#!/usr/bin/python

import smbus
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

# Set up
bus.write_byte_data(MD25_ADDRESS12, MODE_SELECTOR, 1)
bus.write_byte_data(MD25_ADDRESS34, MODE_SELECTOR, 1)


def get_software():
    software58 = bus.read_byte_data(MD25_ADDRESS12, SOFTWARE_REG)
    software59 = bus.read_byte_data(MD25_ADDRESS34, SOFTWARE_REG)
    return(software58, software59)

def reset_Encoders():
    bus.write_byte_data(MD25_ADDRESS12, CMD, RESET_ENCODERS)
    bus.write_byte_data(MD25_ADDRESS34, CMD, RESET_ENCODERS)
    return

def encoder2():
    result = bus.read_i2c_block_data(MD25_ADDRESS12, 0x02, 11)
    max_int_32 = 2 ** 31
    
    encoder = (result[0] << 24) + (result[1] << 16) + \
               (result[2] << 8) + result[3]
    
    if encoder > max_int_32:
        encoder = -(2 ** 32 - encoder)
    
    encoder = encoder * 0.06109
    return(encoder)

def encoder1():
    result = bus.read_i2c_block_data(MD25_ADDRESS12, 0x02, 11)
    max_int_32 = 2 ** 31
    
    encoder = (result[4] << 24) + (result[5] << 16) + \
               (result[6] << 8) + result[7]
    
    if encoder > max_int_32:
        encoder = -(2 ** 32 - encoder)
    
    encoder = encoder * 0.06109
    return(encoder)

def encoder3():
    result = bus.read_i2c_block_data(MD25_ADDRESS34, 0x02, 11)
    max_int_32 = 2 ** 31
    
    encoder = (result[4] << 24) + (result[5] << 16) + \
               (result[6] << 8) + result[7]
    
    if encoder > max_int_32:
        encoder = -(2 ** 32 - encoder)
    
    encoder = encoder * 0.06109
    return(encoder)

def encoder4():
    result = bus.read_i2c_block_data(MD25_ADDRESS34, 0x02, 11)
    max_int_32 = 2 ** 31
    
    encoder = (result[0] << 24) + (result[1] << 16) + \
               (result[2] << 8) + result[3]
    
    if encoder > max_int_32:
        encoder = -(2 ** 32 - encoder)
    
    encoder = encoder * 0.06109
    return(encoder)

def drive(sp1, sp2, sp3, sp4, enc_dist):
    while (abs(encoder1()) < abs(enc_dist) and abs(encoder2()) < abs(enc_dist) and abs(encoder3()) < abs(enc_dist) and abs(encoder4()) < abs(enc_dist)):
        bus.write_byte_data(MD25_ADDRESS12, SPEED1, int(sp1))
        bus.write_byte_data(MD25_ADDRESS12, SPEED2, int(sp2))
        bus.write_byte_data(MD25_ADDRESS34, SPEED1, -int(sp3))
        bus.write_byte_data(MD25_ADDRESS34, SPEED2, -int(sp4))
    stop()
    reset_Encoders()
    t.sleep(0.05)
    return

def stop():
    bus.write_byte_data(MD25_ADDRESS12, SPEED1, 0)
    bus.write_byte_data(MD25_ADDRESS12, SPEED2, 0)
    bus.write_byte_data(MD25_ADDRESS34, SPEED1, 0)
    bus.write_byte_data(MD25_ADDRESS34, SPEED2, 0)
    return
    
def move(x, y, xpr, ypr, sp):
    x_dist = x - xpr
    y_dist = y - ypr
    
    if x_dist > 0:
        if y_dist > 0:
            if abs(x_dist) <= abs(y_dist):
                print("1")
                diag_dist = abs(x_dist * (2)**0.5)
                perp_dist = abs(y_dist) - abs(x_dist)
                print(perp_dist)
                drive(sp * (2)**0.5, sp * (2)**0.5, sp * (2)**0.5, sp * (2)**0.5, diag_dist * (2)**0.5)
                drive(0, 0, sp, sp, perp_dist)
            else:
                print("2")
                diag_dist = abs(y_dist * (2)**0.5)
                perp_dist = abs(x_dist) - abs(y_dist)
                
                drive(sp * (2)**0.5, sp * (2)**0.5, sp * (2)**0.5, sp * (2)**0.5, diag_dist * (2)**0.5)
                drive(sp, sp, 0, 0, perp_dist)
        elif y_dist < 0:
            if abs(x_dist) <= abs(y_dist):
                print("3")
                diag_dist = abs(x_dist * (2)**0.5)
                perp_dist = abs(y_dist) - abs(x_dist)
                
                drive(sp * (2)**0.5, sp * (2)**0.5, -sp * (2)**0.5, -sp * (2)**0.5, diag_dist * (2)**0.5)
                drive(0, 0, -sp, -sp, perp_dist)
            else:
                print("4")
                diag_dist = abs(y_dist * (2)**0.5)
                perp_dist = abs(x_dist) - abs(y_dist)
                print(perp_dist)
                drive(sp * (2)**0.5, sp * (2)**0.5, -sp * (2)**0.5, -sp * (2)**0.5, diag_dist * (2)**0.5)
                drive(sp, sp, 0, 0, perp_dist)
        else:
            print("5")
            drive(sp, sp, 0, 0, abs(x_dist))
    elif x_dist < 0:
        if y_dist > 0:
            if abs(x_dist) <= abs(y_dist):
                print("6")
                diag_dist = abs(x_dist * (2)**0.5)
                perp_dist = abs(y_dist) - abs(x_dist)
                
                drive(-sp * (2)**0.5, -sp * (2)**0.5, sp * (2)**0.5, sp * (2)**0.5, diag_dist * (2)**0.5)
                drive(0, 0, sp, sp, perp_dist)
            else:
                print("7")
                diag_dist = abs(y_dist * (2)**0.5)
                perp_dist = abs(x_dist) - abs(y_dist)
                
                drive(-sp * (2)**0.5, -sp * (2)**0.5, sp * (2)**0.5, sp * (2)**0.5, diag_dist * (2)**0.5)
                drive(-sp, -sp, 0, 0, perp_dist)
        elif y_dist < 0:
            if abs(x_dist) <= abs(y_dist):
                print("8")
                diag_dist = abs(x_dist * (2)**0.5)
                perp_dist = abs(y_dist) - abs(x_dist)
                
                drive(-sp * (2)**0.5, -sp * (2)**0.5, -sp * (2)**0.5, -sp * (2)**0.5, diag_dist * (2)**0.5)
                drive(0, 0, -sp, -sp, perp_dist)
            else:
                print("9")
                diag_dist = abs(y_dist * (2)**0.5)
                perp_dist = abs(x_dist) - abs(y_dist)
                
                drive(-sp * (2)**0.5, -sp * (2)**0.5, -sp * (2)**0.5, -sp * (2)**0.5, diag_dist * (2)**0.5)
                drive(-sp, -sp, 0, 0, perp_dist)
        else:
            print("10")
            drive(-sp, -sp, 0, 0, abs(x_dist))
    else:
        if y_dist > 0:
            drive(0, 0, sp, sp, abs(y_dist))
        else:
            drive(0, 0, -sp, -sp, abs(y_dist))
    return

reset_Encoders()
move(20, -60, 0, 0, 30)