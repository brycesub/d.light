#!/usr/bin/python

def off():
  import RPi.GPIO as GPIO
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

  GPIO.output(p1,True)
  GPIO.output(p2,True)
  GPIO.output(p4,True)
  GPIO.output(p8,True)
  GPIO.output(p16,True)
  GPIO.output(p32,True)
  GPIO.output(p64,True)
  GPIO.output(p128,True)

def light(dummy,state):
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
    for i in range(34,256):
      GPIO.output(p1,not i&1)
      GPIO.output(p2,not i&2)
      GPIO.output(p4,not i&4)
      GPIO.output(p8,not i&8)
      GPIO.output(p16,not i&16)
      GPIO.output(p32,not i&32)
      GPIO.output(p64,not i&64)
      GPIO.output(p128,not i&128)
      print i,not i&1,not i&2,not i&4,not i&8,not i&16,not i&32,not i&64,not i&128
      time.sleep(state['snoozetime']*60/222)

    GPIO.output(p1,False)
    GPIO.output(p2,False)
    GPIO.output(p4,False)
    GPIO.output(p8,False)
    GPIO.output(p16,False)
    GPIO.output(p32,False)
    GPIO.output(p64,False)
    GPIO.output(p128,False)

  except:
    GPIO.cleanup()
  finally:
    GPIO.cleanup()

def web(dummy,state):
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
    state['start'] = 1
    return dict(state)

  @route('/kill')
  def killlight():
    state['kill'] = 1
    return dict(state)

  @route('/stat')
  def stat():
    return dict(state)

  run(host='0.0.0.0',port=config.wwwport)

if __name__ == '__main__':
  from multiprocessing import Process, Manager
  from time import sleep
  import config

  manager = Manager()
  state = manager.dict()
  state['kill'] = 0
  state['start'] = 0
  state['waketime'] = config.waketime
  state['snoozetime'] = config.snoozetime

  l = Process(target=light,args=(1,state))
  l.daemon = True

  w = Process(target=web,args=(1,state))
  w.daemon = True
  w.start()

  while True:
    if state['start'] == 1 and l.is_alive() == False:
      l.start()
      state['start'] = 0

    if state['kill'] == 1 and l.is_alive() == True:
      l.terminate()
      off()
      state['kill'] = 0

    sleep(.5)
