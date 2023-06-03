# params_encSecKey.py
#视频参考：https://www.bilibili.com/video/BV1i54y1h75W?p=48
import random
import json
import requests
from base64 import b64encode
from Crypto.Cipher import AES


class Netease_params(object):
    def __init__(self, data):
        #字典要成字符串（json）再加密
        self.data = data

        #服务于d的
        self.e = '010001'
        self.f = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
        self.g = '0CoJUm6Qyw8W8jud'
        self.i = 'vlgPRPyGhwA6F4Sq' #手动固定的 =》网页是随机的

    def set_user_agent(self):
        USER_AGENTS = [
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
            "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
            "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
            "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
            "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5"
        ]
        user_agent = random.choice(USER_AGENTS)
        return user_agent

    def get_encSecKey(self):
        return "6ea19f618d09893013feb207e6953ab0d04831ccf86095147970745a825a0f3288ad0bfdb802ffd5876394599d179b65785e679b23ae38035d476872f5270c26f7e15f0e2de0da92ac7fdd1de6a965642a67707d3b204d48a3a3c66fe536c9e2056d2032c884d764cf419e8ce7bd245f56bde140deccbaed83995285ee66ccda"

    #转换成16的倍数
    def to_16(self, data):
        pad = 16 -len(data) % 16
        data += chr(pad) * pad
        return data

    def enc_params(self, data, key):
        #加密过程
        iv = "0102030405060708"
        data = self.to_16(data) #加密的内容必须是16的倍数
        aes = AES.new(key=key.encode("utf-8"), IV=iv.encode("utf-8"), mode=AES.MODE_CBC) #创建加密器
        bs = aes.encrypt(data.encode("utf-8")) #加密
        return str(b64encode(bs), "utf-8") #转成字符串，这个bs不能直接decode，要先转成b64

    #数据加密两次
    def get_params(self, data):
        first = self.enc_params(data, self.g)
        secend = self.enc_params(first, self.i)
        return secend


    def run(self, url):
        data = {
        'params': self.get_params(json.dumps(self.data)),
        'encSecKey':self.get_encSecKey()
    }
        headers = {'User-Agent':self.set_user_agent()}
        response = requests.post(url, data=data, headers=headers).json()
        #print(response)
        return response

if __name__ == '__main__':
    url = 'https://music.163.com/weapi/song/lyric?csrf_token='
    data = {
            'csrf_token': "",
            'id': "1398764652", #此处为网易云歌曲id
            'lv': '-1',
            'tv': '-1'
        }
    wyy = Netease_params(data)
    wyy.run(url)
    #Copied from 半岛的孤城 https://www.bilibili.com/read/cv12754897
