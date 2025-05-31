import io
import requests
import json
import os

from .config import Config

class Msger:
    def __init__(self):
        self.wx_robots = Config().get('wx_robots', [])
        self.enable_wx = Config().get('enable_wx',False)

    def send_msg(self, msg: str):
        data = {'msgtype': 'markdown', 'markdown': {'content': msg}}
        headers = {'Content-Type': 'application/json'}
        if not self.enable_wx:
            return
        for robot in self.wx_robots:
            post_res = requests.post(url=robot, data=json.dumps(data), headers=headers)
            if post_res.status_code == 200:
                #logger.info('已发送企业微信消息。 机器人webhook: '+robot)
                pass
            else:
                #logger.error('企业微信消息发送失败')
                pass
    
    def send_file(self, file_data: bytes, file_name: str):
        if not self.enable_wx:
            return
        files = {'media': (file_name, file_data)}
        headers = {'Content-Type': 'multipart/form-data'}
        url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?key={key}&type=file'.format(key=self.wx_robots[0].split('key=')[-1])
        response = requests.post(url, files=files)
        media_id = response.json().get('media_id')
        message = {
            'msgtype': 'file',
            'file': {
                'media_id': media_id
            }
        }
        headers = {'Content-Type': 'application/json'}
        for robot in self.wx_robots:
            response = requests.post(robot, json=message, headers=headers)
    
    def send_file_from_string(self, filename:str, file_str: str):
        file_bytes = file_str.encode('utf-8')
        self.send_file(file_bytes, filename)
    
    def send_file_from_bytes(self, filename:str, file_bytes: bytes):
        self.send_file(file_bytes, filename)
    
    def send_file_from_path(self, file_path: str):
        with open(file_path, 'rb') as f:
            file_data = f.read()
            file_name = os.path.basename(file_path)
            self.send_file(file_data, file_name)