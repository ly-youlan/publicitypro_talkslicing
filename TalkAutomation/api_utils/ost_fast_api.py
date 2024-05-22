#!/usr/bin/python3
# -*- coding:utf-8 -*-
import time
import requests
import datetime
import hashlib
import base64
import hmac
import json
import os
import re
from TalkAutomation.api_utils.fileupload import seve_file
from TalkAutomation.audio.audio_utils import extract_and_convert_audio

path_pwd = os.path.split(os.path.realpath(__file__))[0]
os.chdir(path_pwd)


# 创建和查询
class get_result(object):
    def __init__(self, appid, apikey, apisecret):
        # 以下为POST请求
        self.Host = "ost-api.xfyun.cn"
        self.RequestUriCreate = "/v2/ost/pro_create"
        self.RequestUriQuery = "/v2/ost/query"
        # 设置url
        if re.match("^\d", self.Host):
            self.urlCreate = "http://" + self.Host + self.RequestUriCreate
            self.urlQuery = "http://" + self.Host + self.RequestUriQuery
        else:
            self.urlCreate = "https://" + self.Host + self.RequestUriCreate
            self.urlQuery = "https://" + self.Host + self.RequestUriQuery
        self.HttpMethod = "POST"
        self.APPID = appid
        self.Algorithm = "hmac-sha256"
        self.HttpProto = "HTTP/1.1"
        self.UserName = apikey
        self.Secret = apisecret

        # 设置当前时间
        cur_time_utc = datetime.datetime.utcnow()
        self.Date = self.httpdate(cur_time_utc)
        # 设置测试音频文件
        self.BusinessArgsCreate = {
            "language": "zh_cn",
            "accent": "mandarin",
            "domain": "pro_ost_ed",
            # "callback_url": "http://IP:端口号/xxx/"
        }

    def img_read(self, path):
        with open(path, 'rb') as fo:
            return fo.read()

    def hashlib_256(self, res):
        m = hashlib.sha256(bytes(res.encode(encoding='utf-8'))).digest()
        result = "SHA-256=" + base64.b64encode(m).decode(encoding='utf-8')
        return result

    def httpdate(self, dt):
        """
        Return a string representation of a date according to RFC 1123
        (HTTP/1.1).
        The supplied date must be in UTC.
        """
        weekday = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][dt.weekday()]
        month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep",
                 "Oct", "Nov", "Dec"][dt.month - 1]
        return "%s, %02d %s %04d %02d:%02d:%02d GMT" % (weekday, dt.day, month,
                                                        dt.year, dt.hour, dt.minute, dt.second)

    def generateSignature(self, digest, uri):
        signature_str = "host: " + self.Host + "\n"
        signature_str += "date: " + self.Date + "\n"
        signature_str += self.HttpMethod + " " + uri \
                         + " " + self.HttpProto + "\n"
        signature_str += "digest: " + digest
        signature = hmac.new(bytes(self.Secret.encode('utf-8')),
                             bytes(signature_str.encode('utf-8')),
                             digestmod=hashlib.sha256).digest()
        result = base64.b64encode(signature)
        return result.decode(encoding='utf-8')

    def init_header(self, data, uri):
        digest = self.hashlib_256(data)
        sign = self.generateSignature(digest, uri)
        auth_header = 'api_key="%s",algorithm="%s", ' \
                      'headers="host date request-line digest", ' \
                      'signature="%s"' \
                      % (self.UserName, self.Algorithm, sign)
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Method": "POST",
            "Host": self.Host,
            "Date": self.Date,
            "Digest": digest,
            "Authorization": auth_header
        }
        return headers

    def get_create_body(self, fileurl):
        post_data = {
            "common": {"app_id": self.APPID},
            "business": self.BusinessArgsCreate,
            "data": {
                "audio_src": "http",
                "audio_url": fileurl,
                "encoding": "raw"
            }
        }
        body = json.dumps(post_data)
        return body

    def get_query_body(self, task_id):
        post_data = {
            "common": {"app_id": self.APPID},
            "business": {
                "task_id": task_id,
            },
        }
        body = json.dumps(post_data)
        return body

    def call(self, url, body, headers):

        try:
            response = requests.post(url, data=body, headers=headers, timeout=8)
            status_code = response.status_code
            interval = response.elapsed.total_seconds()
            if status_code != 200:
                info = response.content
                return info
            else:
                resp_data = json.loads(response.text)
                return resp_data
        except Exception as e:
            print("Exception ：%s" % e)

    def task_create(self, fileurl):
        # 使用传递的fileurl创建任务
        body = self.get_create_body(fileurl)
        headers_create = self.init_header(body, self.RequestUriCreate)
        response = self.call(self.urlCreate, body, headers_create)
        if response and 'data' in response and 'task_id' in response['data']:
            return response['data']['task_id']
        else:
            raise Exception("任务创建失败，响应：{}".format(response))

    def task_query(self, task_id):
        # 查询任务状态，使用task_id参数
        body = self.get_query_body(task_id)
        headers_query = self.init_header(body, self.RequestUriQuery)
        response = self.call(self.urlQuery, body, headers_query)
        if response and 'data' in response:
            task_status = response['data']['task_status']
            if task_status not in ['1', '2']:  # 任务状态不是“进行中”或“排队中”
                return response
            else:
                return None  # 任务还在进行中，可以根据需要调整逻辑
        else:
            raise Exception("查询任务失败，响应：{}".format(response))

    def get_fileurl(self, file_path):
        # 修改此方法以使用方法参数file_path而非全局变量
        api = seve_file.SeveFile(app_id=self.APPID, api_key=self.UserName, api_secret=self.Secret, upload_file_path=file_path)
        file_total_size = os.path.getsize(file_path)
        if file_total_size < 31457280:  # 小于30MB，不使用分块上传
            print("-----不使用分块上传-----")
            fileurl = api.gene_params('/upload')['data']['url']
        else:
            print("-----使用分块上传-----")
            fileurl = api.gene_params('/mpupload/upload')
        return fileurl

    def get_result(self):
        # 创建订单
        print("\n------ 创建任务 -------")
        task_id = self.task_create()['data']['task_id']
        # 查询任务
        print("\n------ 查询任务 -------")
        print("任务转写中······")
        while True:
            result = self.task_query(task_id)
            if isinstance(result, dict) and result['data']['task_status'] != '1' and result['data']['task_status'] != '2':
                print("转写完成···\n", json.dumps(result, ensure_ascii=False))
                break
            elif isinstance(result, bytes):
                print("发生错误···\n", result)
                break


