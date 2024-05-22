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
            1: self._transcribeAudio,
            2: self._analyzeContent,
            3: self._sliceAllClips,
            4: self._addSubtitlesToAllClips,
            5: self._addBackgroundToAllClips,
            6: self._editAndRenderShort
            # 1: self._transcribeAudio,
            # 2: self._analyzeContent,
            # 3: self._sliceAllClips,
            # 4: self._addBackgroundToAllClips
        }

    def _transcribeAudio(self):
        self.logger("自动化执行中：(1/6) 转写视频文本")

        # # xunfei
        # self._db_transcribe_json = audioToText(
        #     extract_and_convert_audio(self._db_src_url, target_format='wav', sample_rate=16000, channels=1))
        # print(f"transcribe_josn:{self._db_transcribe_json}")
        # self._db_speech_blocks = preprocess_transcription(self._db_transcribe_json)
        # print(f"_db_speech_blocks:{self._db_speech_blocks}")

        # whipered
        # whispered = audioToTextWhipser(
        #     extract_and_convert_audio(self._db_src_url, target_format='wav', sample_rate=16000, channels=1),
        #     model_size='small')
        # # print(f"whispered:{whispered}")
        # self._db_speech_blocks = getSpeechBlocks(whispered, silence_time=0.8)
        # print(f"speech_blocks:{self._db_speech_blocks}")

        self._db_speech_blocks = [[[0, 1.42], '好,可以开始了。'], [[7.1, 11.3], '蕭老师,您好。请问您在深大多少年了?'],
                                  [[12.18, 19.0], '我在深大24年了。五年在深大读书,然后现在工作已经19年了。'],
                                  [[19.92, 33.16],
                                   '那您在毕业的时候是为什么想要做这份课程呢?因为喜欢跟学生打交道,是喜欢一直一直跟学生打交道,所以选择了做辅导员这个岗位。'],
                                  [[34.04, 47.38],
                                   '希望,希望这辈子的工作都是跟学生打交道。如果说您现在可以拥有一个超能力,您会选择用什么样的超能力来更好的支持您的学生呢?'],
                                  [[48.2, 69.28],
                                   '我现在希望我是一个魔法女巫。可以把,把所有学生的烦恼,阴谋情绪都给吸引过来,然后呢,把它做成世界上最快乐的糖果。然后让他们吃下去能感受到,每天都感受到世界上最快乐的那种感觉。'],
                                  [[70.72, 75.82], '如果今年的工作要用三个词来概括,这三个词会是什么呢?'],
                                  [[76.74, 99.94],
                                   '嗯,今年的工作啊,对我而言是忙碌,学习,再出发。因为,就是已经做了这么多年辅导员了,直到今年才发现,还有很多很多要学的。所以希望是今年的学习之余,能再出发,再去创造一下辅导员的其他奇迹。'],
                                  [[101.78, 109.26],
                                   '在跟学生相处的过程中,会不会有一些负面的情绪,您是如何来排解这些情绪的呢?'],
                                  [[110.42, 118.12],
                                   '嗯,负面的情绪。就是,有些情绪肯定会有,但是做辅导员年限越久,就会越来越少。'],
                                  [[119.5, 125.36], '排解这个,最好的方法就是,遛狗,逗猫,打孩子。'],
                                  [[126.5, 127.38], '不行的话就骂一下老公吧。'], [[129.52, 139.74],
                                                                                 '那今年的工作,您感觉累吗?挺累的。每一年的工作其实都挺累的。辅导员的工作是越来越细,肯定会越来越累。'],
                                  [[141.28, 153.02],
                                   '嗯。那在累的同时,今年有没有什么收获呢?今年我最大的收获是觉得,我收获了一个很好很好的小伙伴团队。'],
                                  [[153.98, 180.14],
                                   '因为在这之前,学院里的辅导员不多,所以始终没有是一个很积极相向的团队。然后现在我有了一个非常好的团队,有一帮很可爱的小伙伴。还有,就是所有人都能互相保护,也就是,所有人都能互相保护。所有人都能互相为对方着想,也互相为对方补台。然后永远都是遇到事情一起上。这个是我觉得今年最大的收获。'],
                                  [[181.3, 187.4], '那么在这样繁忙的工作中,您是如何保持动力以及积极的心态呢?'],
                                  [[188.38, 194.46], '我相信力量吧。力量应该说是从三个方面。'],
                                  [[195.4, 231.7],
                                   '一个是学生给我的力量。真的是每年每年看着那些学生成功,看着学生的喜怒哀乐,然后看着他们一步步跨过很多坎儿。他们给我的力量很足。第二个方面是我的小伙伴团队给我的力量。真的是每一件事情,大家都一起拼搏,一起努力,然后这个力量很足。第三个力量呢,应该说是家里面给的力量。因为家里人都非常支持我这个工作,所以说始终他们是最坚强的后盾。'],
                                  [[232.9, 239.02], '那么让你坚持二十年如一日当辅导员的理由是什么呢?'],
                                  [[240.94, 244.06], '还是喜欢跟学生打交道,爱学生。'], [[246.26, 246.6], '就这个。'],
                                  [[249.4, 254.7], '讲完了。还有一个问题是您这边要不要对学生们说一句话的话。你想说什么?'],
                                  [[256.52, 260.64], '人生苦短,及时行乐。'], [[262.72, 263.66], '好,让我一下。']]

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
