# coding=utf-8
import time
import hashlib
import os
import json
import requests

class MoyinAPI:

    def __init__(self,appkey,secret,voiceName):
        self.timestamp = str(int(time.time()))
        self.appkey = appkey
        self.secret = secret
        self.voiceName = voiceName

        self.message = '+'.join([self.appkey, self.secret, self.timestamp])

        self.m = hashlib.md5()
        self.m.update(self.message.encode("utf8"))
        self.signature = self.m.hexdigest()

        self.http_url = 'https://open.mobvoi.com/api/tts/v1'

    def generate_voice(self,text,filename,voiceName):
        data = {
            'text': text,
            'speaker': voiceName,
            'audio_type': 'mp3',
            'speed': 1.0,
        #'symbol_sil': 'semi_250,exclamation_300,question_250,comma_200,stop_300,pause_150,colon_200', # 停顿调节需要对appkey授权后才可以使用，授权前传参无效。
        #'ignore_limit': True, # 忽略1000字符长度限制，需要对appkey授权后才可以使用
            'gen_srt': False, # 是否生成srt字幕文件，默认不开启。如果开启生成字幕，需要额外计费。生成好的srt文件地址将通过response header中的srt_address字段返回。
            'appkey': self.appkey,
            'timestamp': self.timestamp,
            'signature': self.signature
        }
        try:
            headers = {'Content-Type': 'application/json'}
            print(f"try to request from moyinAPI, data text received:{text}") #debug
            response = requests.post(url=self.http_url, headers=headers, data=json.dumps(data))
            content = response.content

            # filename =os.path.join(os.path.dirname(os.path.abspath("__file__")), "moyinAPI.mp3")
            with open(filename, "wb") as f:
                f.write(content)
                print(f"in f.write(content)_content:{content}")
                print(f"MoyinAPI return filename:{filename}")#debug
                return filename
        except Exception as e:
            print("error: {0}".format(e))

    def moyinAPIWithSrt(self,text,filename,voiceName):
        data = {
            'text':text,
            'speaker': voiceName,
            'audio_type': 'wav',
            'speed': 1.0,
            #'symbol_sil': 'semi_250,exclamation_300,question_250,comma_200,stop_300,pause_150,colon_200', # 停顿调节需要对appkey授权后才可以使用，授权前传参无效。
            #'ignore_limit': True, # 忽略1000字符长度限制，需要对appkey授权后才可以使用
            'gen_srt': True, # 是否生成srt字幕文件，默认不开启。如果开启生成字幕，需要额外计费。生成好的srt文件地址将通过response header中的srt_address字段返回。
            'appkey': self.appkey,
            'timestamp': self.timestamp,
            'signature': self.signature
        }
        try:
            headers = {'Content-Type': 'application/json'}
            print(json.dumps(data))
            response = requests.post(url=self.http_url, headers=headers, data=json.dumps(data))
            content = response.content

            with open(os.path.join(os.path.dirname(os.path.abspath("__file__")), "moyinAPI.mp3"), "wb") as f:
                f.write(content)

            srtUrl = response.headers.get('srt_address', None)
            if srtUrl is None:
                print('not found srt url from response header')
                return

            print('srt url:', srtUrl)
            content = requests.get(url=srtUrl).content
            with open(os.path.join(os.path.dirname(os.path.abspath("__file__")), "moyinAPI.srt"), "wb") as f:
                f.write(content)

        except Exception as e:
            print("error: {0}".format(e))


