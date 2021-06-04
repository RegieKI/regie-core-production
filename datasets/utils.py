
from tqdm import tqdm
from datetime import datetime
import sqlite3
import json
import re

from collections import defaultdict


from .datasource import DataSourceRemote, DataSourceLocal

class DbManager:

  def __init__(self, db_path, data_is_local = True, populate = True):
    if(data_is_local):
      self.datasource = DataSourceLocal(scan = True)  
    else: 
      self.datasource = DataSourceRemote(scan = True)

    # Create table
    self.conn = sqlite3.connect(db_path)      
    self.cur = self.conn.cursor() 

    if populate:
      self.populate()


  def populate(self):
    try:
      self.conn.execute( 'DROP TABLE recordings')
    except:
       pass
       
    self.conn.execute('''CREATE TABLE recordings (
        rec_device          text, 
        rec_label           text, 
        rec_target          integer, 
        rec_tags            text, 
        rec_slabel          text, 
        rec_exercise        text, 
        rec_complexity      text, 
        rec_date            string, 
        rec_dirty           integer, 
        files_config_path   text, 
        files_config_date   text,
        files_hr_path       text, 
        files_hr_samples    integer,
        files_audio_files   text,
        files_audio_bytes integer,
        files_video_files   text,
        files_video_bytes  integer )''')
    

    recording_strings = self.datasource.get_recordings()
    
    print(f"{len(recording_strings)} Files found. Populating database...")
    for recording_string in  recording_strings:
        self.create_recording(recording_string)

  def get_dataset(self, devices, slabels):

    data = defaultdict(dict)

    for device in devices:
      for slabel in slabels:

        res = self.cur.execute("""
          SELECT files_video_files, files_video_bytes
          FROM recordings
          WHERE 
            rec_device = (?) AND
            rec_slabel = (?)  AND
            rec_dirty = 0  AND
            files_video_files<>"" AND
            files_video_bytes > (?)
          """, (device, slabel, 200000)
        )

        data[device][slabel] = res.fetchall()

    return data
    
  def create_recording(self, recording_string):
    try:
      rec_data = DbManager.parse_string(recording_string)
    except ValueError as e:
      print(e)
      print(f"Could not parse '{recording_string}'")
      return None



    file_data = self.datasource.get_file_data(recording_string)

    data = (rec_data + file_data )

    #print(data)

    self.cur.execute("insert into recordings values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", data)
    self.conn.commit()

  def parse_string(recording_string):
    expr = re.compile(r"^(.*?)\_(.*?)\_(.*?)\_(.*?)\_(.*?)\_(.*)$")
    match = expr.match(recording_string)
    
    if match:

      rec_device     = match.group(1)
      rec_target     = match.group(2)
      rec_tags       = ",".join(match.group(3).split('-'))
      rec_label      = match.group(4)

      exercise   = match.group(5).split('-')

      if(len(exercise) == 3):
        rec_slabel     = exercise[0]
        rec_exercise   = exercise[1]
        rec_complexity = exercise[2]
      else:
        raise ValueError("Exercise string failed parse!")

      rec_date       = match.group(6)

      return (  rec_device,
                rec_label, 
                rec_target, 
                rec_tags, 
                rec_slabel,
                rec_exercise,
                rec_complexity, 
                rec_date          )
    else:
      raise ValueError("Regex match failed!")

  def get_total_number(self):
    self.cur.execute("select count(*) from recordings")
    num = self.cur.fetchone()
    if(num):
        return int(num[0])
    else:
        return 0

  def print_info(self):

    print(""" ------------------------
    {} entries found
        {}
      """.format(
          self.get_total_number(),
          self.cur.execute("select distinct rec_device from recordings").fetchall()
      ))
