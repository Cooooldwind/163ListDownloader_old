# Netease_playlist_allSong.py

import time
import requests
import os
from params_encSecKey import *


class playlist_get_allSong(object):
    
    def get_allID(self, playlist_id):
        time.sleep(1)
        playlist_api = 'https://music.163.com/weapi/v6/playlist/detail?'
        data = {
            'csrf_token': "",
            'id': str(playlist_id),
            'n': "0"
        }
        wyy_params = Netease_params(data)
        try:
            response = wyy_params.run(playlist_api)['playlist']
        except KeyError:
            print("歌单爬取错误! 请检查歌单是否为私密歌单")
            return "ErrorGettingPlayList!"
        else: print("获取成功! ")
        # print(response)
        playlist_info = dict()
        playlist_info['id'] = response['id']
        playlist_info['name'] = response['name']
        playlist_info['description'] = response['description']
        id_list = [i['id'] for i in response['trackIds']]
        playlist_info['c'] = [{'id': i} for i in id_list]

        ''' 效果等同于上句
            playlist_info['c'] = []
            for i in id_list:
                info = {'id':i}
                playlist_info['c'].append(info)
        '''
        # print(playlist_info)
        return playlist_info

    def get_song_info(self, c):
        time.sleep(1)
        song_api = 'https://music.163.com/weapi/v3/song/detail'
        data = {
            'c': str(c),
            'csrf_token': ''
        }
        try:
            wyy_params = Netease_params(data)
            song_info = wyy_params.run(song_api)['songs']
        except TimeoutError:
            print("歌曲爬取超时! 正在重新爬取...")
            pass
        # print(song_info)
        else:
            print("获取成功! ")
        return song_info


    
    def save_text(self, playlist_info, song_info):
        name = playlist_info['name']

        intab = "?*/\|.:><"
        outtab = "         "
        trantab = str.maketrans(intab, outtab)
        name = name.translate(trantab)

        text_path = f"./{name}.txt"

        short_info = {}

        for count in range(len(song_info)):
            info = song_info[count]
            artist_list = [i['name'] for i in info['ar']]
            song_url = f"https://music.163.com/song/media/outer/url?id={info['id']}.mp3"
            try: os.mkdir('NC_Download')
            except FileExistsError:pass
            finally: path = "NC_Download"
            #下载
            try:
                filename = f"{','.join(artist_list)} - {info['name']}.mp3"
                dirty = ["/","\\",":","*","\"","?","|","<",">"]
                for stuff in dirty:
                    filename = filename.replace(stuff,"")
                filename = f"{path}/{filename}"
                file_get = requests.get(song_url,allow_redirects = True)
                open(filename,'wb').write(file_get.content)
            except FileNotFoundError:
                os.mkdir('NC_Download')
            else: print(f"已保存第{count+1}首: {','.join(artist_list)} - {info['name']}")
  
        # 格式化json输出
        # with open(text_path, 'a+', encoding='utf8') as fp:
        #     fp.write(str(short_info))

    def run(self, playlist_id):
        print("正在获取歌单信息...")
        playlist_info = self.get_allID(playlist_id)
        if playlist_info != "ErrorGettingPlayList!":
            print("正在获取歌曲信息...")
            song_info = self.get_song_info(playlist_info['c'])
            print("开始下载！")
            self.save_text(playlist_info, song_info)
            judge = input("已经保存至本程序根目录下的“NC_Download”文件夹。是否打开(Y/N)?")
            if judge == "Y": os.startfile('NC_Download')
            else: exit()
        else: exit()

if __name__ == "__main__":
    print("--NeteaseCrabber By ColdWind--")
    print("")
    print("本程序使用CC4.0-BY-NC-SA协议，即您可以自由复制、散布、展示及演出本作品，但必须保留代码最后2行的版权信息并公示、不得用于任何商用场所、"
          "分享时必须同样使用CC4.0-BY-NC-SA协议")
    print("")
    playlist_id = input("输入歌单ID >>> ")
    allSong = playlist_get_allSong()
    allSong.run(playlist_id)

#CodeSource from 半岛的孤城
#Changed by ColdWind from https://www.bilibili.com/read/cv20818455
