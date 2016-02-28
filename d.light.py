#!/usr/bin/python
import config
from multiprocessing import Process, Manager, Event

def light(dummy,state):
  import RPi.GPIO as GPIO
  import time

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
      if state['on'] == True:
        dim = int(state['dim']/100.*config.dimrange+config.dimlow)
        GPIO.output(p1,not dim&1)
        GPIO.output(p2,not dim&2)
        GPIO.output(p4,not dim&4)
        GPIO.output(p8,not dim&8)
        GPIO.output(p16,not dim&16)
        GPIO.output(p32,not dim&32)
        GPIO.output(p64,not dim&64)
        GPIO.output(p128,not dim&128)
      else:
        GPIO.output(p1,True)
        GPIO.output(p2,True)
        GPIO.output(p4,True)
        GPIO.output(p8,True)
        GPIO.output(p16,True)
        GPIO.output(p32,True)
        GPIO.output(p64,True)
        GPIO.output(p128,True)

      sleep(.1)
  except:
    GPIO.cleanup()
  finally:
    GPIO.cleanup()

def web(dummy,state):
  from bottle import route, run, get, post, request, static_file, abort
  import os

  wwwroot = os.path.dirname(__file__)+'/www'

  @route('/')
  def docroot():
    return static_file('index.html',wwwroot)

  @route('/on')
  def light():
    state['dim'] = 100.
    state['on'] = True
    return dict(state)

  @route('/off')
  def off():
    state['dim'] = 0.
    state['on'] = False
    return dict(state)

  @route('/dim/<dimval>')
  def dim(dimval):
    state['on'] = True
    state['dim'] = float(dimval)
    return dict(state)

  @route('/stat')
  def stat():
    return dict(state)

  @route('/<filepath:path>')
  def servfile(filepath):
    return static_file(filepath,wwwroot)

  run(host='0.0.0.0',port=config.wwwport,server='cherrypy')

if __name__ == '__main__':
  from time import sleep

  manager = Manager()
  state = manager.dict()
  state['waketime'] = config.waketime
  state['snoozetime'] = config.snoozetime
  state['on'] = False
  state['dim'] = 0.

  l = Process(target=light,args=(1,state))
  l.daemon = True
  l.start()

  w = Process(target=web,args=(1,state))
  w.daemon = True
  w.start()

  while l.is_alive() == True and w.is_alive() == True:
    sleep(1)

