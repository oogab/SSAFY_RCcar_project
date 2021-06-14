import sys
sys.path.append('./Raspi-MotorHAT-python3')

from Raspi_MotorHAT import Raspi_MotorHAT, Raspi_DCMotor
from Raspi_PWM_Servo_Driver import PWM
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import QtSql
from sense_hat import SenseHat
import RPi.GPIO as gpio
import atexit
import time

global barrelMoveLeft
barrelMoveLeft = False
global barrelMoveRight
barrelMoveRight = False
global pwmValue
pwmValue = 375

trig = 17
echo = 18
led1 = 20
led2 = 21

gpio.setmode(gpio.BCM)
gpio.setup(trig, gpio.OUT)
gpio.setup(echo, gpio.IN)
gpio.setup(led1, gpio.OUT)
gpio.setup(led2, gpio.OUT)
pulse_start = time.time()

buzzer = 12
gpio.setup(buzzer, gpio.OUT)

def backledon():
    gpio.output(led1, True)
    gpio.output(led2, True)

def backledoff():
    gpio.output(led1, False)
    gpio.output(led2, False)

razer = 6
gpio.setup(razer, gpio.OUT)
gpio.output(razer, True)

db2 = QtSql.QSqlDatabase.addDatabase('QMYSQL', 'sense')
db2.setHostName("3.35.8.78")
db2.setDatabaseName("DB_16_03")
db2.setUserName("SSAFY16_03_2")
db2.setPassword("1234")
ok = db2.open()
if ok:
    print("sense ", end="")
    print(ok)
    query2 = QtSql.QSqlQuery(db2)

gpio.setwarnings(False)
pwm = gpio.PWM(buzzer, 262)
pwm.start(50)
time.sleep(0.1)
pwm.stop()

def shoot():
    gpio.output(trig, False)
    time.sleep(0.1) 
    gpio.output(trig, True)
    time.sleep(0.00002)
    gpio.output(trig, False)
      
    while gpio.input(echo) == 0 :
        pulse_start = time.time()
        
    while gpio.input(echo) == 1 :
        pulse_end = time.time()
        
    pulse_duration = pulse_end - pulse_start
    distance_1 = pulse_duration * 17000
    distance_2 = round(distance_1, 2)
    print("Distance : ", distance_2, "cm")
    
    pwm = gpio.PWM(buzzer, 262)
    pwm.start(100)
    time.sleep(0.1)
    pwm.stop()

    query2.prepare("insert into sensing2 (time, num1, num2, num3, meta_string, is_finish) values (:time, :num1, :num2, :num3, :meta, :finish)")
    shoot_time = QDateTime().currentDateTime()
    if distance_2 <= 40.0:
        query2.bindValue(":time", shoot_time)
        query2.bindValue(":num1", 1.0)
        query2.bindValue(":num2", 0.0)
        query2.bindValue(":num3", 0.0)
        query2.bindValue(":meta", "")
        query2.bindValue(":finish", 0)
        query2.exec()
    else:
        query2.bindValue(":time", shoot_time)
        query2.bindValue(":num1", 0.0)
        query2.bindValue(":num2", 0.0)
        query2.bindValue(":num3", 0.0)
        query2.bindValue(":meta", "")
        query2.bindValue(":finish", 0)
        query2.exec()
    
class commandThread(QThread):
    def __init__(self):
        super().__init__()

    def run(self):
        self.db1 = QtSql.QSqlDatabase.addDatabase('QMYSQL', 'command')
        self.db1.setHostName("3.35.8.78")
        self.db1.setDatabaseName("DB_16_03")
        self.db1.setUserName("SSAFY16_03_2")
        self.db1.setPassword("1234")
        ok = self.db1.open()
        if ok:
            print("command ", end="")
            print(ok)
            self.query = QtSql.QSqlQuery(self.db1)

        self.mh = Raspi_MotorHAT(addr=0x6f)
        self.myMotor = self.mh.getMotor(2)
        self.myMotor.setSpeed(100)
        self.pwm = PWM(0x6F)
        self.pwm.setPWMFreq(60)

        # self.pwmValue = 375

        # query run
        while True:
            time.sleep(0.3)
            self.getQuery()

    def getQuery(self):
        # time.sleep(0.5)
        self.query.exec_("select * from command2 order by time desc limit 1");
        self.query.next()

        cmdTime = self.query.record().value(0)
        cmdType = self.query.record().value(1)
        cmdArg = self.query.record().value(2)
        is_finish = self.query.record().value(3)

        if is_finish == 0:
            # detect new command
            print(cmdTime.toString(), cmdType, cmdArg)
                
            # update
            self.query.exec_("update command2 set is_finish=1 where is_finish=0")

            # motor
            if cmdType == "go": self.go()
            if cmdType == "back": self.back()
            if cmdType == "left": self.left()
            if cmdType == "right": self.right()
            if cmdType == "mid": self.middle()
            if cmdType == "stop": self.stop()
            if cmdType == "shoot": self.shoot()

            if cmdType == "front" and cmdArg == "press":
                self.go()
                self.middle()
            if cmdType == "leftside" and cmdArg == "press":
                self.go()
                self.left()
            if cmdType == "rightside" and cmdArg == "press":
                self.go()
                self.right()
                
            if cmdType == "front" and cmdArg == "release": self.stop()
            if cmdType == "leftside" and cmdArg == "release": self.stop()
            if cmdType == "rightside" and cmdArg == "release": self.stop()
            
            if cmdType == "barrelleft" and cmdArg == "press": self.barrelLeft()
            if cmdType == "barrelright" and cmdArg == "press": self.barrelRight() 
            
            if cmdType == "barrelleft" and cmdArg == "release": self.barrelStop()
            if cmdType == "barrelright" and cmdArg == "release": self.barrelStop()

    def go(self):
        print("MOTOR GO")
        backledoff()
        self.myMotor.setSpeed(150)
        self.myMotor.run(Raspi_MotorHAT.FORWARD)

    def back(self):
        print("MOTOR BACK")
        backledon()
        self.myMotor.setSpeed(150)
        self.myMotor.run(Raspi_MotorHAT.BACKWARD)

    def left(self):
        print("MOTOR LEFT")
        self.pwm.setPWM(0, 0, 250);

    def right(self):
        print("MOTOR RIGHT")
        self.pwm.setPWM(0, 0, 430);

    def middle(self):
        print("MOTOR MIDDLE")
        self.pwm.setPWM(0, 0, 350);

    def stop(self):
        print("MOTOR STOP")
        backledoff()
        self.myMotor.run(Raspi_MotorHAT.RELEASE)

    def shoot(self):
        print("SHOOT!!")
        shoot()
    
    def barrelLeft(self):
        print("BARREL LEFT")
        global barrelMoveLeft
        barrelMoveLeft = True

    def barrelRight(self):
        print("BARREL RIGHT")
        global barrelMoveRight
        barrelMoveRight = True

    def barrelStop(self):
        print("BARREL STOP")
        global barrelMoveLeft
        global barrelMoveRight
        barrelMoveLeft = False
        barrelMoveRight = False

