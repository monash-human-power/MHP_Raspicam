# ---------------------------------------------------------------------
# Last Modified:
#   4-12-2017
# Description:
#   This program reads data from the accelerometer and dumps
#   it to a file. The speed of read and write commands is printed to the
#   terminal interface.
# ---------------------------------------------------------------------

# ---------------------- Import required libraries --------------------
import IMU
import time
import datetime
import math
import csv

# ---------------------- Initialise berryIMU --------------------------

RAD_TO_DEG = 57.29578
M_PI = 3.14159265358979323846
# [deg/s/LSB]  If you change the dps for gyro, you need to update this value accordingly
G_GAIN = 0.070
AA = 0.40      # Complementary filter constant

gyroXangle = 0.0
gyroYangle = 0.0
gyroZangle = 0.0
CFangleX = 0.0
CFangleY = 0.0

IMU.detectIMU()  # Detect if BerryIMUv1 or BerryIMUv2 is connected.
IMU.initIMU()  # Initialise the accelerometer, gyroscope and compass

# Open file to print too
filename = "/home/pi/Documents/MHP_raspicam/IMU/Data/Data on #.csv"
filename = filename.replace("#", time.strftime("%d-%m-%Y at %H:%M:%S", time.localtime()))
file = open(filename, 'w')
filewrite = csv.writer(file, delimiter=',', lineterminator='\n')

# ---------------------- Start Program --------------------------------

a = datetime.datetime.now()

while True:
    try:
        # Read the accelerometer,gyroscope and magnetometer values
        ACCx = IMU.readACCx()
        ACCy = IMU.readACCy()
        ACCz = IMU.readACCz()
        GYRx = IMU.readGYRx()
        GYRy = IMU.readGYRy()
        GYRz = IMU.readGYRz()
        MAGx = IMU.readMAGx()
        MAGy = IMU.readMAGy()
        MAGz = IMU.readMAGz()

        # Store Raw Values into .csv file for later analysis
        filewrite.writerow([ACCx, ACCy, ACCz, GYRx, GYRy, GYRz, MAGx, MAGy, MAGz])

        # Calculate loop Period(LP). How long between Gyro Reads
        b = datetime.datetime.now() - a
        a = datetime.datetime.now()
        LP = b.microseconds / (1000000 * 1.0)
        print "Loop Time | %5.2f|" % (LP),

        # Convert Gyro raw to degrees per second
        rate_gyr_x = GYRx * G_GAIN
        rate_gyr_y = GYRy * G_GAIN
        rate_gyr_z = GYRz * G_GAIN

        # Calculate the angles from the gyro.
        gyroXangle += rate_gyr_x * LP
        gyroYangle += rate_gyr_y * LP
        gyroZangle += rate_gyr_z * LP

        # Convert Accelerometer values to degrees
        AccXangle = (math.atan2(ACCy, ACCz) + M_PI) * RAD_TO_DEG
        AccYangle = (math.atan2(ACCz, ACCx) + M_PI) * RAD_TO_DEG

        # convert the values to -180 and +180
        AccXangle -= 180.0
        if AccYangle > 90:
            AccYangle -= 270.0
        else:
            AccYangle += 90.0

        # Complementary filter used to combine the accelerometer and gyro values.
        CFangleX = AA * (CFangleX + rate_gyr_x * LP) + (1 - AA) * AccXangle
        CFangleY = AA * (CFangleY + rate_gyr_y * LP) + (1 - AA) * AccYangle

        # Calculate heading
        heading = 180 * math.atan2(MAGy, MAGx) / M_PI

        # Only have our heading between 0 and 360
        if heading < 0:
            heading += 360

        # Normalize accelerometer raw values.
        accXnorm = ACCx / math.sqrt(ACCx * ACCx + ACCy * ACCy + ACCz * ACCz)
        accYnorm = ACCy / math.sqrt(ACCx * ACCx + ACCy * ACCy + ACCz * ACCz)

        # Calculate pitch and roll
        pitch = math.asin(accXnorm)
        roll = -math.asin(accYnorm / math.cos(pitch))

        # Calculate the new tilt compensated values
        magXcomp = MAGx * math.cos(pitch) + MAGz * math.sin(pitch)
        magYcomp = MAGx * math.sin(roll) * math.sin(pitch) + MAGy * \
            math.cos(roll) - MAGz * math.sin(roll) * math.cos(pitch)

        # Calculate tilt compensated heading
        tiltCompensatedHeading = 180 * math.atan2(magYcomp, magXcomp) / M_PI

        if tiltCompensatedHeading < 0:
            tiltCompensatedHeading += 360

        if 1:  # Change to '0' to stop showing the angles from the accelerometer
            print ("\033[1;34;40mACCX Angle %5.2f ACCY Angle %5.2f  \033[0m  " %
                   (AccXangle, AccYangle)),

        if 1:  # Change to '0' to stop  showing the angles from the gyro
            print ("\033[1;31;40m\tGRYX Angle %5.2f  GYRY Angle %5.2f  GYRZ Angle %5.2f" %
                   (gyroXangle, gyroYangle, gyroZangle)),

        if 1:  # Change to '0' to stop  showing the angles from the complementary filter
            print ("\033[1;35;40m   \tCFangleX Angle %5.2f \033[1;36;40m  CFangleY Angle %5.2f \33[1;32;40m" % (
                CFangleX, CFangleY)),

        if 1:  # Change to '0' to stop  showing the heading
            print ("HEADING  %5.2f \33[1;37;40m tiltCompensatedHeading %5.2f" %
                   (heading, tiltCompensatedHeading))

        # slow program down a bit, makes the output more readable
        time.sleep(0.03)

    except KeyboardInterrupt:

        # End program
        print("\n\nEnding Program\n")
        file.close()
        break
