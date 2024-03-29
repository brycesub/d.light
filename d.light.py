#!/usr/bin/python
import config
from multiprocessing import Process, Manager, Event

def scheduler(dummy,state,esnooze):
  import time
  from datetime import datetime, timedelta

  while True:
    now = datetime.now()
    at = datetime.strptime(state['alarmtime'],'%H:%M')-timedelta(minutes=state['brightentime'])
    if at.hour == now.hour and at.minute == now.minute and now.second <= 2 and state['alarmset']:
      state['alarming'] = True
      i = int(config.dimlow)
      while state['alarming'] and state['alarmset']:
        if esnooze.is_set():
          i=int(config.dimlow)
          esnooze.clear()
          if state['alarming']:
            state['dim'] = 0
            state['on'] = False
            esnooze.wait(state['snoozetime']*60)
          if state['alarming'] == False:
            esnooze.clear()
            break
        state['dim'] = (float(i)-config.dimlow)/config.dimrange*100
        state['on'] = True
        esnooze.wait(state['brightentime']*60./float(config.dimrange))
        if i < config.dimhigh:
          i=i+1
    time.sleep(1)

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

        if state['dim'] == 0:
          dim = 0
          state['on'] = False
        elif state['dim'] == 100:
          dim = 255
        else:
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

def web(dummy,state,esnooze):
  from bottle import route, run, get, post, request, static_file, abort
  import time
  import os
  from datetime import datetime

  wwwroot = os.path.dirname(__file__)+'/www'

  @route('/')
  def docroot():
    return static_file('index.html',wwwroot)

  @route('/light/<sw>')
  def light(sw):
    if sw == "on":
      state['dim'] = 100.
      state['on'] = True
      return dict(state)
    elif sw == "off":
      state['alarming'] = False
      state['dim'] = 0.
      state['on'] = False
      return dict(state)
    else:
      return false

  @route('/alarm/<sw>')
  def alarm(sw):
    if sw == 'on':
      state['alarmset'] = True
      return dict(state)
    elif sw == 'off':
      if state['alarming']:
        state['alarming'] = False
        state['dim'] = 0
        esnooze.set()
      state['alarmset'] = False
      return dict(state)
    else:
      abort(400,'Invalid alarm setting.')

  @route('/alarmset/<t>')
  def alarmset(t):
    try:
      datetime.strptime(t,'%H:%M')
    except:
      abort(400,'Invalid time format.')
    state['alarmtime'] = t
    return dict(state)

  @route('/snoozeset/<t:int>')
  def snoozeset(t):
    state['snoozetime'] = float(t)
    return dict(state)

  @route('/brightenset/<t:int>')
  def brightenset(t):
    state['brightentime'] = float(t)
    return dict(state)

  @route('/dim/<dimval:int>')
  def dim(dimval):
    state['on'] = True
    state['dim'] = float(dimval)
    return dict(state)

  @route('/snooze')
  def snooze():
    esnooze.set()
    return dict(state)

  @route('/alarmoff')
  def alarmoff():
    state['alarming'] = False
    esnooze.set()
    state['dim'] = 100
    state['on'] = True
    return dict(state)

  @route('/stat')
  def stat():
    return dict(state)

  @route('/<filepath:path>')
  def servfile(filepath):
    return static_file(filepath,wwwroot)

  run(host='0.0.0.0',port=config.wwwport)

if __name__ == '__main__':
  from time import sleep

  manager = Manager()
  state = manager.dict()
  state['on'] = False
  state['dim'] = 0.
  state['snoozetime'] = config.snoozetime
  state['brightentime'] = config.brightentime
  state['alarmset'] = True
  state['alarmtime'] = config.alarmtime
  state['alarming'] = False
  esnooze = Event()

  l = Process(target=light,args=(1,state))
  l.daemon = True
  l.start()

  w = Process(target=web,args=(1,state,esnooze))
  w.daemon = True
  w.start()

  s = Process(target=scheduler,args=(1,state,esnooze))
  s.daemon = True
  s.start()

  while l.is_alive() and w.is_alive() and s.is_alive():
    sleep(1)
