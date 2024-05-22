import sys
import os
import requests
print("Hello,World")
headers = {


	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',

}
payload = {'xiaomapeiyin_svip_user_id': '3339', 'xiaomapeiyin_svip_token': 'xiaomapeiyinapi123d823339be5148e80aca9ea8ad942b13a3faccfbe1c91df0e9b'
    , 'xiaomapeiyin_text': '小马配音'
    , 'caiyanglv': '16'
    , 'geshi': '3'
    , 'renming_id': '19'
    , 'pitchRate': '0'
	, 'speechRate': '0'
	, 'volume': '50'
	, 'bgurl': ''
	, 'is_shiting': '1'
	, 'bgurl': ''
	, 'bgurl': ''  }
r = requests.post("http://peiyin.xiaomawenku.com/PeiYin/xiaomapeiyin_api_to_peiyin", data=payload, headers=headers)
print(r.url)
mp3_url = r.json()['data']['xiaomapeiyin_result_url']


print(""+r.text)


# 读取MP3资源]
res = requests.get(mp3_url,stream=True,headers=headers)
 # 获取文件地址
print(""+mp3_url)
file_path='xiaomapeiyin.mp3'
# 打开本地文件夹路径file_path，以二进制流方式写入，保存到本地
with open(file_path, 'wb') as fd:
	for chunk in res.iter_content():
		fd.write(chunk)