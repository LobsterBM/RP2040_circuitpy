import board
import digitalio
import time
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode
import busio
from adafruit_i2c import adafruit_ssd1306
from adafruit_i2c import adafruit_framebuf
import json

#Define definitions
MENU = 0
ACCOUNT_LIST = 1
PIN_INPUT = 2

#Define button actions
KEY = 1
ADD = 2
BACK = 3
OFF = 4
UP = 5
DOWN = 6
LEFT = 7
RIGHT = 8
OK = 9





class Button :

    def __init__(self , pin):
        self.btn_pin = pin
        self.btn = digitalio.DigitalInOut(self.btn_pin)
        self.btn.direction = digitalio.Direction.OUTPUT
        self.btn.value = True
    def getValue(self):
        return self.btn.value

    def value(self):
        return self.btn.value

btn1 = Button(board.GP5)
btn2 = Button(board.GP6)
btn3 = Button(board.GP9)
btn4= Button(board.GP10)
btntop = Button(board.GP20)

def accountPage(interface):
    interface.update(listfb, ACCOUNT_LIST)
    with open('./accounts.json' , 'r') as js:
        data = json.load(js)
    js.close()
    account_list=[]
    for i in data["account_list"]:
        account_list.append(i)

    accountsize = len(account_list)
    accountitterator = 0
    display.text(account_list[0]["account"] , 0 , 0, 1,size = 2 )
    display.show()
    print(account_list[0]["account"])
    cycle = True
    while cycle:
        if (btn1.value()) == False :
            accountitterator +=1
            interface.update(listfb, interface.getstate())
            display.text(account_list[accountitterator%accountsize]["account"] ,0,0, 1 , size = 2)
            display.show()
        elif (btn2.value()) ==False :
            accountitterator -= 1
            interface.update(listfb, interface.getstate())
            display.text(account_list[accountitterator % accountsize]["account"], 0, 0, 1 , size = 2)
            display.show()
        elif (btn4.value()) == False:
            interface.update(menufb, MENU)
            menuPage(interface)
        elif(btntop.value() == False):
            interface.update(inputfb , PIN_INPUT)
            menuPage(interface)

        time.sleep(0.1)

def menuPage(interface):
    interface.update(menufb, MENU)
    pressed = True
    while pressed:
        if (btn1.value()) == False:
            pressed = False;
            print("button 1 pressed")
            accountPage(interface)

        elif (btn2.value()) == False:
            print('button 2 pressed')
            pressed = False;
            btn_action(btn2, interface)

        elif (btn3.value()) == False:
            pressed = False;
            btn_action(btn3, interface)

        elif (btn4.value()) == False:
            pressed = False;
            btn_action(btn4, interface)

        elif (btntop.value()) == False:
            pressed = False;
            btn_action(btntop, interface)
        time.sleep(0.1)




#actions per button
def btn_action(btn , interface):
    state = interface.getstate()
    if state == MENU:
        if btn == btn1:
            interface.update(listfb, ACCOUNT_LIST)
            accountPage(interface)

        elif btn == btn2:
            pass
        elif btn == btn3 :
            pass


    elif state == ACCOUNT_LIST :
        if btn == btn1 :
            pass
        elif btn == btntop:
            interface.update(inputfb, PIN_INPUT )
        elif btn == btn4 :
            interface.update(menufb, MENU)
            menuPage(interface)




#types the string str out as HID keyboard

keyboard = Keyboard(usb_hid.devices)
keyboardus = KeyboardLayoutUS(usb_hid.devices)

def str_to_hid(str):
    return
#TODO  : add keycode for AZERTYBE and AZERTY by copying and editing the original Keycode file

#init I2C oled screen
SCL = board.GP1
SDA = board.GP0

i2c = busio.I2C(SCL, SDA)

#set the size
display = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)
#reset the display

display.fill(0)
display.show()



def bitmap_to_fb(filename):
    with open(filename , 'rb') as fp:
        fp.readline()
        fp.readline()
        fp.readline()

        buffer = bytearray(fp.read())
        #WTF, for some reasong , MHMSB works but MVLSB doesn't even though it's itnedned for SSD1306...
        fb = adafruit_framebuf.FrameBuffer(buffer, 128, 64, buf_format=adafruit_framebuf.MHMSB)
        fp.close()
        #print("pbm read")
        return fb


def oledprt(fb, display):
    display.fill(0)
    for y in range(fb.height):
        for x in range(fb.width):
            display.pixel(x,y,fb.pixel(x,y))
    display.show()



class GuiInterface :


    def __init__(self, display , width , height , state):
        self.display = display
        self.height = height
        self.width = width
        self.state = state #menu , input password , accoutn selection , ...
        self.prev = state


    #TODO find a better more efficient way of doing this
    def update(self,fb , state ):
        self.prev = self.state
        self.state = state
        display.fill(0)
        for y in range(fb.height):
            for x in range(fb.width):
                display.pixel(x, y, fb.pixel(x, y))
        display.show()

    def getstate(self):
        return self.state
    def __setstate__(self, state):
        self.state = state





#fb2 = xbitmap_to_fb('./background.bitmap')
fb1 = bitmap_to_fb('./1bitmap.pbm')

menufb = bitmap_to_fb('./main_menu.pbm')
listfb =bitmap_to_fb("./list.pbm")
inputfb = bitmap_to_fb('./input.pbm')
oledprt(fb1,display)
time.sleep(1)
interface = GuiInterface(display , 128, 64, MENU)
interface.update(menufb, MENU)
menuPage(interface)



"""
    On boot ask what to do 
        1: type password HID
            -select account
            - ask for pin/password  (and give 15 second timer)
            -after typing password , shutdown 
        2 : add password
            ~ need input method 
            -update existing
            -add new 
                -insert account name 
                -password 
                -pin / master password 
        3 : pong ? top & bottom buttons 
        
"""




