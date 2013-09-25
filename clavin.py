#! /usr/bin/env python
import socket
import logging
import json

log = logging.getLogger('mc-clavin')
clavin_socket = None
clavin_socket_file = None

def connect(host="127.0.0.1", port=4000):
    global clavin_socket, clavin_socket_file, log
    try:
      clavin_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      clavin_socket.connect((host, port))
      clavin_socket_file = clavin_socket.makefile('r') 
    except socket.error, msg:
      log.error("CLAVIN: Unable to connect to CLAVIN server at "+host+":"+str(port))
      log.error(msg[1])
      return False
    log.info("CLAVIN: Connected to CLAVIN server at "+host+":"+str(port))
    return True

def locate(text):
    clavin_socket.send(text.encode('utf-8')+"\n")
    byte_count = 0
    results = clavin_socket_file.readline()
    log.info("CLAVIN: received "+str(len(results))+" bytes of from a locate request")
    log.info(results)
    return json.loads(results)

def close():
    global clavin_socket
    clavin_socket.close()
    log.info("Closed CLAVIN server")
