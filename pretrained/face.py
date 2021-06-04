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
import tflite_runtime.interpreter as tflite

import pretrained.common as common

Object = collections.namedtuple('Object', ['id', 'score', 'bbox'])

def load_labels(path):
    p = re.compile(r'\s*(\d+)(.+)')
    with open(path, 'r', encoding='utf-8') as f:
       lines = (p.match(line).groups() for line in f.readlines())
       return {int(num): text.strip() for num, text in lines}

class BBox(collections.namedtuple('BBox', ['xmin', 'ymin', 'xmax', 'ymax'])):
    """Bounding box.
    Represents a rectangle which sides are either vertical or horizontal, parallel
    to the x or y axis.
    """
    __slots__ = ()

def get_output(interpreter, score_threshold, top_k, image_scale=1.0):
    """Returns list of detected objects."""
    boxes = common.output_tensor(interpreter, 0)
    class_ids = common.output_tensor(interpreter, 1)
    scores = common.output_tensor(interpreter, 2)
    count = int(common.output_tensor(interpreter, 3))

    def make(i):
        ymin, xmin, ymax, xmax = boxes[i]
        return Object(
            id=int(class_ids[i]),
            score=scores[i],
            bbox=BBox(xmin=np.maximum(0.0, xmin),
                      ymin=np.maximum(0.0, ymin),
                      xmax=np.minimum(1.0, xmax),
                      ymax=np.minimum(1.0, ymax)))

    return [make(i) for i in range(top_k) if scores[i] >= score_threshold]



class FaceDetector:
    def __init__(self):

        self.model = 'pretrained/all_models/mobilenet_ssd_v2_face_quant_postprocess.tflite'
        labels =  'pretrained/all_models/coco_labels.txt'

        print('Loading {} with {} labels.'.format(self.model, labels))
        self.interpreter = common.make_interpreter(self.model)
        self.interpreter.allocate_tensors()
        self.labels = load_labels(labels)

    def get_faces(self, img):
        common.set_input(self.interpreter, img)
        self.interpreter.invoke()
        objs = get_output(self.interpreter, score_threshold=0.7, top_k=1)

        faces = []
        for obj in objs:
            box = (
                obj.bbox.xmin * img.width,
                obj.bbox.ymin * img.height,
                obj.bbox.xmax * img.width,
                obj.bbox.ymax * img.height                
            )

            w = box[2] - box[0]
            h = box[3] - box[1]

            center = (
                box[0] + w * 0.5,
                box[1] + h * 0.5
            )

            size = max(w, h)

            crop_box = (
                center[0] - size * 0.5,
                center[1] - size * 0.5,
                center[0] + size * 0.5,
                center[1] + size * 0.5              
            )


            face = img.crop(crop_box)
            face.resize((180, 180))

            faces.append(face)

        return faces