"""
class senseThread(QThread): 
    def __init__(self):
        super().__init__()

    def run(self):
        self.db2 = QtSql.QSqlDatabase.addDatabase('QMYSQL', 'sense')
        self.db2.setHostName("3.35.8.78")
        self.db2.setDatabaseName("DB_16_03")
        self.db2.setUserName("SSAFY16_03_2")
        self.db2.setPassword("1234")
        ok = self.db2.open()
        if ok:
            print("sense ", end="")
            print(ok)
            self.query = QtSql.QSqlQuery(self.db2)

        while True:
            time.sleep(0.1)
            self.setQuery()

    def setQuery(self):
        pressure = self.sense.get_pressure()
        temp = self.sense.get_temperature()
        humidity = self.sense.get_humidity()
 
        p = round((pressure - 1000) / 100, 3)
        t = round(temp / 100, 3)
        h = round(humidity / 100, 3)
        
        # self.query2.next()
        self.query.prepare("insert into sensing2 (time, num1, num2, num3, meta_string, is_finish) values (:time, :num1, :num2, :num3, :meta, :finish)")
        time = QDateTime().currentDateTime()
        self.query.bindValue(":time", time)
        self.query.bindValue(":num1", p)
        self.query.bindValue(":num2", t)
        self.query.bindValue(":num3", h)
        self.query.bindValue(":meta", "")
        self.query.bindValue(":finish", 0)
        self.query.exec()

        a = int((p*1271)%256)
        b = int((p*1271)%256)
        c = int((p*1271)%256)
        self.sense.clear(a, b, c)
"""

"""
class senseThread(QThread):
    def __init__(self):
        super().__init__()

    def run(self):
        self.db2 = QtSql.QSqlDatabase.addDatabase('QMYSQL', 'sense')
        self.db2.setHostName("3.35.8.78")
        self.db2.setDatabaseName("DB_16_03")
        self.db2.setUserName("SSAFY16_03_2")
        self.db2.setPassword("1234")
        ok = self.db2.open()
        if ok:
            print("sense ", end="")
            print(ok)
            self.query = QtSql.QSqlQuery(self.db2)

        while True:
            time.sleep(0.1)
            self.setQuery()

    def setQuery(self):
        global distance_2
        if distance_2 < 40
"""


class barrelLeft(QThread):
    def __init__(self):
        super().__init__()

    def run(self):
        self.pwm = PWM(0x6F)
        self.pwm.setPWMFreq(60)
        
        global barrelMoveLeft
        global pwmValue

        while True:
            if barrelMoveLeft:
                if pwmValue <= 150:
                    pass
                else:
                    pwmValue -= 2
                    self.pwm.setPWM(1, 0, pwmValue)
                    time.sleep(0.015)

class barrelRight(QThread):
    def __init__(self):
        super().__init__()

    def run(self):
        self.pwm = PWM(0x6F)
        self.pwm.setPWMFreq(60)

        global barrelMoveRight
        global pwmValue

        while True:
            if barrelMoveRight:
                if pwmValue >= 600:
                    pass
                else:
                    pwmValue += 2
                    self.pwm.setPWM(1, 0, pwmValue)
                    time.sleep(0.015)

try:
    th1 = commandThread()
    th1.start()

    th2 = barrelLeft()
    th2.start()

    th3 = barrelRight()
    th3.start()

    app = QApplication([])

    #infinity loop
    while True:
        pass

finally:
    gpio.cleanup()
