'''
163ListDownloader by CooooldWind_
Version 1.3.0-23010a
Sourcecode follows GPL-3.0 licence.
Updates:
重写内容
更改主文件名称为__init__（手动加入到site-packages文件夹可以实现调用）
下载的时候会在文件夹底下生成随机名称的文件夹防止串歌
暂时阉割掉了多线程下载，后面再研究看看
差不多这样子
'''


import random,time,os,eyed3,requests
from mutagen.id3 import ID3,APIC
from PIL import Image
from .params_encSecKey import *

__name__ = "163ListDownloader_Sirius"
__version__ = "1.3.0-23010a"

class Playlist():
    def __init__(self, ID):
        self.ID = ID
        
    
    #获取数据
    def data_get(self, Path, Args):
        if Path[-1] != '/': Path += '/'
        #获取歌单简短信息
        PlaylistAPI = "https://music.163.com/weapi/v6/playlist/detail?"
        try: List = Netease_params(
                {'csrf_token': "", 'id': str(self.ID), 'n': "0"}
            ).run(PlaylistAPI)['playlist']
        except KeyError: pass
        else: pass
        #数据整理成列表，第一项是用户id，用于仿创建者获取，爬私密歌单；第二项是歌曲id。
        self.shortList = [str(""),dict()]
        try: self.shortList[0] = str(List['userId'])
        except: return "Failure:Offical Playlist!"
        self.shortList[1] = dict()
        self.shortList[1]['name'] = List['name']
        self.shortList[1]['songs'] = [{'id':i['id']} for i in List['trackIds']]
        #用户是否有分类文件夹需求。
        if Args[0] == True: Path = Path + self.shortList[1]['name'] + '/'
        #获取详细信息。
        SongAPI = "https://music.163.com/weapi/v3/song/detail"
        try: SongInfo = Netease_params(
                {'c': str(self.shortList[1]['songs']), 'csrf_token': '', 'userId': self.shortList[0]}
            ).run(SongAPI)['songs']
        except TimeoutError: pass
        else: pass
        #随机种子为时间戳，用于填入文件夹防下载时串歌
        random.seed(time.time())
        #数据逐个整理。
        self.longList = []
        for i in range(len(SongInfo)):
            Artists = ""
            for j in SongInfo[i]['ar']: Artists += j['name'] + ","
            Name = SongInfo[i]['name']
            Album = SongInfo[i]['al']['name']
            Dirty = ["/","\\",":","*","\"","?","|","<",">"]
            for Stuff in Dirty: Name = Name.replace(Stuff,"")
            for Stuff in Dirty: Album = Album.replace(Stuff,"")
            for Stuff in Dirty: Artists = Artists.replace(Stuff,"")
            Path_A = Path
            #创建随机的文件夹
            Path_B = "{" + "".join(random.sample('1234567890QWERTYUIOPASDFGHJKLZXCVBNM',5)) + "-" + "".join(random.sample('1234567890QWERTYUIOPASDFGHJKLZXCVBNM',5)) + "-" + "".join(random.sample('1234567890QWERTYUIOPASDFGHJKLZXCVBNM',5)) + "-" + "".join(random.sample('1234567890QWERTYUIOPASDFGHJKLZXCVBNM',5)) + "}/"
            Appending = {
                'name':Name,#歌曲名
                'id':str(SongInfo[i]['id']),#id
                'artists':Artists[0:len(Artists)-1],#作者（-1是把最后一个逗号删掉）
                'album':Album,#专辑
                'album_picture_url':SongInfo[i]['al']['picUrl'],#图片链接
                'path':Path_A,#存放地址
                'path_add':Path_B,#暂时存放的文件夹防止串歌
                'args':Args#需求[分类文件夹,歌曲下载,歌词下载,封面下载,信息录入]
            }
            self.longList.append(Appending)
        return self.longList
        #此处返回包含字典的列表。
        
        
    #下载的主函数
    def download_main(self):
        for self.downloading in self.longList:
            #下载时的文件名
            self.downloading['filename'] = self.downloading['name'] + " - " + self.downloading['artists']
            #逐个判断是否要操作
            ss = "Successful!"
            print(self.downloading['path'] + self.downloading['path_add'])
            os.makedirs(self.downloading['path'] + self.downloading['path_add'])
            if self.downloading['args'][1] == True: ss = self.music_get()
            if self.downloading['args'][2] == True and ss == "Successful!": self.lyric_get()
            if self.downloading['args'][3] == True and ss == "Successful!": self.cover_get()
            if self.downloading['args'][4] == True and ss == "Successful!": self.info_write()
            print(self.mixer())
        return None
    
    
    #下载音乐
    def music_get(self):
        DownloadURL = "https://music.163.com/song/media/outer/url?id=" + self.downloading['id'] + ".mp3"
        filename = self.downloading['filename'] + ".mp3"
        random.seed(time.time())
        file = open(self.downloading['path'] + self.downloading['path_add'] + filename,'wb+')
        #妈的，不给我标头是吧，爷一直找你要，烦死你！操
        while True:
            try: fileget = requests.get(DownloadURL,allow_redirects = True,stream=True)
            except: pass
            else: break
        downloaded = int(0)
        '''try: totalsize = int(fileget.headers['Content-Length'])
        except: pass'''
        for data in fileget.iter_content(chunk_size = 1024):
            file.write(data)
            downloaded += len(data)
            if random.randint(0,1000) % 200 == 0:
                time.sleep(0.01)
            if downloaded == len(data):
                try: str_test = data.decode("utf-8")
                except UnicodeDecodeError: pass
                else:
                    file.close()
                    time.sleep(0.05)
                    os.remove(self.downloading['path'] + self.downloading['path_add'] + filename)
                    time.sleep(0.01)
                    os.removedirs(self.downloading['path'] + self.downloading['path_add'])
                    return "Error:VIP Song!"
        file.close() 
        return "Successful!"
    
    
    #下载歌词
    def lyric_get(self):
        LyricAPI = 'https://music.163.com/weapi/song/lyric?csrf_token='
        while True:
            try: Lyric = Netease_params({'csrf_token':"", 'id':self.downloading['id'], 'lv':'-1', 'tv':'-1'}).run(LyricAPI)
            except: pass
            else: break
        filename = self.downloading['filename'] + ".lrc"
        file = open(self.downloading['path'] + self.downloading['path_add'] + filename,'w+',encoding='utf-8')
        file.write(Lyric['lrc']['lyric'].replace("\n",'\n'))
        file.close()
        return "Successful!"
    
    
    #下载封面
    def cover_get(self):
        filename = self.downloading['filename'] + ".jpg"
        file = open(self.downloading['path'] + self.downloading['path_add'] + filename,'wb+')
        while True:
            try: file.write(requests.get(self.downloading['album_picture_url'],allow_redirects = True).content)
            except: pass
            else: break
        file.close()
        file = Image.open(self.downloading['path'] + self.downloading['path_add'] + filename)
        file = file.convert("RGB")
        fileType = file.format
        file_Out = file.resize((800, 800),Image.NEAREST)
        file_Out.save(self.downloading['path'] + self.downloading['path_add'] + filename,fileType)
        return "Successful"
    
    
    #属性填写
    def info_write(self):
        filename = self.downloading['filename'] + ".mp3"
        picname = self.downloading['filename'] + ".jpg"
        file = eyed3.load(self.downloading['path'] + self.downloading['path_add'] + filename)
        file.tag.artist = self.downloading['artists']
        file.tag.album = self.downloading['album']
        file.tag.save()
        if self.downloading['args'][3] == True:
            file = open(self.downloading['path'] + self.downloading['path_add'] + picname,'rb+')
            audio = ID3(self.downloading['path'] + self.downloading['path_add'] + filename)
            audio.add(APIC(encoding = 3,mime = 'image/jpeg',type = 3,desc = u'Cover',data = file.read()))
            audio.save(v2_version=3)
            file.close()
            os.remove(self.downloading['path'] + self.downloading['path_add'] + picname)
        return "Successful!"
    
    
    #然后处理一下
    def mixer(self):
        command_1 = "copy \"" + self.downloading['path'] + self.downloading['path_add'] + "*\" \"" + self.downloading['path'] + "\""
        command_1 = command_1.replace('/','\\')
        command_2 = self.downloading['path'] + self.downloading['path_add'] + "\""
        command_2 = command_2.replace('/','\\')
        command_2 = "rd /S /Q \"" + command_2
        print(command_1)
        print(command_2)
        while True:
            try: 
                os.system(command_1)
                os.system(command_2)
            except: pass
            else:break
        return "Successful!"