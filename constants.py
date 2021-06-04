from collections import OrderedDict


mode_map = OrderedDict({
    "pause"    : ("off" , "rtsp-only"),
    "simulate" : ("fake", "rtsp-only"),
    "face"     : ("face", "face-extraction-rtsp"),
    "body"     : ("body", "pose-detection-rtsp"),
    "debug"    : ("off" , "debug")
})


emotions = [
  "angst",
  "freude",
  "liebe",
  "trauer",
  "uberraschung",
  "verachtung",
  "wut"
]

num_emotions = len(emotions)
