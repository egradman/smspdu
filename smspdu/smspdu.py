#Copyright (c) 2009 Eric Gradman
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.

import serial
import time
from cStringIO import StringIO
from math import ceil
from binascii import unhexlify, hexlify
from itertools import *

class T39(object):
  def __init__(self, file="/dev/tty.T39-SerialPort1-1"):
    self.file = file

    self.ser = serial.Serial(file, 115200)
    self.pdu = PDU()

    for s in ('ATZ', 'AT+CPMS="ME","ME","ME"', 'AT+CNMI=3,3,2,0,0'):
      self.ser.write("%s\r" % s)

      while True:
        d=self.ser.readline()
        print d
        if d.startswith("OK"):
          break
    
  def fetch(self):
    s = self.ser.readline()
    return self.pdu.decode(s)

class PDU(object):
  def decode(self, s):
    s = unhexlify(s)
    d = StringIO(s)
    
    # parse SMSC information
    p = {}
    p['smsc_len'] = d.read(1)
    p['type_of_address'] = d.read(1)
    p['sc_num'] = self.unsemi(d.read(ord(p['smsc_len'])-1))


    p['msg_type'] = d.read(1)
    p['address_len'] = d.read(1)
    p['type_of_address'] = d.read(1)

    p['sender_num'] = self.unsemi(d.read(int(ceil(ord(p['address_len'])/2.0))))
    p['pid'] = d.read(1)
    p['dcs'] = d.read(1)
    p['ts'] = d.read(7)
    p['udl'] = d.read(1)
    p['user_data'] = d.read(ord(p['udl']))
    p['user_data'] = self.decode_user_data(p['user_data'])

    return p

  def decode_user_data(self, s):
    """PDU user data is stored in a strange 7-bit packed format"""
    bytes = map(ord, s)
    strips = cycle(range(1,9))
    out = ""
    c = 0    # carry
    clen = 0 # carry length in bits
    while len(bytes):
      strip = strips.next()
      if strip == 8:
        byte = 0
        ms = 0
        ls = 0
      else:
        byte = bytes.pop(0)
        # take strip bytes off the top
        ms = byte >> (8-strip)
        ls = byte & (0xff >> strip)
      #print "%d byte %x ms %x ls %x" % (strip, byte, ms, ls)

      # append the previous
      byte = ((ls << clen) | c) & 0xff
      out += chr(byte)

      c = ms
      clen = strip % 8

    if strip == 7:  out += chr(ls) # changed 6/11/09 to incorporate Carl's suggestion in comments
    return out

  def unsemi(self, s):
    """turn PDU semi-octets into a string"""
    l = list(hexlify(s))
    out = ""
    while len(l):
      out += l.pop(1)
      out += l.pop(0)
    return out
