# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import collections
import numpy as np
import os
from PIL import Image
import re
import tensorflow.lite as tflite

import tensorflow as tf
import enum
import collections

class KeypointType(enum.IntEnum):
  """Pose kepoints."""
  NOSE = 0
  LEFT_EYE = 1
  RIGHT_EYE = 2
  LEFT_EAR = 3
  RIGHT_EAR = 4
  LEFT_SHOULDER = 5
  RIGHT_SHOULDER = 6
  LEFT_ELBOW = 7
  RIGHT_ELBOW = 8
  LEFT_WRIST = 9
  RIGHT_WRIST = 10
  LEFT_HIP = 11
  RIGHT_HIP = 12
  LEFT_KNEE = 13
  RIGHT_KNEE = 14
  LEFT_ANKLE = 15
  RIGHT_ANKLE = 16


def get_output(interpreter, score_threshold):
    pass


Pose = collections.namedtuple('Pose', ['keypoints', 'score'])

class BodyDetector:

    num_keypoints = int(KeypointType.RIGHT_ANKLE + 1)
    size = (641, 481)

    def __init__(self):


            posenet_decoder_delegate
        ]

        self.model = "./pretrained/posenet/posenet_mobilenet_v1_075_481_641_quant_decoder_edgetpu.tflite"

        print('Loading {}'.format(self.model))

        self.interpreter =  tflite.Interpreter(
            model_path=self.model,
            experimental_delegates=delegates)

        self.interpreter.allocate_tensors()

    def get_pose(self, image):
        pose = None


        image = image.convert("RGB").resize(self.size)
        input_img = np.expand_dims(np.asarray(image), axis=0)
        
        interpreter = self.interpreter

        interpreter.set_tensor(interpreter.get_input_details()[0]["index"], input_img)

        interpreter.invoke()

        def get_output(idx):
            return np.squeeze( interpreter.tensor( interpreter.get_output_details()[idx]['index'])() )

        keypoints       = get_output(0)
        keypoint_scores = get_output(1)
        pose_scores     = get_output(2)
        num_poses       = get_output(3)

        poses   = []
        y_means = []

        if(num_poses > 0):
            for i in range(int(num_poses)):
                pose_score = pose_scores[i]

                if(pose_score < 0.6 ):
                    continue

                pose_keypoints = np.zeros((17, 3))

                for j in range(self.num_keypoints):
                    y, x = keypoints[i, j]
                    s    = keypoint_scores[i, j]

                    pose_keypoints[j, 0] = max(min(x / self.size[0], 1.0), 0.0)
                    pose_keypoints[j, 1] = max(min(y / self.size[1], 1.0), 0.0)
                    pose_keypoints[j, 2] = max(min(s          , 1.0), 0.0)
                
                y_means.append( np.mean(pose_keypoints[:,1]) )
                poses.append(Pose(pose_keypoints, pose_score))

            y_means = np.absolute(np.asarray(y_means) - 0.5)
            middle_index = np.argmin(y_means) 

            pose = poses[middle_index]

        return pose



