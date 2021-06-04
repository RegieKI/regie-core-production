## RegieKI Core

This repository contains code used to train and run the machine learning model at the heart of RegieKI.

__Note: This repository is a guide only. Many components specific to our setup, such as pretrained models, out trained model. And API Keys are not included in this repository.__

## Data preparation

Our raw data comes in the form of videos labeled with an emotion from each of the performers. The videos must be split into frames, and the aligned faces/bodies extracted. We then train a single model from all of the performers data which attempts to classify a given frame with an emotion.

The `datasets` module provides some utilities for managing our specific setup, where the raw data is stored in a Google Storage bucket. The `DBManager` can provide some statistics on data stored remotely and can also pre-process a local dataset. Preprocessing steps are covered shown in `DataDB.ipynb`.

Extraction of aligned faces and pose frames are coved in the `Extract.ipynb` and `ExractPose.ipynb` notebooks respectively. These two notebooks use exact models run on the PDACs prior to video streaming to ensure consistency between training and production data. Specifically we use exactly the same quantized version of mobile net. So pre-processing does require and Coral TPU.

## Training

Models are trained in `Train.ipynb`

## Live Inference

The live runner `live.py` serves the models such that it can receive video streams from the PDACs and run inference in realtime. Run with:

`python3 live.py --osc_IP IP_ADDRESS`

Where `IP_ADDRESS` is the endpoint from predictions and logging, in our case the media machine.

This script also controls the PDACs during the performance, setting the extraction model and which data are streamed. 

And OSC listener is opened on port `31636` which provides a endpoint accepting commands in the form `/mode/ -> <str>`. This correspond to the folloing states for the stage PDACs and the inference loop.

| Mode Symbol | ML Mode  | Pdac Mode            | Notes           |
|-------------|----------|----------------------|-----------------|
| pause       | off      | rtsp-only            |                 |
| simulate    | fake     | rtsp-only            |                 |
| face        | face     | face-extraction-rtsp |                 |
| body        | body     | pose-detection-rtsp  | Not implemented |
