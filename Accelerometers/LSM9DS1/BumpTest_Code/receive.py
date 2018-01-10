
import socket
import subprocess
from time import sleep

UDP_IP = subprocess.check_output(['hostname', '-I'])
UDP_PORT = 5005
start = 1

try:
    print ""
    while True:
        sock = socket.socket(socket.AF_INET,  # Internet
                             socket.SOCK_DGRAM)  # UDP
        sock.bind((UDP_IP, UDP_PORT))

        data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes

        if start == 1:
            print "Received Start Command!\n"
            start = 0
            p1 = subprocess.Popen(["python", "datav2a.py"])
            sleep(1)
            print("Recording!\n")
        else:
            print "Received Stop Command!\n"
            start = 1
            subprocess.Popen.kill(p1)
            print("\n\nExecution Terminated.\n")
            p3 = subprocess.call(
                '/home/pi/Documents/MHP_raspicam/Accelerometers/LSM9DS1/BumpTest_Code/Shell_Scripts/sendcsv.sh')
            sleep(1)
except KeyboardInterrupt:
    print("\n\nProgram Ended.\n")
