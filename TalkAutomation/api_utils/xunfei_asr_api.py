# -*- coding: utf-8 -*-
import base64
import hashlib
import hmac
import json
import os
import time
import requests
import urllib

lfasr_host = 'https://raasr.xfyun.cn/v2/api'
# 请求的接口名
api_upload = '/upload'
api_get_result = '/getResult'

class XunfeiASRAPI:
    def __init__(self, appid, secret_key, upload_file_path):
        self.appid = appid
        self.secret_key = secret_key
        self.upload_file_path = upload_file_path
        self.ts = str(int(time.time()))
        self.signa = self.get_signa()

    def get_signa(self):
        m2 = hashlib.md5()
        m2.update((self.appid + self.ts).encode('utf-8'))
        md5 = m2.hexdigest()
        signa = hmac.new(self.secret_key.encode('utf-8'), bytes(md5, encoding='utf-8'), hashlib.sha1).digest()
        return base64.b64encode(signa).decode('utf-8')

    def upload(self):
        print("上传部分：")
        upload_file_path = self.upload_file_path
        file_len = os.path.getsize(upload_file_path)
        file_name = os.path.basename(upload_file_path)

        param_dict = {}
        param_dict['appId'] = self.appid
        param_dict['signa'] = self.signa
        param_dict['ts'] = self.ts
        param_dict["fileSize"] = file_len
        param_dict["fileName"] = file_name
        param_dict["duration"] = "200"
        print("upload参数：", param_dict)
        data = open(upload_file_path, 'rb').read(file_len)

        response = requests.post(url=lfasr_host + api_upload + "?" + urllib.parse.urlencode(param_dict),
                                 headers={"Content-type": "application/json"}, data=data)
        print("upload_url:", response.request.url)
        result = json.loads(response.text)
        print("upload resp:", result)
        return result

    def get_result(self):
        uploadresp = self.upload()
        orderId = uploadresp['content']['orderId']
        param_dict = {}
        param_dict['appId'] = self.appid
        param_dict['signa'] = self.signa
        param_dict['ts'] = self.ts
        param_dict['orderId'] = orderId
        param_dict['resultType'] = "transfer,predict"
        print("")
        print("查询部分：")
        print("get result参数：", param_dict)
        status = 3
        # 建议使用回调的方式查询结果，查询接口有请求频率限制
        while status == 3:
            response = requests.post(url=lfasr_host + api_get_result + "?" + urllib.parse.urlencode(param_dict),
                                     headers={"Content-type": "application/json"})
            # print("get_result_url:",response.request.url)
            result = json.loads(response.text)
            print(result)
            status = result['content']['orderInfo']['status']
            print("status=", status)
            if status == 4:
                break
            time.sleep(5)
        print("get_result resp:", result)
        return result

    def convert_to_speech_blocks(self, iflytek_result):
        result_json = json.loads(iflytek_result['content']['orderResult'])
        speech_blocks = []
        for lattice in result_json['lattice']:
            lattice_data = json.loads(lattice['json_1best'])
            for sentence in lattice_data['st']['rt']:
                for ws in sentence['ws']:
                    start_time = ws['wb'] / 100
                    end_time = ws['we'] / 100
                    text = ''.join([cw['w'] for cw in ws['cw']])
                    speech_blocks.append([[start_time, end_time], text])
        return speech_blocks

# 使用示例
if __name__ == '__main__':
    api = XunfeiASRAPI(appid="56689a9b",
                       secret_key="5b71c2c71cf9a5001c569dcca79c3655",
                       upload_file_path=r"audio/lfasr_涉政.wav")
    # 假设api_response是从get_result返回的结果
    api_response = api.get_result()
    speech_blocks = api.convert_to_speech_blocks(api_response)
    print(speech_blocks)
