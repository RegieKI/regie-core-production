from google.cloud import storage
from collections import defaultdict
import re
from datetime import datetime
from pathlib import Path
import json
from tqdm import tqdm

class Session():
  def __init__(self ):
    self.dirty               = 0
    self.files_config_path   = ""
    self.files_config_date   = ""
    self.files_hr_path       = ""
    self.files_hr_samples    = 0
    self.files_audio_files   = ""
    self.files_audio_bytes   = 0
    self.files_video_files   = ""
    self.files_video_bytes   = 0


class DataSource:
  def __init__(self, scan):
    self.scan = scan
    self.files    = defaultdict(list)
    self.sessions = {}

    self._setup()

  def _setup(self):
    print("First pass..")

    for path in self._get_all_paths():
        expr = re.compile(r"^(.*?)\/recordings\/(.*?)\/(.*)$")
        match = expr.match(path)
        if(match):
            recording_string = match.group(2)
            self.files[recording_string].append(path)

            if( recording_string not in self.sessions):
              self.sessions[recording_string] = Session()

    print("Second pass..")
    for recording_string, files in self.files.items():
      audio_files    = []
      video_files    = []

      for file in files:
        filename = file.split("/")[-1]
        
        if filename == "config.json":
          self.sessions[recording_string].files_config_path  = file
          continue

        if filename == "heartrate.hrt":
          self.sessions[recording_string].files_hr_path  = file
          continue

        if filename.startswith("AUDIO"):
          audio_files.append(file)         
          continue

        if filename.startswith("VIDEO"):
          video_files.append(file)         
          continue

        if filename.startswith(".dirty"):
          self.sessions[recording_string].dirty = 1       
          continue


      self.sessions[recording_string].files_audio_files  = ",".join(audio_files)
      self.sessions[recording_string].files_video_files  = ",".join(video_files)


      self.populate_extra_data(self.sessions[recording_string], files)

  def _get_file_string(self, file):   
    raise NotImplementedError()

  def _get_file_size(self, file):   
    raise NotImplementedError()


  def populate_extra_data(self, session, files):

    if session.files_config_path is not "":
        json_str  = self._get_file_string(session.files_config_path)
        try:
          config = json.loads(json_str)        
          dt_obj = datetime.strptime(config["time-received"], "%Y%m%d-%H%M%S")
          session.files_config_date = dt_obj.strftime("%Y%m%d-%H:%M:%S")
        except json.JSONDecodeError as e:
          print(f"Config corrupted in {session}.\n{e}")

    if session.files_hr_path is not "":
        txt  = self._get_file_string(session.files_hr_path)
        session.files_hr_samples    = len(txt.split('\n'))

    # Audio 
    audio_files  = session.files_audio_files.split(",")
    if len(audio_files) > 0  :
        a_size = [ self._get_file_size(af) for af in audio_files if af is not "" ]
        session.files_audio_bytes = sum(a_size)

    video_files  = session.files_video_files.split(",")
    if len(video_files) > 0  :
        v_size = [ self._get_file_size(vf) for vf in video_files if vf is not ""  ]
        session.files_video_bytes = sum(v_size)  

  def get_recordings(self):
    return self.files

  def get_file_data(self, recording_string):
    return (
      self.sessions[recording_string].dirty,
      self.sessions[recording_string].files_config_path,
      self.sessions[recording_string].files_config_date,
      self.sessions[recording_string].files_hr_path    ,
      self.sessions[recording_string].files_hr_samples ,
      self.sessions[recording_string].files_audio_files,
      self.sessions[recording_string].files_audio_bytes,
      self.sessions[recording_string].files_video_files,
      self.sessions[recording_string].files_video_bytes
    )

  def _get_all_paths(self):        
    raise NotImplementedError()

class DataSourceRemote(DataSource):
  def __init__(self, scan=False, bucket = "regie-cloud-data", project = "RegieKi"):
    self.storage_client = storage.Client(project=project)
    self.data_bucket = self.storage_client.get_bucket(bucket)

    super().__init__(scan)

  def _get_all_paths(self):    
    return [ blob.name for blob in self.data_bucket.list_blobs()]

  def _get_file_string(self, file):   
    config_blob = self.data_bucket.get_blob(file)
    return config_blob.download_as_string().decode()

  def _get_file_size(self, file):   
    return self.data_bucket.get_blob(file).size

class DataSourceLocal(DataSource):
  def __init__(self, scan=False, data_root = "/media/regieki/data/RegieKI/data/regie-cloud-data"):

    self.data_root = data_root
    super().__init__(scan)


  def _get_all_paths(self):  
    p = Path(self.data_root)  
    paths = [ str(path) for path in p.glob("**/*") ]
    print(paths)
    return paths

  def _get_file_string(self, file):   
    data = ""
    with open (file, "r") as f:
        data=f.read()

    return data

  def _get_file_size(self, file):   
    return Path(file).stat().st_size