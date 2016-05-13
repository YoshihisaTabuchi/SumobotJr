#! /usr/bin/env python
# Test for Sumobot
# 2016-05-01 K.OHWADA @ FabLab Kannai
# Behavior
#   reft turn <-> stop <-> right turn

import time
import RPi.GPIO as GPIO

#
# TwinServo class
#
class TwinServo():
	OFFSET_L = -20.0
	OFFSET_R = -20.0	
	servo_l = None
	servo_r = None

	def __init__(self, pin_l, pin_r):
		self.servo_l = ServoSpeed()
		self.servo_r = ServoSpeed()
		self.servo_l.setOffset(self.OFFSET_L)
		self.servo_r.setOffset(self.OFFSET_R)
#		self.servo_l.setPinMode()
#		self.servo_r.setPinMode()
		self.servo_l.setPin(pin_l)
		self.servo_r.setPin(pin_r)		
		self.servo_l.start()
		self.servo_r.start()

	def change(self, speed_l, speed_r):
		self.servo_l.change(speed_l)
		self.servo_r.change(speed_r)

	def stop(self):
		self.servo_l.stop()
		self.servo_r.stop()
		self.servo_l.cleanupGpio()
#		self.servo_r.cleanupGpio()
							
# end of class

#
# ServoSpeed
#
# speed
#   -100 : clokckwide full-speed
#   0 : stop
#   100 : anticlokckwide full-speed
#
class ServoSpeed():
	FREQ = 50 # 50 Hz (20 ms)
	DUTY_STOP = 7.5 # 1.5ms / 20ms
	COEF = 0.025 # 2.5 / 100
	MIN_SPEED = -100
	STOP_SPEED = 0
	MAX_SPEED = 100	
	servo = None
	pin = 0
	debugPrint = False
	dutyOffset = 0

	def __init__(self):
		pass

	def setDebugPrint(self, debug):
		self.debugPrint = bool(debug)

	def setOffset(self, offset):
		self.dutyOffset = self.COEF * float(offset)

	def setPinMode(self):
		GPIO.setmode(GPIO.BOARD)

	def setPin(self, pin):
		self.pin = int(pin)
		GPIO.setup(self.pin, GPIO.OUT)

	def start(self):
		self.servo = GPIO.PWM(self.pin, self.FREQ)
		duty = self.calcDuty(0)
		self.servo.start(duty)

	def stop(self):
		self.servo.stop()

	def cleanupGpio(self):
		GPIO.cleanup()
		
	def change(self, speed):
		duty = self.calcDuty(speed)
		self.servo.ChangeDutyCycle(duty)

	def calcDuty(self, speed):
		# -100 -> 5.0
		# 0 -> 7.5
		# 100 -> 10.0
		speed = float(speed)
		if speed < self.MIN_SPEED: speed = self.MIN_SPEED
		if speed > self.MAX_SPEED: speed = self.MAX_SPEED
		duty = self.DUTY_STOP + self.dutyOffset + self.COEF * speed
		if self.debugPrint: print duty
		return duty
		
# end of class

#
# Swicth
#
class Swicth():
	pin = 0

	def __init__(self, pin):
		self.pin = pin
		GPIO.setmode(GPIO.BOARD)
		GPIO.setup(self.pin, GPIO.IN)
		pass

	def read(self):
		val = GPIO.input(self.pin)
		return val

	def cleanupGpio(self):
		GPIO.cleanup()

# end of class
	
# main
PIN_L = 15
PIN_R = 16
PIN_SW =18
speed = 0
amount = 5

sw = Swicth(PIN_SW)
val = sw.read()
if not val:
	# exit this program, if sw is off
	sw.cleanupGpio()
	exit()

servo = TwinServo(PIN_L, PIN_R)

try:
	# endless loop
	while True:
		servo.change(speed, speed)
		speed = speed + amount;
		if speed <= -100 or speed >= 100:
			amount = -amount
		time.sleep(0.1)
except KeyboardInterrupt:
	# exit the loop, if key Interrupt
	pass

servo.stop()
# end of main