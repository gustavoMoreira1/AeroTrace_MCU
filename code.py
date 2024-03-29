# SDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# Simple GPS module demonstration.
# Will wait for a fix and print a message every second with the current location
# and other details.
import time
import board
import busio

import adafruit_gps

from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

ble = BLERadio()
ble.name = "Aerotrace1"
uart1 = UARTService()
advertisement = ProvideServicesAdvertisement(uart1)

connectonce = 0
# Create a serial connection for the GPS connection using default speed and\
# a slightly higher timeout (GPS modules typically update once a second).
# These are the defaults you should use for the GPS FeatherWing.
# For other boards set RX = GPS module TX, and TX = GPS module RX pins.
uart = busio.UART(board.D3, board.D2, baudrate=9600, timeout=10)

# for a computer, use the pyserial library for uart access
# import serial
# uart = serial.Serial("/dev/ttyUSB0", baudrate=9600, timeout=10)

# If using I2C, we'll create an I2C interface to talk to using default pins
# i2c = board.I2C()  # uses board.SCL and board.SDA
# i2c = board.STEMMA_I2C()  # For using the built-in

# Create a GPS module instance.
gps = adafruit_gps.GPS(uart, debug=False)  # Use UART/pyserial
# gps = adafruit_gps.GPS_GtopI2C(i2c, debug=False)  # Use I2C interface
def dilutionGrader():
    if gps.horizontal_dilution < 1:
        uart1.write("Dilution Grade: Ideal")
    elif gps.horizontal_dilution < 2:
        uart1.write("Dilution Grade: Excellent")
    elif gps.horizontal_dilution < 5:
        uart1.write("Dilution Grade: Good")
    elif gps.horizontal_dilution < 10:
        uart1.write("Dilution Grade: Moderate")
    elif gps.horizontal_dilution < 20:
        uart1.write("Dilution Grade: Fair")
    else:
        uart1.write("Dilution Grade: Poor")


# Initialize the GPS module by changing what data it sends and at what rate.
# These are NMEA extensions for PMTK_314_SET_NMEA_OUTPUT and
# PMTK_220_SET_NMEA_UPDATERATE but you can send anything from here to adjust
# the GPS module behavior:
#   https://cdn-shop.adafruit.com/datasheets/PMTK_A11.pdf

# Turn on the basic GGA and RMC info (what you typically want)
gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
# Turn on just minimum info (RMC only, location):
# gps.send_command(b'PMTK314,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
# Turn off everything:
# gps.send_command(b'PMTK314,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
# Turn on everything (not all of it is parsed!)
# gps.send_command(b'PMTK314,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0')

# Set update rate to once a second (1hz) which is what you typically want.
# gps.send_command(b"PMTK220,1000")
# Or decrease to once every two seconds by doubling the millisecond value.
# Be sure to also increase your UART timeout above!
# gps.send_command(b'PMTK220,2000')
# You can also speed up the rate, but don't go too fast or else you can lose
# data during parsing.  This would be twice a second (2hz, 500ms delay):
# gps.send_command(b"PMTK220,500")
# data during parsing.  This would be twice a second (8hz, 125ms delay):
# gps.send_command(b"PMTK220,125")
# data during parsing.  This would be twice a second (10hz, 100ms delay):
# 10 Hz is the maximum frequency... need to stress test for later -
# gps.send_command(b"PMTK220,100")
# data during parsing.  This would be twice a second (4hz, 250ms delay):
gps.send_command(b"PMTK220,250")


# Main loop runs forever printing the location, etc. every second.
last_print = time.monotonic()
count = 0
while True:
    # Make sure to call gps.update() every loop iteration and at least twice
    # as fast as data comes from the GPS unit (usually every second).
    # This returns a bool that's true if it parsed new data (you can ignore it
    # though if you don't care and instead look at the has_fix property).
    gps.update()
    last_time = 0
    # Every second print out current location details if there's a fix.
    current = time.monotonic()
    if current - last_print >= 0.250:
        last_print = current
        if not gps.has_fix:
            # Try again if we don't have a fix yet.
            current_time = time.time()
            count = count + 1
            if count == 4:
                count = 0
            print(f"Waiting for fix... {current_time} {count}")
            continue
        # We have a fix! (gps.has_fix is true)
        # Print out details about the fix like location, date, etc.

        ble.start_advertising(advertisement)
        print("Advertising...")
        while not ble.connected:
            pass
        while ble.connected:
            if connectonce == 0:
                print("connected")
                connectonce = 1
            uart1.write("========================================")
            # Print a separator line.

            uart1.write(
                "Fix timestamp: {}/{}/{} {:02}:{:02}:{:02}".format(
                    gps.timestamp_utc.tm_mon,  # Grab parts of the time from the
                    gps.timestamp_utc.tm_mday,  # struct_time object that holds
                    gps.timestamp_utc.tm_year,  # the fix time.  Note you might
                    gps.timestamp_utc.tm_hour - 6,  # not get all data like year, day,
                    gps.timestamp_utc.tm_min,  # month!
                    gps.timestamp_utc.tm_sec,
                    # gps.timestamp_utc[6]
                    # cannot find way to scape ms. Need to identify timestamp init code.
                    )
                )
            uart1.write("Raw Latitude: {0:.9f} degrees".format(gps.latitude))
            uart1.write("Raw Longitude: {0:.9f} degrees".format(gps.longitude))
        # print(f"DDM Latitude: {int(gps.latitude)} Degrees {60 *
        # (int(gps.latitude)-gps.latitude)} Minutes")
        # print(f"DDM Longitude: {int(gps.longitude)} Degrees {60 *
        # (int(gps.longitude)-gps.longitude)} Minutes")

        # print(
        #    "Precise Latitude: {:2.}{:2.4f} degrees".format(
        #        gps.latitude_degrees, gps.latitude_minutes
        #    )
        # )
        # print(
        #    "Precise Longitude: {:2.}{:2.4f} degrees".format(
        #        gps.longitude_degrees, gps.longitude_minutes
        #    )
        # )
            uart1.write("Fix quality: {}".format(gps.fix_quality))
        # Some attributes beyond latitude, longitude and timestamp are optional
        # and might not be present.  Check if they're None before trying to use!
            if gps.satellites is not None:
                uart1.write("# satellites: {}".format(gps.satellites))
            if gps.altitude_m is not None:
                uart1.write("Altitude: {} feet".format(gps.altitude_m * 3.28084))
            if gps.speed_knots is not None:
                uart1.write("Speed: {} miles/hour".format(gps.speed_knots * 1.15078))
            if gps.track_angle_deg is not None:
                uart1.write("Track angle: {} degrees".format(gps.track_angle_deg))
            if gps.horizontal_dilution is not None:
                uart1.write(f"Horizontal dilution: {gps.horizontal_dilution}")
                dilutionGrader()

            # print(f"Dilution Grade {dilutionGrader()}")
            # print(f"Horizontal dilution: {}".format(gps.horizontal_dilution))
        # if gps.height_geoid is not None:
        #    print("Height geoid: {} meters".format(gps.height_geoid))
