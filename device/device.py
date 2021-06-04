import numpy as np
from .modes import PDAC_MODES
import requests
import threading
from requests.exceptions import ConnectionError
from logger import Logger, LogType

import gi
gi.require_version('Gst', '1.0')
gi.require_version('GLib', '2.0')
gi.require_version('GObject', '2.0')
from gi.repository import GLib, GObject, Gst
Gst.init(None)

logger = Logger()

TIMEOUT = 5

class Device:

    def __init__(self, name, ip_addr, port = 8888, rtsp_port = 11000):
        self.name      = name
        self.port      = port
        self.rtsp_port = rtsp_port
        self.ip_addr   = ip_addr
        self.condition = threading.Condition()
        self.newFrame  = False
        self.running   = False
        self.sample    = None
        self.frame     = None
        self.pipeline  = None
        self.newFrame  = False
        self.mode      = None
        self.counter   = 0


    def getFrame(self, size = (256, 256 )):
        if self.running:
            if self.newFrame:
                with self.condition:
                    sample = self.sample
                    self.sample = None
            
            if(self.newFrame):

                logger.log(f"[{self.name}] {self.counter:09d} New Frame")
                self.counter += 1
                buffer = sample.get_buffer()

                caps_format = sample.get_caps().get_structure(0)  # Gst.Structure

                # GstVideo.VideoFormat
                # video_format = GstVideo.VideoFormat.from_string(
                #     caps_format.get_value('format'))

                # w, h = caps_format.get_value('width'), caps_format.get_value('height')
                # c = utils.get_num_channels(video_format)

                w = 256
                h = 256
                c = 3

                buffer_size = buffer.get_size()
                shape = (h, w, c) if (h * w * c == buffer_size) else buffer_size
                self.frame = np.ndarray(shape=shape, buffer=buffer.extract_dup(0, buffer_size),
                                dtype=np.uint8)

                self.frame = np.squeeze(self.frame)  # remove single dimension if exists

            self.newFrame = False
            return self.frame
        else:
            return None


    def on_new_sample(self, sink):
        sample = sink.emit('pull-sample')
        #logger.log(f"[{self.name}] Sample")Timeo
        logger.log(f"[{self.name}] Closing ")

        if(self.pipeline):
            ret = self.pipeline.set_state(Gst.State.NULL)
            if(ret == Gst.StateChangeReturn.FAILURE):
                logger.log("[{self.name}] Error closing pipeline", LogType.WARNING)

            self.pipeline = None

        try:
            r = requests.post(f"http://{self.ip_addr}:{self.port}/stop/", timeout=TIMEOUT)
            self.running = False
        except ConnectionError as e:
            logger.log(f"[{self.name}] Stop timed out.", LogType.WARNING)

    def stop(self):
        logger.log(f"[{self.name}] Closing ")

        if(self.pipeline):
            ret = self.pipeline.set_state(Gst.State.NULL)
            if(ret == Gst.StateChangeReturn.FAILURE):
                logger.log("[{self.name}] Error closing pipeline", LogType.WARNING)

            self.pipeline = None

        try:
            r = requests.post(f"http://{self.ip_addr}:{self.port}/stop/")
            self.running = False
        except ConnectionError as e:
            logger.log(str(e), LogType.WARNING)


    def exit(self):
        self.stop()

    def setMode(self, mode):

        if(self.running):
            if( mode == self.mode):
                logger.log(f"[{self.name}] Already mode to  '{mode}'", LogType.WARNING)
                return
            else:
                logger.log(f"[{self.name}] Setting mode, but already running", LogType.WARNING)
                self.stop()


        if( mode  in PDAC_MODES):
            logger.log(f"[{self.name}] Setting mode to  '{mode}'")    
            try:
                modeDetails = PDAC_MODES[mode]
                r = requests.post(f"http://{self.ip_addr}:{self.port}/start/", json=modeDetails, timeout=TIMEOUT)

                if( modeDetails["sinks"]["rstp"] ):
                    stream_url = f"rtsp://{self.ip_addr}:{self.rtsp_port}/stream"
                    logger.log(f"[{self.name}] Setting up stream: '{stream_url}'")

                    command = f"rtspsrc location={stream_url} is_live=true latency=0 ! rtph264depay ! avdec_h264 ! tee name=t \
                        t. ! queue ! videoconvert ! video/x-raw,format=RGB,width=256,height=256,framerate=30/1 ! appsink name=appsink emit-signals=True \
                        t. ! queue ! videoconvert ! autovideosink"
                        
                    self.pipeline = Gst.parse_launch(command)
                    appsink = self.pipeline.get_by_name('appsink')
                    appsink.connect('new-sample', self.on_new_sample)

                    logger.log(f"[{self.name}] Pipeline:\n{command}")

                    self.pipeline.set_state(Gst.State.PLAYING)

                logger.log(f"[{self.name}] Setting mode to '{mode}'")    
                self.mode = mode
                self.running = True

            except ConnectionError as e:
                logger.log(f"[{self.name}] Set mode timed out.", LogType.WARNING)
                self.running = False
        else:
            logger.log(f"[{self.name}] Mode '{mode}' not defined", LogType.WARNING)
