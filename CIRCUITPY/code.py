import os

import adafruit_rsa.key
import adafruit_rsa.prime
import adafruit_rsa
import storage
import board
import digitalio
import storage
import time
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode
import busio
from adafruit_i2c import adafruit_ssd1306
from adafruit_i2c import adafruit_framebuf
import json
import microcontroller

#RSA bits
RSABIT = 512
#Unique cpu ID
UID = microcontroller.cpu.uid


TESTPASS = [0]*8


#Define definitions
MENU = 0
ACCOUNT_LIST = 1
PIN_INPUT = 2
ACCOUNT_PAGE = 3
UNLOCK = 4
MANAGE_PAGE = 5

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

#Master pass for editing and deleting passwords
MASTERPASS = ['0']*8
EDIT = 0
DELETE =1

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

#RSA key generation
def getKeys(passCode):
    p = ord(passCode[0])
    for i in passCode:
        p *= ord(i)

    q = int.from_bytes(microcontroller.cpu.uid , 'big')

    p = adafruit_rsa.prime.getprime(p%(RSABIT-1))
    q = adafruit_rsa.prime.getprime(q%(RSABIT-1))

    (e,d) = adafruit_rsa.key.calculate_keys(p,q)

    n = p*q

    (public, private) = (adafruit_rsa.PublicKey(n, e), adafruit_rsa.PrivateKey(n, e, d, p, q))


    return public

#TODO : swap RSA with AES
def encrypt(str , public):
    return adafruit_rsa.encrypt(str, public)

def decrypt(str , private):
    return adafruit_rsa.decrypt(str , private)

def previousPinChar(pos):
    if pos < 0:
        return
    display.fill_rect((16 * (pos + 1)) + 2, 39, 14, 2, False)
    display.fill_rect((16 * pos) + 2, 39, 14, 2, True)
    display.show()

def nextPinChar(pos):
    if pos > 7:
        return
    display.fill_rect((16 * pos) + 2, 39, 14, 2, True)
    display.fill_rect((16 * (pos - 1)) + 2, 39, 14, 2, False)
    display.show()
def updateChar(pos , char):
    display.fill_rect((16 * (pos)) + 3, 20, 13, 16, False)
    display.text(chr(48+char), 3 + (16*pos) , 20 ,1, size = 2   )
    display.show()

def keyboardType(str, layout):
    layout.write(str)








#Initial page gui
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
            continue
        elif (btn3.value()) == False:
            pass

        elif (btn4.value()) == False:
            pass

        elif (btntop.value()) == False:
            sleep()
        time.sleep(0.1)


#########################
# Left button account list page
#########################

#list fo accounts found in json
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
            #interface.update(listfb, interface.getstate())
            #remove text , more efficient thant reprinting the whole page
            display.fill_rect(0,0,100, 40 , False)
            display.text(account_list[accountitterator%accountsize]["account"] ,0,0, 1 , size = 2)
            display.show()
        elif (btn2.value()) ==False :
            accountitterator -= 1
            #interface.update(listfb, interface.getstate())
            display.fill_rect(0,0,100, 40 , False)
            display.text(account_list[accountitterator % accountsize]["account"], 0, 0, 1 , size = 2)
            display.show()
        elif (btn3.value()) == False:
            addAccountPage(interface)
        elif (btn4.value()) == False:
            menuPage(interface)
        elif(btntop.value() == False):
           managePage(interface, account_list[accountitterator%accountsize])
           # accountSelectedPage(interface  , account_list[accountitterator % accountsize])

        time.sleep(0.1)



