#!/usr/bin/python

import RPi.GPIO as GPIO
import time
import bottle

p1 = 5
p2 = 6
p4 = 13
p8 = 19
p16 = 26
p32 = 16
p64 = 20
p128 = 21

GPIO.setmode(GPIO.BCM)
GPIO.setup(p1,GPIO.OUT)
GPIO.setup(p2,GPIO.OUT)
GPIO.setup(p4,GPIO.OUT)
GPIO.setup(p8,GPIO.OUT)
GPIO.setup(p16,GPIO.OUT)
GPIO.setup(p32,GPIO.OUT)
GPIO.setup(p64,GPIO.OUT)
GPIO.setup(p128,GPIO.OUT)

for i in range(32,256):
  GPIO.output(p1,not i&1)
  GPIO.output(p2,not i&2)
  GPIO.output(p4,not i&4)
  GPIO.output(p8,not i&8)
  GPIO.output(p16,not i&16)
  GPIO.output(p32,not i&32)
  GPIO.output(p64,not i&64)
  GPIO.output(p128,not i&128)
  print i,not i&1,not i&2,not i&4,not i&8,not i&16,not i&32,not i&64,not i&128
  time.sleep(.1)

GPIO.cleanup()
