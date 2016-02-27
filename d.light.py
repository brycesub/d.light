#!/usr/bin/python

from multiprocessing import Process, Manager, Event

def light(dummy,state,wake,kill):
  import RPi.GPIO as GPIO
  import time
  import config

  p1 = config.p1
  p2 = config.p2
  p4 = config.p4
  p8 = config.p8
  p16 = config.p16
  p32 = config.p32
  p64 = config.p64
  p128 = config.p128

  GPIO.setmode(GPIO.BCM)
  GPIO.setwarnings(False)
  GPIO.setup(p1,GPIO.OUT)
  GPIO.setup(p2,GPIO.OUT)
  GPIO.setup(p4,GPIO.OUT)
  GPIO.setup(p8,GPIO.OUT)
  GPIO.setup(p16,GPIO.OUT)
  GPIO.setup(p32,GPIO.OUT)
  GPIO.setup(p64,GPIO.OUT)
  GPIO.setup(p128,GPIO.OUT)

  try:
    while True:
      GPIO.output(p128,True)
      GPIO.output(p64,True)
      GPIO.output(p32,True)
      GPIO.output(p16,True)
      GPIO.output(p8,True)
      GPIO.output(p4,True)
      GPIO.output(p2,True)
      GPIO.output(p1,True)

      while wake.is_set() == False:
        wake.wait(.1)

      wake.clear()

      for i in range(35,255):
        GPIO.output(p1,not i&1)
        GPIO.output(p2,not i&2)
        GPIO.output(p4,not i&4)
        GPIO.output(p8,not i&8)
        GPIO.output(p16,not i&16)
        GPIO.output(p32,not i&32)
        GPIO.output(p64,not i&64)
        GPIO.output(p128,not i&128)
        print "bright",i
        kill.wait(state['waketime']*60/(255-35))
        if kill.is_set() == True:
          break

      while kill.is_set() == False:
        kill.wait(.1)

      kill.clear()

  except:
    GPIO.cleanup()
  finally:
    GPIO.cleanup()

def web(dummy,state,wake,kill):
  from bottle import route, run, get, post, request, static_file, abort
  import os
  import config

  wwwroot = os.path.dirname(__file__)+'/www'

  @route('/')
  def docroot():
    return static_file('index.html',wwwroot)

  @route('/<filepath:path>')
  def servfile(filepath):
    return static_file(filepath,wwwroot)

  @route('/light')
  def light():
    wake.set()
    return dict(state)

  @route('/kill')
  def killlight():
    kill.set()
    return dict(state)

  @route('/stat')
  def stat():
    return dict(state)

  run(host='0.0.0.0',port=config.wwwport)

if __name__ == '__main__':
  from time import sleep
  import config

  manager = Manager()
  state = manager.dict()
  kill = Event()
  wake = Event()
  state['waketime'] = config.waketime
  state['snoozetime'] = config.snoozetime

  l = Process(target=light,args=(1,state,wake,kill))
  l.daemon = True
  l.start()

  w = Process(target=web,args=(1,state,wake,kill))
  w.daemon = True
  w.start()

  while l.is_alive() == True and w.is_alive() == True:
    sleep(1)

