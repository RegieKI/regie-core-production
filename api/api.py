from osc4py3.as_eventloop import *
from osc4py3 import oscmethod as osm
from osc4py3 import oscbuildparse
from logger import Logger, LogType
import time


from constants import emotions

import threading

import logging
logging.basicConfig(format='%(asctime)s - %(threadName)s ø %(name)s - '
    '%(levelname)s - %(message)s')
osclogger = logging.getLogger("osc")
osclogger.setLevel(logging.ERROR)


logger = Logger()

class Api:

    def __init__(self, snd_ips, rcv_ip="0.0.0.0", snd_port=31637, rcv_port=31636 ):
        osc_startup(logger=osclogger)



        self.clients = [ f"client{i:02d}" for i, _ in enumerate(snd_ips)]
        for client, snd_ip in zip(self.clients, snd_ips):
            logger.log(f"Setting up '{client}' on {snd_ip}:{snd_port}")
            osc_udp_client(snd_ip, snd_port, client)

        osc_udp_server( rcv_ip, rcv_port, "server")
        logger.log(f"Setting up server on '{rcv_ip}':{rcv_port}")
        osc_method("/*", self.debug_log, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATA)

        self.thread = threading.Thread(target=self.process)
        self.running = True
        self.thread.start()


    def exit(self):
        self.send_log(f"[API] Stopping API loop")
        self.running = False
        self.thread.join()
        osc_terminate()
        print("Stopped API")

    def process(self):
        self.send_log(f"[API] Starting API loop")
        while(self.running):
            osc_process()

        osc_process()

    def debug_log(self, addr, data):
        logger.log(f"{addr} / {data}", LogType.NOTICE)

    def set_mode_callback(self, callback):
        def parse_mode(data):
            return ''.join(data)

        method = lambda m : callback(parse_mode(m))
        osc_method("/mode", method, osm.OSCARG_DATA)

    def send(self, msg):
        for client in self.clients:            
            osc_send(msg, client)

    def send_data(self, device, data):    
        for i, emotion in enumerate(emotions):
            addr = f"/data/{device.name}/{emotion}"  
            msg = oscbuildparse.OSCMessage(addr, None, [float(data[i])])
            self.send(msg)

    def send_log(self, data):
        addr = "/log"        
        msg = oscbuildparse.OSCMessage(addr, None, data)
        self.send(msg)

    def send_status(self, status):
        addr = "/status"        
        msg = oscbuildparse.OSCMessage(addr, None, status)
        self.send(msg)
