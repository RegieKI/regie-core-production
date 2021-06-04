PDAC_MODES = {
    "debug" : {
    "session-id" : "debug",
        "sources" : {
            "audio"     : { "active" : False },
            "video"     : { "active" : True  },
            "heartrate" : { "active" : False },
        },
        "inference"  : None,
        "transform"  : False,
        "sinks" : {
            "rstp"   : { "active" : True  },
            "file"   : { "active" : False },
            "window" : { "active" : False },
        }           
    },  
    "rtsp-only" : {
        "session-id" : "live",
        "sources" : {
            "audio"     : { "active" : False },
            "video"     : { "active" : True  },
            "heartrate" : { "active" : False },
        },
        "inference"  : None,
        "transform"  : False,
        "sinks" : {
            "rstp"   : { "active" : True  },
            "file"   : { "active" : False },
            "window" : { "active" : False },
        }           
    },  
    "face-extraction-rtsp" : {
        "session-id" : "face-extraction",
        "sources" : {
            "audio"     : { "active" : False },
            "video"     : { "active" : True  },
            "heartrate" : { "active" : False },
        },
        "inference"  : "face-extraction",
        "transform"  : True,
        "sinks" : {
            "rstp"   : { "active" : True  },
            "file"   : { "active" : False },
            "window" : { "active" : False },
        }            
    },  
    "pose-detection-rtsp" : {
        "session-id" : "pose-detection",
        "sources" : {
            "audio"     : { "active" : False },
            "video"     : { "active" : True  },
            "heartrate" : { "active" : False },
        },
        "inference"  : "pose-detection",
        "transform"  : None,
        "sinks" : {
            "rstp"   : { "active" : True  },
            "file"   : { "active" : False },
            "window" : { "active" : False },
        }           
    }
}
