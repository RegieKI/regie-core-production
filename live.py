
from device import Device
from model  import InferenceRunner
from api    import Api
from logger import Logger
from constants import mode_map
import threading
import argparse

import threading

import signal
import gi
gi.require_version('GLib', '2.0')
gi.require_version('Gtk', '3.0')
from gi.repository import GLib, Gtk

import time

device_configs = [
    ( "pdac-stage-01", "10.0.8.210" ),
    ( "pdac-stage-02", "10.0.8.211" ),
    ( "pdac-stage-03", "10.0.8.212" ),
    ( "pdac-stage-04", "10.0.8.213" ),
    ( "pdac-stage-05", "10.0.8.214" ),
]

logger = Logger()

class App():
    def __init__(self, args):
        self.mode = "init"
        self.inferenceRunner = InferenceRunner()
        self.running = False
        
        self.api = Api(args.osc_ips)
        logger.add_channel( self.api.send_log )
        self.api.set_mode_callback( self.setModeAll)

        self.devices = [ Device(name, ip) for name, ip in device_configs]

        #self.setModeAll("pause")
        self.setModeAll("debug")

        self.thread = threading.Thread(target=self.main_loop)
        
    def start(self):
        if(not self.running):
            logger.log("[APP] Starting inference thread!")
            self.running = True
            self.thread.start()
        else:
            logger.log("[APP] Thread already running!")

    def setModeAll(self, mode):
        if( mode in mode_map):
            self.mode = mode
            logger.log(f"[APP] Setting mode {mode}!")

            ml_mode   = mode_map[mode][0]
            pdac_mode = mode_map[mode][1]


            set_mode_threads = []
            set_mode_thread = threading.Thread(
                target = InferenceRunner.set_mode, 
                args = [ self.inferenceRunner, ml_mode ]) 

            set_mode_thread.start()
            set_mode_threads.append(set_mode_thread)
            
            for device in self.devices:
                set_mode_thread = threading.Thread(
                    target = Device.setMode, 
                    args = [ device, pdac_mode ]) 

                set_mode_thread.start()
                set_mode_threads.append(set_mode_thread)

            for set_mode_thread in set_mode_threads:
                set_mode_thread.join()

        else:           
            logger.log(f"[APP] Cant set invalid mode! {mode}")


    def main_loop(self):
        self.itr = 0
        while self.running:
            self.api.send_status(self.mode)
            try:
                count = 0
                for device in self.devices:
                    frame = device.getFrame()
                    if(frame is not None):
                        output = self.inferenceRunner.run_inference(device, frame)
                        if(output is not None):

                            logger.log(f"[APP]  {device.name} -> {output}")
                            self.api.send_data(device, output)
                            count += 1


                if count == 0:
                    time.sleep(0.5)
                else:
                    self.itr += count
                    logger.log(f"[APP] Iteration {self.itr}")

            except Exception as e:
                raise e

        print("Exiting Main loop")

    def exit(self):
        print("Exiting Main App")


        if( self.running ):
            print("Stopping main loop...")
            self.running = False
            self.thread.join()

        exit_threads = []
        for device in self.devices:        
            exit_thread  = threading.Thread(
                target = Device.exit, 
                args = [ device ]) 

            exit_thread.start()
            exit_threads.append(exit_thread)

        for exit_thread in exit_threads:
            exit_thread.join()

        print("Thread finished")


def main(args):

    app = App(args)
    app.start()

    GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, Gtk.main_quit)
    try:
        Gtk.main()
    except Exception as e:
        print(str(e))

    app.exit()
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--osc_ips', type=str, nargs='+', default=["127.0.0.1", "10.0.8.201"],
                        help='IP adress of the TD Machine')

    args = parser.parse_args()

    main(args)
    