def audioToText(file_path):
    get_result_instance = get_result("56689a9b", "f7589e5853fc82b26c844559be7f503d", "MjMwMDc0MWRjOTY4YTZmZThjNjRhNzA4")

    # 上传文件并获取URL
    fileurl = get_result_instance.get_fileurl(file_path)
    # 创建任务
    task_id = get_result_instance.task_create(fileurl)
    if not task_id:
        raise Exception("创建任务失败")
    # 轮询查询任务结果
    result = None
    while not result:
        result = get_result_instance.task_query(task_id)
        # 适当等待时间后再次查询，避免频繁请求
        time.sleep(2)  # 根据实际情况调整等待时间
    return result


def convert_to_speech_block(data):
    segments = []
    for lattice in data['data']['result']['lattice']:
        segment_text = []
        segment_start = float('inf')
        segment_end = 0
        for sentence in lattice['json_1best']['st']['rt']:
            for word_info in sentence['ws']:
                for cw in word_info['cw']:
                    word = cw['w']
                    start = int(word_info['wb']) / 1000.0  # 将毫秒转换为秒
                    end = int(word_info['we']) / 1000.0
                    if word:  # 忽略空单词
                        segment_text.append(word)
                        segment_start = min(segment_start, start)
                        segment_end = max(segment_end, end)
        if segment_text:
            segments.append([[segment_start, segment_end], ' '.join(segment_text)])
    return segments


# Example Python code for preprocessing the provided data format

def preprocess_transcription(data):
    processed_data = []

    # Assuming 'data' is the dictionary containing the entire transcription data
    for item in data['data']['result']['lattice']:
        # Extract begin and end timestamps, speaker identifier
        begin_time = item['begin']
        end_time = item['end']
        speaker = item['spk']

        # Concatenate all words to form the full recognized text
        words = [word_info['cw'][0]['w'] for rt in item['json_1best']['st']['rt'] for word_info in rt['ws']]
        recognized_text = ''.join(words)

        # Append the structured information to the processed_data list
        processed_data.append({
            'begin': begin_time,
            'end': end_time,
            'speaker': speaker,
            'text': recognized_text
        })

    return processed_data



if __name__ == '__main__':
    # 输入讯飞开放平台的appid，secret、key和文件路径
    # 示例使用
    video_path = '/Users/youlan/Pictures/private/M4ROOT/CLIP/23年思政学风会议+采访/采访主机位-35mm-主声音/20231222_A0535.MP4'
    file_path = extract_and_convert_audio(video_path, target_format='wav', sample_rate=16000, channels=1)
    print(file_path)

    # file_path = r"/Users/youlan/Downloads/20231222_A0527.wav"

    # 使用xunfeiOstAPI类处理转写
    result = audioToText(file_path)
    print("转写结果：", result)

    # result2 = convert_to_speech_block(result)
    # print("speech blocks：", result2)

    # Example usage
    # This is a placeholder; the actual 'data' variable should contain the full transcription data
    data = result  # This should be replaced with the actual transcription data
    processed_data = preprocess_transcription(data)

    # Now 'processed_data' contains the structured information ready for analysis
    print(processed_data)


