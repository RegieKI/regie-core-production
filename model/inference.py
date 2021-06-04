import numpy as np
from logger import Logger, LogType
from .model import *
from datetime import datetime


logger = Logger()

class InferenceRunner():

    def __init__(self):
        self.num_labels = 7

        self.model_types = {
            "off"  : None,
            "fake" : FakeModel,
            "face" : FaceModel,
            "body" : BodyModel
        }
        self.model = None

    def set_mode(self, mode):
        logger.log(f"[Inference] Setting ml_mode {mode}")
        if mode in self.model_types :
            self.mode = mode
            if(self.model_types[mode] is not None):
                self.model = self.model_types[mode]()
            else:
                self.model = None
        else:
            logger.log(f"[Inference] ml_mode {mode} not recognised!", LogType.ERROR)

    def run_inference(self, device, frame):
        if self.model is not None:
            t0 = datetime.now()
            output = self.model.run_inference(frame)
            t1 = datetime.now()
            print(f"Inference: {(t1 - t0):04f}")
            return output
        else:
            pass
