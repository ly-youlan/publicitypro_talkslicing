import os
import subprocess

import yt_dlp


CONST_CHARS_PER_SEC = 20.5  # Arrived to this result after whispering a ton of shorts and calculating the average number of characters per second of speech.

WHISPER_MODEL = None

from moviepy.editor import VideoFileClip
from pydub import AudioSegment
import os


def convert_audio_properties(audio_path, target_format='wav', sample_rate=16000, channels=1):
    # 加载音频文件
    audio = AudioSegment.from_file(audio_path)

    # 设置单声道
    if channels == 1:
        audio = audio.set_channels(1)

    # 设置采样率
    audio = audio.set_frame_rate(sample_rate)

    # 构建目标音频文件的路径
    target_path = os.path.splitext(audio_path)[0] + f'.{target_format}'

    # 根据格式保存音频文件
    if target_format.lower() == 'wav':
        audio.export(target_path, format='wav')
    elif target_format.lower() == 'pcm':
        audio.export(target_path, format='raw')
    elif target_format.lower() == 'mp3':
        audio.export(target_path, format='mp3')
    else:
        return "Unsupported format."

    return target_path


def extract_and_convert_audio(video_path, target_format='wav', sample_rate=16000, channels=1):
    # 确保视频文件存在
    if not os.path.exists(video_path):
        return "Video file does not exist."
    try:
        # 加载视频文件
        video = VideoFileClip(video_path)
        # 构建临时音频文件的路径
        temp_audio_path = os.path.splitext(video_path)[0] + '_temp.wav'
        # 从视频中提取音频并保存为临时WAV格式
        video.audio.write_audiofile(temp_audio_path)
        # 调整音频属性并保存为目标格式
        final_audio_path = convert_audio_properties(temp_audio_path, target_format, sample_rate, channels)
        # 返回最终音频文件的路径
        print(f"extract audio path: {final_audio_path}")
        return final_audio_path
    except Exception as e:
        # 如果遇到任何错误，返回错误消息
        return f"An error occurred: {e}"

def preprocess_transcription_whisper(data):
    processed_data = []
    for item in data['segments']:
        begin_time = item['start']
        end_time = item['end']
        text = item['text']

        # Append the structured information to the processed_data list
        processed_data.append({
            'begin': begin_time,
            'end': end_time,
            'text': text
        })

    return processed_data


def downloadYoutubeAudio(url, outputFile):
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "no_color": True,
        "no_call_home": True,
        "no_check_certificate": True,
        "format": "bestaudio/best",
        "outtmpl": outputFile
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            dictMeta = ydl.extract_info(
                url,
                download=True)
            if (not os.path.exists(outputFile)):
                raise Exception("Audio Download Failed")
            return outputFile, dictMeta['duration']
    except Exception as e:
        print("Failed downloading audio from the following video/url", e.args[0])
    return None


# def speedUpAudio(tempAudioPath, outputFile, expected_duration=None):  # Speeding up the audio to make it under 60secs, otherwise the output video is not considered as a short.
#     tempAudioPath, duration = get_asset_duration(tempAudioPath, False)
#     if not expected_duration:
#         if (duration > 57):
#             subprocess.run(['ffmpeg', '-i', tempAudioPath, '-af', f'atempo={(duration/57):.5f}', outputFile])
#         else:
#             subprocess.run(['ffmpeg', '-i', tempAudioPath, outputFile])
#     else:
#         subprocess.run(['ffmpeg', '-i', tempAudioPath, '-af', f'atempo={(duration/expected_duration):.5f}', outputFile])
#     if (os.path.exists(outputFile)):
#         return outputFile


def ChunkForAudio(alltext, chunk_size=2500):
    alltext_list = alltext.split('.')
    chunks = []
    curr_chunk = ''
    for text in alltext_list:
        if len(curr_chunk) + len(text) <= chunk_size:
            curr_chunk += text + '.'
        else:
            chunks.append(curr_chunk)
            curr_chunk = text + '.'
    if curr_chunk:
        chunks.append(curr_chunk)
    return chunks


def audioToTextWhipser(filename, model_size="base"):
    from whisper_timestamped import load_model, transcribe_timestamped
    global WHISPER_MODEL
    if (WHISPER_MODEL == None):
        WHISPER_MODEL = load_model(model_size)
    gen = transcribe_timestamped(WHISPER_MODEL, filename, verbose=False, fp16=False, language='zh')
    return gen



def run_background_audio_split(sound_file_path):
    try:
        # Run spleeter command
        # Get absolute path of sound file 
        output_dir = os.path.dirname(sound_file_path)
        command = f"spleeter separate -p spleeter:2stems -o '{output_dir}' '{sound_file_path}'"

        process = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # If spleeter runs successfully, return the path to the background music file
        if process.returncode == 0:
            return os.path.join(output_dir, sound_file_path.split("/")[-1].split(".")[0], "accompaniment.wav")
        else:
            return None
    except Exception:
        # If spleeter crashes, return None
        return None

