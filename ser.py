import serial, datetime
import Adafruit_CharLCD as LCD

# Set to True enable debug mode...
debugMode = False

# Raspberry Pi pin configuration:
lcd_rs        = 25
lcd_en        = 24
lcd_d4        = 23
lcd_d5        = 17
lcd_d6        = 21
lcd_d7        = 22
lcd_backlight = 4
lcd_columns = 16
lcd_rows    = 2
# Initialize the LCD using the pins above.
lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7,
                           lcd_columns, lcd_rows, lcd_backlight)

def main():
    # Initialise the serial port to listen to the Arduino's outputs...
    ser = serial.Serial('/dev/ttyAMA0', 115200, timeout=2)
    print("Polling serial port...")

    # Set up a dictonary for our house layout
    rooms=['Front door','Hall','Lounge','Kitchen','Study','Dining room','Back door']
    alarmStatus = {'Front door':[245,245,245,'Never'], 'Hall':[245,245,245,'Never'], 'Lounge':[245,245,245,'Never'], 'Kitchen':[245,245,245,'Never'], 'Study':[245,245,245,'Never'], 'Dining room':[245,245,245,'Never'], 'Back door':[245,245,245,'Never']}
    lastRoom = "NOTHING"

    lcd.clear()
    lcd.message('Scanning...')
    
    while True:
        # Poll the serial buffer.
        state = ser.readline()

        # The input can be a bit messy. Disguard any clearly wrong data.
        if len(state) > 2:
            if debugMode == True:
                print("Raw incoming serial data: '" + state + "'")
            state = state.rstrip("ACT\n")

            if debugMode == True:
                print("Cleaned incoming serial data: '" + state + "'")
                
            # If something has changed, update the dictionary then write a new index.php file...
            alarmStatus = updateDictionary(rooms, alarmStatus, state)
    
            if debugMode == True:
                print("Dictionary after serial update: " + str(alarmStatus))
        else:
            # If nothing is new, we'll still need to send something over for 'state'...
            state = 999

        if state != 999:
            alarmStatus = mapColourTicker(alarmStatus, rooms[int(state)])
            # Make a note of the room that was just triggered.
            lastRoom = rooms[int(state)]
        else:
            alarmStatus = mapColourTicker(alarmStatus, "NOTHING")
        
        if debugMode == True:
            if state != 999:
                print("Room for next update: " + str(rooms[int(state)]))
            print("Dictionary after colour update: ")
            print(alarmStatus)
            print("")

        if state != 999:
            writeNewFile(alarmStatus,rooms[int(state)], lastRoom)
            # Show the room that's been triggered on the LCD panel.
            rightNow = '{:%H:%M:%S %d-%m}'.format(datetime.datetime.now())
            lcd.clear()
            lcd.message('Last: ' + rooms[int(state)] + '\n' + rightNow)
        else:
            writeNewFile(alarmStatus,"NOTHING", lastRoom)

def mapColourTicker(alarmDict, roomName):
    # Bring the recently triggered rooms colour
    # back to grey incrementally.
    for currRoom in alarmDict:
        if currRoom == roomName:
            alarmDict[currRoom][0] = 100
            alarmDict[currRoom][2] = 0
        elif alarmDict[currRoom][0] < 245:
            alarmDict[currRoom][0] += 2
            alarmDict[currRoom][2] += 4
        elif alarmDict[currRoom][0] > 245 or alarmDict[currRoom][2] > 245:
            alarmDict[currRoom][0] = 245
            alarmDict[currRoom][2] = 245

    return alarmDict
        
def updateDictionary(roomList, currStatus, newState):
    # newState is an integer, indicating which sensor has been triggered.

    rightNow = '{:%H:%M:%S %d-%m-%Y}'.format(datetime.datetime.now())
    if debugMode == True:
        print("Sensor: " + str(newState))
        print("Old dictionary state: " + str(currStatus))
        print("Room list: " + str(roomList))
        print("------")

    try:
        currStatus[roomList[int(newState)]][3] = str(rightNow)
    except:
        pass
        
    # Idea is that the dictionary should contain a timestamps.
    # The web page needs to be served out at (/var/www/html) 
    return currStatus