def unlockPage(interface, accountInfo):
    interface.update(unlockfb, UNLOCK)
    layouts = ['qwerty' , "azerty/FR", "azerty/BE" ]
    layoutval = 0
    display.text("" + accountInfo["account"] + ":", 0, 0, 1, size=1)
    display.text(layouts[layoutval], 10, 20, 1, size=1)
    display.show()
    keyboard = Keyboard(usb_hid.devices)
    keyboardLayout = KeyboardLayoutUS(keyboard)
    #TODO implement other layouts

    cycle = True
    timer = 150
    while cycle :
        if not btn1.value():
            keyboardType(accountInfo["login"],keyboardLayout)
            time.sleep(1)
            menuPage(interface)

        elif not btn2.value():
            keyboardType(accountInfo["pass"],keyboardLayout)
            time.sleep(1)
            menuPage(interface)
        elif not btn3.value():
            layoutval +=1
            layoutval = layoutval%len(layouts)
            display.fill_rect(0,20,100 , 10 , False)
            display.text(layouts[layoutval] , 10,20,1,size = 1)
            display.show()
        elif not btn4.value():
            menuPage(interface)
        if timer % 10 == 0 :
            display.fill_rect(100 , 1 , 24 , 24, False)

            display.text("%s"%(timer//10) , 101 , 2 , 1 , size = 2)
            display.show()
        if timer <= 0:
            menuPage(interface)
        timer -=1
        time.sleep(0.1)



def managePage(interface , accountInfo):
    interface.update(accountfb, ACCOUNT_PAGE)
    display.text(accountInfo["account"], 0, 0, 1, size=2)
    display.show()
    cycle = True
    while cycle:
        if (btn1.value()) == False:
            editAccountPage(interface, accountInfo , EDIT)
        elif (btn2.value()) == False:
            accountSelectedPage(interface,accountInfo)
        elif (btn3.value()) == False:
            editAccountPage(interface, accountInfo , DELETE)
        elif (btn4.value()) == False:
            accountPage(interface)
        elif (btntop.value() == False):
           pass
        time.sleep(0.1)


def accountSelectedPage(interface , accountInfo):
    interface.update(inputfb, ACCOUNT_PAGE)
    display.text("Pin code "+ accountInfo["account"] + ":", 0, 0, 1, size=1)
    display.show()
    display.rect(0,12 , 128 , 32 , True )
    display.line(16 , 12 , 16 , 44 , True)
    display.line(32 , 12 , 32 , 44 , True)
    display.line(48 , 12 , 48 , 44 , True)
    display.line( 64, 12 , 64 , 44 , True)
    display.line( 80, 12 , 80 , 44 , True)
    display.line( 96, 12 , 96 , 44 , True)
    display.line( 112, 12 , 112 , 44 , True)
    display.fill_rect(2,39,14,2, True)
    display.text(chr(48), 3 , 20 ,1, size = 2   )
    display.text(chr(48), 19 , 20 ,1, size = 2   )
    display.text(chr(48), 35 , 20 ,1, size = 2   )
    display.text(chr(48), 51 , 20 ,1, size = 2   )
    display.text(chr(48), 67 , 20 ,1, size = 2   )
    display.text(chr(48), 83 , 20 ,1, size = 2   )
    display.text(chr(48), 99 , 20 ,1, size = 2   )
    display.text(chr(48), 115 , 20 ,1, size = 2   )
    display.show()
    cycle = True
    pos = 0
    char = [0,0,0,0,0,0,0,0]
    while cycle :
        if not btn1.value():
            char[pos] +=1
            if char[pos] == 58-48:
                char[pos] = 65-48
            if char[pos] == 91 -48 :
                char[pos] = 97-48
            char[pos] = char[pos] % (123-48)
            print(char[pos])
            updateChar(pos,char[pos])
        elif not btn2.value():
            char[pos] -=1
            if char[pos] == 96-48:
                char[pos] = 90-48
            if char[pos] == 64-48:
                char[pos] = 57-48
            char[pos] = char[pos] % (123-48)
            updateChar(pos,char[pos])
        elif not btn3.value():
            if pos > 0:
                pos -=1
                previousPinChar(pos)
        elif not btn4.value():
             if pos < 7 :
                pos +=1
                nextPinChar(pos)
        elif not btntop.value():

            if(TESTPASS == char):
                unlockPage(interface , accountInfo)
            else:
                menuPage(interface)
        time.sleep(0.1)

def editAccountPage(interface, accountInfo, action):
    interface.update(inputfb, ACCOUNT_PAGE)
    actionstr = "edit"
    if action:
        actionstr = "delete"
    display.text("Master pin code to "+ actionstr + accountInfo["account"] + ":", 0, 0, 1, size=1)
    display.show()
    display.rect(0, 12, 128, 32, True)
    display.line(16, 12, 16, 44, True)
    display.line(32, 12, 32, 44, True)
    display.line(48, 12, 48, 44, True)
    display.line(64, 12, 64, 44, True)
    display.line(80, 12, 80, 44, True)
    display.line(96, 12, 96, 44, True)
    display.line(112, 12, 112, 44, True)
    display.fill_rect(2, 39, 14, 2, True)
    display.text(chr(48), 3, 20, 1, size=2)
    display.text(chr(48), 19, 20, 1, size=2)
    display.text(chr(48), 35, 20, 1, size=2)
    display.text(chr(48), 51, 20, 1, size=2)
    display.text(chr(48), 67, 20, 1, size=2)
    display.text(chr(48), 83, 20, 1, size=2)
    display.text(chr(48), 99, 20, 1, size=2)
    display.text(chr(48), 115, 20, 1, size=2)
    display.show()
    cycle = True
    pos = 0
    char = [0, 0, 0, 0, 0, 0, 0, 0]
    while cycle:
        if not btn1.value():
            char[pos] += 1
            if char[pos] == 58 - 48:
                char[pos] = 65 - 48
            if char[pos] == 91 - 48:
                char[pos] = 97 - 48
            char[pos] = char[pos] % (123 - 48)
            print(char[pos])
            updateChar(pos, char[pos])
        elif not btn2.value():
            char[pos] -= 1
            if char[pos] == 96 - 48:
                char[pos] = 90 - 48
            if char[pos] == 64 - 48:
                char[pos] = 57 - 48
            char[pos] = char[pos] % (123 - 48)
            updateChar(pos, char[pos])
        elif not btn3.value():
            if pos > 0:
                pos -= 1
                previousPinChar(pos)
        elif not btn4.value():
            if pos < 7:
                pos += 1
                nextPinChar(pos)
        elif not btntop.value():

            if (MASTERPASS == char):
                if action:
                    #editAccountAuthorizedPage(interface, accountInfo)
                    pass
                else:
                    deleteAccountAuthorizedPage(interface,accountInfo)
                    display.fill(0)
                    display.text("Deleted", 0,0,1,size = 2)
                    display.show()
                    menuPage(interface)
            else:

                menuPage(interface)
        time.sleep(0.1)
    pass

#edits section in json file
def editAccountAuthorizedPage(interface, accountInfo):

    fp = open("./accounts.json","a")
    accounts = json.load(fp)

    for i in range(len(accounts)):
        if(accounts[i]["account"] == accounts["account"]):
            accounts.pop(i)
        break
    fp.close()
    if os.path.exists("/accounts.bak"):
        os.remove("/accounts.bak")

    os.rename("/accounts.json" ,"/accounts.bak" )

    fp = open("/accounts.json","w")
    fp.write(json.dumps(accounts, sort_keys=True, separators=(',',':')))
    fp.close()
    return


#deletes section in json file
def deleteAccountAuthorizedPage(interface, accountInfo):
    fp = open("./accounts.json","a")
    accounts = json.load(fp)

    for i in range(len(accounts)):
        if(accounts[i]["account"] == accounts["account"]):
            accounts.pop(i)
        break
    fp.close()
    if os.path.exists("/accounts.bak"):
        os.remove("/accounts.bak")

    os.rename("/accounts.json" ,"/accounts.bak" )

    fp = open("/accounts.json","w")
    fp.write(json.dumps(accounts, sort_keys=True, separators=(',',':')))
    fp.close()
    return

def addAccountPage(interface):
    pass


#########################
# Center right button manage account page
#########################


#TODO  : add keycode for AZERTYBE and AZERTY by copying and editing the original Keycode file
def str_to_hid(str):
    return


#blink led on boot
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
for i in range (10):
    led.value = not led.value
    time.sleep(0.1)
led.value = True

#init buttons
# 2 14 10 6 20
btn1 = Button(board.GP2)
btn2 = Button(board.GP6)
btn3 = Button(board.GP10)
btn4= Button(board.GP14)
btntop = Button(board.GP20)


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
    def previousPage(self):
        self.state = self.prev
        if self.state == MENU:
            menuPage(self)

        elif self.state == ACCOUNT_LIST :
            accountPage(self)


def sleep():
    while True:
        display.fill(0)
        display.show()
        time.sleep(100)





#load all bitmaps as framebuffers

fb1 = bitmap_to_fb('./splash.pbm')
menufb = bitmap_to_fb('./main_menu2.pbm')
listfb =bitmap_to_fb("./list.pbm")
inputfb = bitmap_to_fb('./input.pbm')
unlockfb = bitmap_to_fb('./unlock.pbm')
accountfb = bitmap_to_fb('./account_action.pbm')

#display first framebuffer
oledprt(fb1,display)
time.sleep(0.5)

#init GUI class , mighgt remove class since not necessary
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
"""with open("/pass.txt","a") as fp:
    fp.write("this worked ")
    print("printed to file")
    fp.close()
"""


"""#checking if public key already exists
try :
    publicfile = open("./public.key")
    print("public key already exists")
    publicfile.close()
except OSError:

    #TODO find a way to write to file
   storage.remount("/", readonly=False)
    publicfile = open('./test.txt',"a")
    publicfile.write("abc")
    publicfile.close()



"""


"""
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

"""
