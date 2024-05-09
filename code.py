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
ble.name = "Aerotrace5"
uart1 = UARTService()
advertisement = ProvideServicesAdvertisement(uart1)

connectonce = 0
# Create a serial connection for the GPS connection using default speed and\
# a slightly higher timeout (GPS modules typically update once a second).
# These are the defaults you should use for the GPS FeatherWing.
# For other boards set RX = GPS module TX, and TX = GPS module RX pins.
uart = busio.UART(board.D2, board.D1, baudrate=9600, timeout=10)

# for a computer, use the pyserial library for uart access
# import serial
# uart = serial.Serial("/dev/ttyUSB0", baudrate=9600, timeout=10)

# If using I2C, we'll create an I2C interface to talk to using default pins
# i2c = board.I2C()  # uses board.SCL and board.SDA
# i2c = board.STEMMA_I2C()  # For using the built-in

# Create a GPS module instance.
gps = adafruit_gps.GPS(uart, debug=False)  # Use UART/pyserial
# gps = adafruit_gps.GPS_GtopI2C(i2c, debug=False)  # Use I2C interface

disconnected_BLE = False
# this flag is used to indicate when the BLE disconnects.


# def dilutionGrader():
# if gps.horizontal_dilution < 1:
# return "Dilution Grade: Ideal"
# elif gps.horizontal_dilution < 2:
# return "Dilution Grade: Excellent"
# elif gps.horizontal_dilution < 5:
# return "Dilution Grade: Good"
# elif gps.horizontal_dilution < 10:
# return "Dilution Grade: Moderate"
# elif gps.horizontal_dilution < 20:
# return "Dilution Grade: Fair"
# else:
# return "Dilution Grade: Poor"


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

# here is the frequency, do not let it go over 10!!
frequency_hertz = 8

frequency_conversion = int(1 / frequency_hertz * 1000)  # AKA miliseconds
gps_send_command = "PMTK220," + str(frequency_conversion)
# print(gps_send_command)
# gps.send_command(b"PMTK220,250")

# experimental gps.senc_command
gps.send_command(bytes(gps_send_command, "ascii"))

# Main loop runs forever printing the location, etc. every second.
last_print = time.monotonic()
count = 0

# array of data when discconected
disconnected_data = []
disconnected_counter = 0

advertise_counter = 0

save_once = 0

