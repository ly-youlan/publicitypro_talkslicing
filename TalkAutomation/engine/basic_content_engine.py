from abc import ABC
from moviepy.editor import *
import subprocess
import re
import json

class BacisContentEngine(ABC):
    def __init__(self):
        self.default_logger = lambda _: None
        self.logger = self.default_logger
        self.stepDict = {}

    def get_total_steps(self):
        return len(self.stepDict)


    def get_audio_path(self):
        video = VideoFileClip(self._db_src_url)
        audio = video.audio
        audio_file_path = self._db_src_url.rsplit('.', 1)[0] + '.wav'
        audio.write_audiofile(audio_file_path)
        return audio_file_path

    def get_video_duration(self,video_path):
        # 使用ffmpeg获取视频信息
        result = subprocess.run(["ffmpeg", "-i", video_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                text=True)

        # 从ffmpeg输出中搜索视频时长
        duration_match = re.search(r"Duration: (\d+:\d+:\d+\.\d+)", result.stderr)
        if duration_match:
            return duration_match.group(1)
        else:
            raise ValueError("Could not find video duration")

    def standardlized_and_extract_longest_json(self,input_str):
        json_match = re.search(r'\{.*\}', input_str)
        if json_match:
            json_data = json_match.group()
            try:
                # 尝试解析JSON数据
                json_dict = json.loads(json_data)
                # print(f"GPT sugggested cut(json):{json_dict}")
                # self._db_edit_json = json_dict
                return json_dict
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                return None
        else:
            print("No JSON data found in the string.")

    def set_logger(self, logger):
        self.logger = logger