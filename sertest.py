import serial

def main():
    # Initialise the serial port to listen to the Arduino's outputs...
    ser = serial.Serial('/dev/ttyAMA0', 115200, timeout=2)
    rooms=['Front Door','Hall','Lounge','Kitchen','Landing','Dining room','Back door']
    print("Polling serial port...")

    while True:
        # Poll the serial buffer.
        state = ser.readline()

        # The input can be a bit messy. Disguard any clearly wrong data.
        
        try:
            state = state.rstrip("ACT\n")
            
            if len(state)>0:
                print("Alarm: " + rooms[int(state)])
        except:
            pass

main()
