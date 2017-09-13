import RPi.GPIO as GPIO, time
import datetime

# Enter the GPIO pins and their corresponding names here...
pins = [17,27]
rooms=["Front door", "Back door"]

currStatus=[]
lastStatus=[]

for n in range(0, len(pins)):
    currStatus.append("Unknown")
    lastStatus.append("Unknown")

# Tell the GPIO library to use
# Broadcom GPIO references
GPIO.setmode(GPIO.BCM)

# Supress 'already in use' warning...
GPIO.setwarnings(False)

# Define function to measure charge time
def RCtime (PiPin):
    measurement = 0

    # Discharge capacitor
    GPIO.setup(PiPin, GPIO.OUT)
    GPIO.output(PiPin, GPIO.LOW)
    time.sleep(0.2)

    GPIO.setup(PiPin, GPIO.IN)
    # Count loops until voltage across
    # capacitor reads high on GPIO

    while (GPIO.input(PiPin) == GPIO.LOW):
        measurement += 1

    return measurement

def calibrate():
    # Allow a few runs for the caps to stabilise...
    print("Initialising...")
    for i in range(20):
        for n in range(0,len(pins)):
            x=RCtime(pins[n])

    print("DONE. Scanning rooms...")

# ********************** MAIN PROGRAM
calibrate()

# Main program loop
while True:
    for n in range(0,len(pins)):
        nextVal=RCtime(pins[n])
        
        if nextVal>100:
            currStatus[n]="Open"
        else:
            currStatus[n]="Closed"

        # If there's a change in status, print to console...
        if currStatus[n] != lastStatus[n]:
            time.sleep(2)
            print(rooms[n] + ": " + currStatus[n])
            lastStatus[n] = currStatus[n]

            # Make a log entry:
            with open("alarmstatus.txt", "a") as text_file:
                text_file.write("{:%d-%m-%Y @ %H:%M:%S}: ".format(datetime.datetime.now()) + rooms[n] + ": " + currStatus[n] + "<br> \n")
