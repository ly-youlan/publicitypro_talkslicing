# -*- coding: utf-8 -*-

import datetime
import os
import re
import shutil
import traceback
from tqdm import tqdm
import json
import subprocess, shlex
from moviepy.editor import *
from PIL import Image, ImageDraw, ImageFont

from TalkAutomation.config.languages import ACRONYM_LANGUAGE_MAPPING, Language

from TalkAutomation.editing_utils.captions import (getCaptionsWithTime,
                                                   getSpeechBlocks)
from TalkAutomation.gpt.gpt_analyze import analyzeContent
from TalkAutomation.gpt.gpt_news import writeNews


from TalkAutomation.api_utils.ost_fast_api import convert_to_speech_block, audioToText, preprocess_transcription
from TalkAutomation.audio.audio_utils import extract_and_convert_audio, audioToTextWhipser, \
    preprocess_transcription_whisper
from TalkAutomation.engine.basic_content_engine import BacisContentEngine


class TalkSlicingEngine(BacisContentEngine):

    def __init__(self, src_url: str = ""):
        default_voice_module = None
        super().__init__()

        if src_url:
            self._db_src_url = src_url

        self.stepDict = {
            1: self._generateScript,
            2: self._analyzeContent,
            3: self._sliceAllClips,
            4: self._addSubtitlesToAllClips,
            5: self._addBackgroundToAllClips,
            6: self._editAndRenderShort
            # 1: self._generateScript,
            # 2: self._analyzeContent,
            # 3: self._sliceAllClips,
            # 4: self._addBackgroundToAllClips
        }

    def _generateScript(self):
        print("GPT start writing...")
        self.logger("自动化执行中：生成稿件")
        self.script = writeNews("")


    def _analyzeContent(self):
        print("GPT start analyzing...")
        self.logger("自动化执行中：(2/6) 分析视频内容")

        self._db_analyzed_speech_blocks = analyzeContent(json.dumps(self._db_speech_blocks))
        print(f"GPT sugggested cut:{self._db_analyzed_speech_blocks}")

        # standardlized and extract longest json
        self._db_edit_json = self.standardlized_and_extract_longest_json(self._db_analyzed_speech_blocks)

    def _sliceAllClips(self):
        self.logger("自动化执行中：(3/6) 切分各个片段")
        split_videos_paths = []
        clip_objects = []
        themes = []
        titles = []
        for block in self._db_edit_json['analyzed_speech_blocks']:
            theme = block['theme']
            tltle = block['title']
            clips = []
            for interval in block['time_intervals']:
                start_time = float(interval['start_time']) /1000 # 转换为秒
                end_time = float(interval['end_time']) /1000 # 转换为秒
                clip = VideoFileClip(self._db_src_url).subclip(start_time, end_time)
                clips.append(clip)

            # 将同一主题的所有视频片段剪辑在一起
            final_clip = concatenate_videoclips(clips)
            clip_objects.append(final_clip)
            themes.append(theme)
            titles.append(tltle)
        self.clip_objects = clip_objects
        self.clips_title = titles
        self.clips_theme = themes

    # # 使用主题作为文件名
    # output_filename = f"{theme}.mp4".replace(' ', '_').replace('/', '_')
    # output_path = f"{output_dir}/{output_filename}"
    #
    # # 输出剪辑后的视频到指定目录
    # final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
    # split_videos_paths.append(output_path)  # 将输出路径添加到列表中
    # self.split_videos_paths = split_videos_paths

    def _generate_subtitles_for_clip(self, clip):
        # 临时保存音频文件
        clip_subtitles = []
        temp_audio_path = '/Users/youlan/Coding/PublicityPro/public/temp/temp_audio.wav'

        # 从视频片段中提取音频并保存
        clip.audio.write_audiofile(temp_audio_path, codec='pcm_s16le', fps=16000)

        # 将音频文件转写成文本
        # clip_transcribe_json = audioToText(temp_audio_path)
        clip_transcribe_json = audioToTextWhipser(temp_audio_path, model_size="large")
        print(f"clip_transcribe_json:{clip_transcribe_json}")
        clip_subtitles = preprocess_transcription_whisper(clip_transcribe_json)
        print(f"clip_subtitle{clip_subtitles}")
        # 返回字幕数据
        return clip_subtitles

    def _add_subtitles_to_clip(self, clip, subtitles_data):
        font_path = '/Users/youlan/Library/Fonts/字小魂天工宋.ttf'

        # 字幕 clips 列表
        subtitles_clips = [clip]  # 确保原始视频片段也包含在内
        # 记得讯飞的是毫秒
        for subtitle in subtitles_data:
            # 解析每条字幕的时间戳和文本
            start_time = float(subtitle['begin'])
            end_time = float(subtitle['end'])
            text = subtitle['text']

            # 创建一个 TextClip 对象作为字幕
            subtitle_clip = TextClip(text, fontsize=150, color='white', font=font_path,
                                     size=(clip.size[0], clip.size[1] // 10)).set_position('bottom').set_duration(
                end_time - start_time).set_start(start_time)

            subtitles_clips.append(subtitle_clip)

        # 将原视频片段和字幕 clips 合并
        final_clip = CompositeVideoClip([clip] + subtitles_clips)
        return final_clip

    def _addSubtitlesToAllClips(self):
        self.logger("自动化执行中：(4/6) 生成视频字幕")

        # self.clip_objects = []
        # self.clip_objects.append(VideoFileClip(
        #     "/Users/youlan/Pictures/private/M4ROOT/CLIP/23年思政学风会议+采访/采访主机位-35mm-主声音/20231222_A0530.MP4"))
        # 假设 all_subtitles_data 包含了所有视频片段的字幕数据
        for i, clip in enumerate(self.clip_objects):
            subtitles_data = self._generate_subtitles_for_clip(clip)
            self.clip_objects[i] = self._add_subtitles_to_clip(clip, subtitles_data)

    def _add_background_to_clip(self, clip, background_image_path):
        # 加载背景图片
        background = ImageClip(background_image_path)
        background = background.set_duration(clip.duration)  # 确保背景图片持续时间与原视频一致

        # 调整原视频的大小和位置
        clip_resized = clip.resize(height=608)  # 调整原视频高度，宽度会按比例缩放
        clip_resized = clip_resized.set_position(('center', 'center'))  # 居中放置

        # 将原视频放置在背景之上
        final_clip = CompositeVideoClip([background, clip_resized], size=(1080, 1440))  # 假设目标尺寸为1080x1920
        return final_clip

    def _add_text_to_background(self, text, image_path, output_path="output_image.png", position=(40, 150),
                                font_path="/Users/youlan/Library/Fonts/字小魂天工宋.ttf", font_size=90,
                                text_color=(255, 255, 255)):

        # 打开图片
        image = Image.open(image_path)
        # 创建一个可以在给定图像上绘图的对象
        draw = ImageDraw.Draw(image)
        try:
            font = ImageFont.truetype(font_path, font_size)
        except IOError:
            # 如果指定的字体路径找不到，使用默认字体
            font = ImageFont.load_default()
        # 在指定位置添加文字
        draw.text(position, text, fill=text_color, font=font)
        # 保存图片
        image.save(output_path)
        print(f"Image saved as {output_path}")

        return output_path

    def _addBackgroundToAllClips(self):
        self.logger("自动化执行中：(5/6) 添加视频背景")
        # self.clip_objects 存储了所有的视频片段对象
        base_background_image_path = "/Users/youlan/Coding/PublicityPro/assets/img/background.png"
        base_title_background_path = "/Users/youlan/Coding/PublicityPro/assets/img"

        for i, clip in enumerate(self.clip_objects):
            title_background_path = f"{base_title_background_path}/{self.clips_title[i]}.png"
            temp = self._add_text_to_background(self.clips_title[i], base_background_image_path, title_background_path)
            background_image_path = self._add_text_to_background(self.clips_theme[i], temp, title_background_path,
                                                                 position=(40, 280),
                                                                 font_path="/Users/youlan/Library/Fonts/字小魂天工宋.ttf",
                                                                 font_size=50, text_color=(255, 255, 255))
            # 为每个视频片段添加背景
            self.clip_objects[i] = self._add_background_to_clip(clip, background_image_path)

    def _editAndRenderShort(self):
        self.logger("自动化执行中：(6/6) 渲染视频")

        output_dir = "/Users/youlan/Coding/PublicityPro/TalkAutomation/videos"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        for i, clip in enumerate(self.clip_objects):
            # 使用主题作为文件名
            output_filename = f"{self.clips_title[i]}.mp4".replace(' ', '_').replace('/', '_')
            output_path = f"{output_dir}/{output_filename}"

            # 输出剪辑后的视频到指定目录
            clip.write_videofile(output_path, codec="libx264", audio_codec="aac", ffmpeg_params=['-f', 'mp4'])

    def get_output_video_path(self):
        testpath = '/Users/youlan/Coding/PublicityPro/TalkAutomation/videos/挑战与成长_with_subtitles.mp4'
        return testpath


def main():
    videoPath = "/Users/youlan/Pictures/private/M4ROOT/CLIP/23年思政学风会议+采访/采访主机位-35mm-主声音/20231222_A0550.MP4"
    # Create an instance of TalkSlicingEngine
    talk_slicing_engine = TalkSlicingEngine(src_url=videoPath)
    num_steps = talk_slicing_engine.get_total_steps()

    try:
        # Perform the steps of the TalkSlicingEngine
        for step_number in range(1, num_steps + 1):
            talk_slicing_engine.stepDict[step_number]()
    except Exception as e:
        traceback.print_exc()
        print(f"Error in main function: {str(e)}")


if __name__ == '__main__':
    main()