def writeNewFile(newStatus, mostRecent, prevRoom):
    # Writes out a new PHP alarm file
    with open('/var/www/html/index.html', 'w') as f:
        # TO DO: There's got to be a way to have a header file with all this in it,
        # so that the actual important data can be concatenated onto it...
        f.write("<html><head><title>Brownton Alarm</title><meta http-equiv='refresh' content='2'>")
        f.write("<meta name='format-detection' content='telephone=no'></head><body>")
        f.write("<font face=arial><center><h1><u>Brownton alarm sensors</u><p><br>")
        
        # Draw the floorplan...
        f.write("<svg width='600' height='600'>")
        # Hall
        f.write("<rect x='300' y='20' width='50' height='250' style='fill:rgb(" + str(newStatus["Hall"][0]) + "," + str(newStatus["Hall"][1]) + "," + str(newStatus["Hall"][2]) + ");stroke:#111111;stroke-width:5;opacity:1' />")
        # Front door
        f.write("<rect x='300' y='20' width='50' height='20' style='fill:rgb(" + str(newStatus["Front door"][0]) + "," + str(newStatus["Front door"][1]) + "," + str(newStatus["Front door"][2]) + ");stroke:#111111;stroke-width:5;opacity:1' />")
        # Study
        f.write("<rect x='175' y='20' width='125' height='125' style='fill:rgb(" + str(newStatus["Study"][0]) + "," + str(newStatus["Study"][1]) + "," + str(newStatus["Study"][2]) + ");stroke:#111111;stroke-width:5;opacity:1' />")
        # Lounge
        f.write("<rect x='350' y='20' width='175' height='250' style='fill:rgb(" + str(newStatus["Lounge"][0]) + "," + str(newStatus["Lounge"][1]) + "," + str(newStatus["Lounge"][2]) + ");stroke:#111111;stroke-width:5;opacity:1' />")
        # Dining room
        f.write("<rect x='350' y='270' width='175' height='150' style='fill:rgb(" + str(newStatus["Dining room"][0]) + "," + str(newStatus["Dining room"][1]) + "," + str(newStatus["Dining room"][2]) + ");stroke:#111111;stroke-width:5;opacity:1' />")
        # Kitchen
        f.write("<rect x='175' y='270' width='175' height='150' style='fill:rgb(" + str(newStatus["Kitchen"][0]) + "," + str(newStatus["Kitchen"][1]) + "," + str(newStatus["Kitchen"][2]) + ");stroke:#111111;stroke-width:5;opacity:1' />")
        # Back door
        f.write("<rect x='175' y='400' width='50' height='20' style='fill:rgb(" + str(newStatus["Back door"][0]) + "," + str(newStatus["Back door"][1]) + "," + str(newStatus["Back door"][2]) + ");stroke:#111111;stroke-width:5;opacity:1' />")

        # Add some text labels...
        f.write("<text x='195' y='100' font-family='Verdana' fill='black' transform='rotate(90 238,180)'>Hall</text>")
        f.write("<text x='185' y='90' font-family='Verdana' fill='black'>Study</text>")
        f.write("<text x='375' y='150' font-family='Verdana' fill='black'>Lounge</text>")
        f.write("<text x='380' y='350' font-family='Verdana' fill='black'>Dining</text>")
        f.write("<text x='195' y='350' font-family='Verdana' fill='black'>Kitchen</text>")

        f.write("Sorry, your browser does not support inline SVG.")
        f.write("</svg><br>")
        
        for room in newStatus:
            if room == prevRoom:
                f.write("<font color=green><b>")

            f.write(room + ": " + newStatus[room][3] + "<br>")

            if room ==prevRoom:
                f.write("</font color></b>")

        f.write("<br>Green on map = activity in the past 2.5mins.")
        f.write("</font></body></html>")

main()
