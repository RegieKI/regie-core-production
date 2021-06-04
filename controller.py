from constants import mode_map
from osc4py3.as_eventloop import *
from osc4py3 import oscmethod as osm
from osc4py3 import oscbuildparse
import curses
import os
import threading
import time



class Controller():
    def __init__(self, snd_port=31636, rcv_port=31637 ):

        self.log = []

        osc_startup()

        osc_udp_client( "127.0.0.1", snd_port, "sender")

        osc_udp_server( "127.0.0.1", rcv_port, "receiver")
        osc_method("/*", self.debug_log, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATA)
 



    def process(self):
        osc_process()

    def set_mode(self, mode):
        addr = f"/mode"  
        msg = oscbuildparse.OSCMessage(addr, None, mode)
        osc_send(msg, "sender")

    def debug_log(self, addr, data):
        self.log.append(''.join(data))



def draw(win, current_mode, log):
    win.clear()

    win.addstr(f"Menu:\n") 
    for i, (mode, (pdac_mode, ml_mode)) in enumerate(mode_map.items()):
        win.addstr(f"\t{i + 1} : {mode}\t ({pdac_mode}, {ml_mode})\n")      
    win.addstr(f"\n")  
    win.addstr(f"Current: {current_mode}")
    win.addstr(f"\n")  
    win.addstr(f"------------------------------------\n")  

    for line in log:
        try:
            win.addstr(f"{line.encode('utf-8')}\n")
        except curses.error as e: 
            pass

def main(win):

    controller = Controller()

    win.nodelay(False) 

    mode = ""
    draw(win, mode, controller.log )

    running = True
    def loop():
        while(running):
            draw(win, mode, controller.log )
            controller.process()

            time.sleep(0.01)

    thread = threading.Thread(target=loop)
    thread.start()

    while True:   
        time.sleep(0.01)
        try:                
            selected = win.getkey()
            try:
                selected = int(selected)
            except ValueError:
                continue

            if(selected <= len(mode_map) and selected > 0 ):
                mode = list(mode_map.items())[selected - 1]
                mode_str = str(mode[0])
                controller.set_mode(mode_str)

        except curses.error as e:  
            pass     


curses.wrapper(main)