while True:

    last_time = 0
    # Every second print out current location details if there's a fix.
    current = time.monotonic()
    if current - last_print >= (frequency_conversion / 1000):
        last_print = current
        # if not gps.has_fix:
        #     # Try again if we don't have a fix yet.
        #     count = count + 1
        #     if count == frequency_hertz:
        #         count = 0
        #     print(f"Waiting for fix... {time.time()} {count}")
        #     continue
        # We have a fix! (gps.has_fix is true)
        # Print out details about the fix like location, date, etc.
        if advertise_counter == 0:
            ble.start_advertising(advertisement)
            print("Advertising...")
            advertise_counter = 1
        while not ble.connected and not disconnected_BLE:
            # print("Got to here")
            pass

        if not ble.connected and disconnected_BLE and save_once == 0:
            print("got to here")
            while disconnected_counter <= 10 * frequency_hertz:
                print(f"Iteration: {disconnected_counter}/{10 * frequency_hertz}")
                disconnected_counter = disconnected_counter + 1
                """disconnected_data.append(
                    "{}/{}/{} {:02}:{:02}:{:02}\n".format(
                        gps.timestamp_utc.tm_mon,  # Grab parts of the time from the
                        gps.timestamp_utc.tm_mday,  # struct_time object that holds
                        gps.timestamp_utc.tm_year,  # the fix time.  Note you might
                        gps.timestamp_utc.tm_hour - 6,  # Central Time zone
                        gps.timestamp_utc.tm_min,  # month!
                        gps.timestamp_utc.tm_sec,
                        # gps.timestamp_utc[6]
                        # cannot find way to scape ms.
                        # Need to identify timestamp init code.
                    )
                )"""
                # 2. Latitute
                if gps.latitude is not None:
                    disconnected_data.append("LA:{0:.9f}\n".format(gps.latitude))
                else:
                    disconnected_data.append("LA:NoLat\n")
                # 3. Longitude
                if gps.longitude is not None:
                    disconnected_data.append("LO:{0:.9f}\n".format(gps.longitude))
                else:
                    disconnected_data.append("LO:NoLong\n")
                # 4. # of sattelites
                """if gps.satellites is not None:
                    disconnected_data.append("SA:{}\n".format(gps.satellites))
                else:
                    disconnected_data.append("SA:NoSat\n")"""
                # 5. Altitude in Feet
                if gps.altitude_m is not None:
                    disconnected_data.append("AL:{}\n".format(gps.altitude_m * 3.28084))
                else:
                    disconnected_data.append("AL:NoAlt\n")
                # 6. Speed miles/hour
                if gps.speed_knots is not None:
                    disconnected_data.append(
                        "SP:{}\n".format(gps.speed_knots * 1.15078)
                    )
                else:
                    disconnected_data.append("SP:NoSpeed\n")
                # 7. Track angle degrees
                if gps.track_angle_deg is not None:
                    disconnected_data.append("TA:{}\n".format(gps.track_angle_deg))
                else:
                    disconnected_data.append("TA:NoTrac\n")
                # 8. Horizontal dilution
                """if gps.horizontal_dilution is not None:
                    disconnected_data.append("{}\n".format(gps.horizontal_dilution))
                else:
                    disconnected_data.append("NoDil\n")"""
                time.sleep(frequency_conversion / 1000)
            print("Finished downloading data")
            save_once = 1
            advertise_counter = 0
            disconnected_counter = 0
        if ble.connected and disconnected_BLE:
            print("Uploading Lost Data")
            asdfg = 0
            time.sleep(3)
            for data in disconnected_data:
                try:
                    asdfg = asdfg + 1
                    print(asdfg)
                    uart1.write(data)
                    print(data)
                except Exception:
                    pass
            disconnected_BLE = False
            disconnected_data = []
            save_once = 0

        # SSENDSENDSNED SEND SEND SEND
        # while ble.connected:
        while ble.connected:
            if connectonce == 0:
                print("connected")
                connectonce = 1
            # Make sure to call gps.update() every loop iteration and at least twice
            # as fast as data comes from the GPS unit (usually every second).
            # This returns a bool that's true if it parsed new data (you can ignore it
            # though if you don't care and instead look at the has_fix property).
            gps.update()

            while not gps.has_fix:
                gps.update()
                # Try again if we don't have a fix yet.
                count = count + 1
                if count == frequency_hertz:
                    count = 0
                uart1.write(f"Waiting for fix... {count}")
                print(f"Waiting for fix... {count}")
                time.sleep(frequency_conversion / 1000)
            try:
                # uart1.write("========================================")
                # Print a separator line.
                # 1. TIMESTAMP {}/{}/{} {:02}:{:02}:{:02}
                """uart1.write(
                    "{}/{}/{} {:02}:{:02}:{:02}".format(
                        gps.timestamp_utc.tm_mon,  # Grab parts of the time from the
                        gps.timestamp_utc.tm_mday,  # struct_time object that holds
                        gps.timestamp_utc.tm_year,  # the fix time.  Note you might
                        gps.timestamp_utc.tm_hour - 6,  # Central Time zone
                        gps.timestamp_utc.tm_min,  # month!
                        gps.timestamp_utc.tm_sec,
                        # gps.timestamp_utc[6]
                        # cannot find way to scape ms.
                        # Need to identify timestamp init code.
                    )
                )"""
                # 2. Latitute
                if gps.latitude is not None:
                    uart1.write(f"LA:{gps.latitude:.9f}")
                    print(f"LA:{gps.latitude:.9f}")
                    print(f"BleStatus: {ble.connected}")
                    if ble.connected is False:
                        print("Breaking!")
                        disconnected_BLE = True
                        advertise_counter = 1
                        break
                else:
                    uart1.write("LA:NoLat")
                    print("LA:NoLat")
                    print(f"BleStatus: {ble.connected}")
                    if ble.connected is False:
                        print("Breaking!")
                        disconnected_BLE = True
                        advertise_counter = 1
                        break
                # 3. Longitude
                if gps.longitude is not None:
                    uart1.write(f"LO:{gps.longitude:.9f}")
                    print(f"LO:{gps.longitude:.9f}")
                    print(f"BleStatus: {ble.connected}")
                    if ble.connected is False:
                        print("Breaking!")
                        disconnected_BLE = True
                        advertise_counter = 1
                        break
                else:
                    uart1.write("LO:NoLong")
                    print("LO:Nolong")
                    print(f"BleStatus: {ble.connected}")
                    if ble.connected is False:
                        print("Breaking!")
                        disconnected_BLE = True
                        advertise_counter = 1
                        break
                # 4. # of sattelites
                """if gps.satellites is not None:
                    uart1.write("{}".format(gps.satellites))
                else:
                    uart1.write("NoSat")"""
                # 5. Altitude in Feet
                if gps.altitude_m is not None:
                    uart1.write(f"AL:{gps.altitude_m * 3.28084}")
                    print(f"AL:{gps.altitude_m * 3.28084}")
                    print(f"BleStatus: {ble.connected}")
                    if ble.connected is False:
                        print("Breaking!")
                        disconnected_BLE = True
                        advertise_counter = 1
                        break
                else:
                    uart1.write("AL:NoAlt")
                    print("AL:NoAlt")
                    print(f"BleStatus: {ble.connected}")
                    if ble.connected is False:
                        print("Breaking!")
                        disconnected_BLE = True
                        advertise_counter = 1
                        break
                # 6. Speed miles/hour
                if gps.speed_knots is not None:
                    uart1.write(f"SP:{gps.speed_knots * 1.15078}")
                    print(f"SP:{gps.speed_knots * 1.15078}")
                    print(f"BleStatus: {ble.connected}")
                    if ble.connected is False:
                        print("Breaking!")
                        disconnected_BLE = True
                        advertise_counter = 1
                        break
                else:
                    uart1.write("SP:NoSpeed")
                    print("SP:NoSpeed")
                    print(f"BleStatus: {ble.connected}")
                    if ble.connected is False:
                        print("Breaking!")
                        disconnected_BLE = True
                        advertise_counter = 1
                        break
                # 7. Track angle degrees
                if gps.track_angle_deg is not None:
                    uart1.write(f"TA:{gps.track_angle_deg}")
                    print(f"TA:{gps.track_angle_deg}")
                    print(f"BleStatus: {ble.connected}")
                    if ble.connected is False:
                        print("Breaking!")
                        disconnected_BLE = True
                        advertise_counter = 1
                        break
                else:
                    uart1.write("TA:NoTrac")
                    print("TA:NoTrac")
                    print(f"BleStatus: {ble.connected}")
                    if ble.connected is False:
                        print("Breaking!")
                        disconnected_BLE = True
                        advertise_counter = 1
                        break
                # 8. Horizontal dilution
                """if gps.horizontal_dilution is not None:
                    uart1.write("{}\n".format(gps.horizontal_dilution))
                else:
                    uart1.write("NoDil")"""
            except Exception:
                disconnected_BLE = True
                # print(f"BleStatus: {ble.connected}")
                print("Disconnected")
                advertise_counter = 1
                if disconnected_counter <= disconnected_counter * 10:
                    """disconnected_data.append(
                        "========================================\n"
                    )"""
                    # Print a separator line.
                    # 1. TIMESTAMP {}/{}/{} {:02}:{:02}:{:02}
                    """disconnected_data.append(
                        "{}/{}/{} {:02}:{:02}:{:02}\n".format(
                            gps.timestamp_utc.tm_mon,  # Grab parts of the time from the
                            gps.timestamp_utc.tm_mday,  # struct_time object that holds
                            gps.timestamp_utc.tm_year,  # the fix time.  Note you might
                            gps.timestamp_utc.tm_hour - 6,  # Central Time zone
                            gps.timestamp_utc.tm_min,  # month!
                            gps.timestamp_utc.tm_sec,
                            # gps.timestamp_utc[6]
                            # cannot find way to scape ms.
                            # Need to identify timestamp init code.
                        )
                    )"""
                    # 2. Latitute
                    if gps.latitude is not None:
                        disconnected_data.append("LA:{0:.9f}\n".format(gps.latitude))
                    else:
                        disconnected_data.append("LA:NoLat\n")
                    # 3. Longitude
                    if gps.longitude is not None:
                        disconnected_data.append("LO:{0:.9f}\n".format(gps.longitude))
                    else:
                        disconnected_data.append("LO:NoLong\n")
                    # 4. # of sattelites
                    """if gps.satellites is not None:
                        disconnected_data.append("{}\n".format(gps.satellites))
                    else:
                        disconnected_data.append("NoSat\n")"""
                    # 5. Altitude in Feet
                    if gps.altitude_m is not None:
                        disconnected_data.append(
                            "AL:{}\n".format(gps.altitude_m * 3.28084)
                        )
                    else:
                        disconnected_data.append("AL:NoAlt\n")
                    # 6. Speed miles/hour
                    if gps.speed_knots is not None:
                        disconnected_data.append(
                            "SP:{}\n".format(gps.speed_knots * 1.15078)
                        )
                    else:
                        disconnected_data.append("SP:NoSpeed\n")
                    # 7. Track angle degrees
                    if gps.track_angle_deg is not None:
                        disconnected_data.append("TA:{}\n".format(gps.track_angle_deg))
                    else:
                        disconnected_data.append("TA:NoTrac\n")
                    # 8. Horizontal dilution
                    """if gps.horizontal_dilution is not None:
                        disconnected_data.append("{}\n".format(gps.horizontal_dilution))
                    else:
                        disconnected_data.append("NoDil\n")"""
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
        # print("Fix quality: {}".format(gps.fix_quality))
        # Some attributes beyond latitude, longitude and timestamp are optional
        # and might not be present.  Check if they're None before trying to use!
        # if gps.satellites is not None:
        # uart1.write("# satellites: {}".format(gps.satellites))
        # if gps.altitude_m is not None:
        # uart1.write("Altitude: {} feet".format(gps.altitude_m * 3.28084))
        # if gps.speed_knots is not None:
        # uart1.write("Speed: {} miles/hour".format(gps.speed_knots * 1.15078))
        # if gps.track_angle_deg is not None:
        # uart1.write("Track angle: {} degrees".format(gps.track_angle_deg))
        # if gps.horizontal_dilution is not None:
        # uart1.write(f"Horizontal dilution: {gps.horizontal_dilution}")
        # dilutionGrader(disconnected_BLE)

        # print(f"Dilution Grade {dilutionGrader()}")
        # print(f"Horizontal dilution: {}".format(gps.horizontal_dilution))
        # if gps.height_geoid is not None:
        #    print("Height geoid: {} meters".format(gps.height_geoid))
