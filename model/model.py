import numpy as np
from PIL import Image
import os
from logger import Logger

from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential

import time

from constants import num_emotions

logger = Logger()


def getFaceModel():
    model = Sequential([
    layers.experimental.preprocessing.RandomContrast(0.2, 
                                                    input_shape=(180, 180, 3)),
    layers.experimental.preprocessing.Rescaling(1./255),
    layers.Conv2D(16, 3, padding='same', activation='relu'),
    layers.MaxPooling2D(),
    layers.Conv2D(32, 3, padding='same', activation='relu'),
    layers.MaxPooling2D(),
    layers.Conv2D(64, 3, padding='same', activation='relu'),
    layers.MaxPooling2D(),
    layers.Dropout(0.2),
    layers.Flatten(),
    layers.Dense(128, activation='relu'),
    layers.Dense(num_emotions)
    ])


    model.compile(optimizer='adam',
                    loss=keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                    metrics=['accuracy'])


    return model


class Model():

    def run_inference(self, frame):
        raise NotImplementedError()

class FakeModel(Model):

    def run_inference(self, frame):
        logger.log(f"Dummy inference")
        output = np.random.rand((7))
        time.sleep(0.5)
        return output



class FaceModel(Model):

    def __init__(self):
        self.model = getFaceModel()

        checkpoint_dir = "models/checkpoints/cp.ckpt"
        self.model.load_weights(checkpoint_dir)
        print(f"Loaded model! {checkpoint_dir}")


    def run_inference(self, frame):
        # This is slow! dont do this
        im = Image.fromarray(frame).resize((180, 180))
        np_img = np.asarray(im).reshape( 1, 180, 180, 3)
        labels = self.model.predict(np_img)
        return labels[0]


class BodyModel(Model):
    pass

