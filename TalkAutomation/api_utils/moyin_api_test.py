# coding=utf-8
import time
import hashlib
import os
import json
import requests

class MoyinAPI:

    def __init__(self,appkey,secret):
        self.timestamp = str(int(time.time()))
        self.appkey = '552C7566356DF7A256C23D93466331F8'
        self.secret = '300591A6C20003089AE54C09D643310F'

        self.message = '+'.join([self.appkey, self.secret, self.timestamp])

        self.m = hashlib.md5()
        self.m.update(self.message.encode("utf8"))
        self.signature = self.m.hexdigest()

        self.http_url = 'https://open.mobvoi.com/api/tts/v1'

    def generate_voice(self,text):
        data = {
            'text': text,
            'speaker': 'xiaoyi_meet',
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
            response = requests.post(url=self.http_url, headers=headers, data=json.dumps(data))
            content = response.content
            print(f"in f.write(content)_content:{content}")

            filename =os.path.join(os.path.dirname(os.path.abspath("__file__")), "moyinAPI.mp3")
            with open(filename, "wb") as f:
                f.write(content)
                print(f"MoyinAPI已返回filename:{filename}")
                return filename
        except Exception as e:
            print("error: {0}".format(e))

    def moyinAPIWithSrt(self):
        data = {
            'text': '出门问问成立于2012年，是一家以语音交互和软硬结合为核心的人工智能公司，为全球40多个国家和地区的消费者、企业提供人工智能产品和服务。',
            'speaker': 'xiaoyi_meet',
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

    def moyinAPIWithSsml(self):
        data = {
            'text': '<speak version="1.0" xml:lang="zh-CN" xmlns="http://www.w3.org/2001/10/synthesis">9月10日，庆祝2019年<w phoneme="jiao4 shi1 jie2">教师节</w>暨全国教育系统先进集体和先进个人表彰大会在京举行。<break time="500ms" />习近平总书记在人民大会堂亲切会见受表彰代表，<break time="500ms" />向受到表彰的先进集体和先进个人表示热烈祝贺，<break time="500ms" />向全国广大<p phoneme="jiao4">教</p>师和教育工作者致以节日的问候。</speak>',
            'speaker': 'xiaoyi_meet',
            'audio_type': 'wav',
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
            print(json.dumps(data))
            response = requests.post(url=self.http_url, headers=headers, data=json.dumps(data))
            content = response.content

            with open(os.path.join(os.path.dirname(os.path.abspath("__file__")), "ssmlmoyinAPI.mp3"), "wb") as f:
                f.write(content)

        except Exception as e:
            print("error: {0}".format(e))

def main():
    appkey = '552C7566356DF7A256C23D93466331F8'
    secret = '300591A6C20003089AE54C09D643310F8'

    moyin_instance = MoyinAPI(appkey, secret)

    text_to_generate = '有些人，注定只是路过，而有些人，注定会留下痕迹。'
    moyin_instance.generate_voice(text_to_generate)
    # moyinAPI()
    # # moyinAPIWithSrt()
    # # moyinAPIWithSsml()

if __name__ == '__main__':
    main()