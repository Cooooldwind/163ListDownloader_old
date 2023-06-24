'''
163ListDownloader By ColdWind
Version 1.3.0(Sirius)-23002a
SourceCode Follow GPL-3.0 License
增加:
1. 音乐的流式下载
2. 接口增加开放
   增加部分接口的方便调用，如: 
   Playlist = Playlist_Get("ID","163LD_Download",[True,True,True,True],64)
   Playlist.DownloadPrepare()
   print(f"Tot = {int(Playlist.ListTot())}")
   以上代码可以输出歌曲总数
3. 运行时执行
   在代码105-117行被注释的代码就是运行时执行的代码，您可以取消这几行的注释，同时取消118-130行的注释看看效果。
修复:
1. 专辑存储时的错误:
   我是煞笔，mime写成mine了（笑
备注: 添加了tqdm，请在cmd中输入"pip install tqdm"安装。
'''

import time,requests,os,eyed3,threading
#import pprint 字典输出美化，使用pprint.pprint(内容)。 
from tkinter import *
from tqdm import tqdm
from params_encSecKey import *
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error

class Playlist_Get(threading.Thread):
    def __init__(self, ID, Path, Args, MaxThread):
        self.ID = ID
        self.Path = Path
        self.Args = Args
        self.MaxThread = MaxThread
        if self.MaxThread > 32: self.MaxThread = 32
    def List_Get(self):
        PlaylistAPI = "https://music.163.com/weapi/v6/playlist/detail?"
        try: 
            List = Netease_params(
                {
                    'csrf_token': "",
                    'id': str(self.ID), 
                    'n': "0"
                 }
            ).run(PlaylistAPI)['playlist']
        except KeyError: pass
        else: pass
        ReturnList = [str(""),dict()]
        ReturnList[0] = str(List['userId'])
        ReturnList[1] = dict()
        ReturnList[1]['name'] = List['name']
        ReturnList[1]['songs'] = [{'id':i['id']} for i in List['trackIds']]
        return ReturnList
    def Song_Get(self, ListInfo, UserID): 
        SongAPI = "https://music.163.com/weapi/v3/song/detail"
        try:
            SongInfo = Netease_params(
                {
                    'c': str(ListInfo['songs']),
                    'csrf_token': '',
                    'userId': UserID
                }
            ).run(SongAPI)['songs']
        except TimeoutError: pass
        else: pass
        ReturnSongInfo = []
        for i in range(len(SongInfo)):
            Artist = SongInfo[i]['ar'][0]['name']
            Name = SongInfo[i]['name']
            Album = SongInfo[i]['al']['name']
            Dirty = ["/","\\",":","*","\"","?","|","<",">"]
            for Stuff in Dirty: Name = Name.replace(Stuff,"")
            for Stuff in Dirty: Album = Album.replace(Stuff,"")
            for Stuff in Dirty: Artist = Artist.replace(Stuff,"")
            Appending = {
                'name':Name,
                'id':str(SongInfo[i]['id']),
                'artists':Artist,
                'album':Album,
                'album_picture_url':SongInfo[i]['al']['picUrl']
            }
            ReturnSongInfo.append(Appending)
        return ReturnSongInfo
    def DownloadPrepare(self):
        List = Playlist_Get.List_Get(self)
        UserID = List[0]
        SongInfo = Playlist_Get.Song_Get(self, List[1], UserID)
        Dirty = ["/","\\",":","*","\"","?","|","<",">"]
        for Stuff in Dirty: List[1]['name'] = List[1]['name'].replace(Stuff,"")
        self.Path = self.Path + '\\' + List[1]['name'] + '\\'
        print(self.Path)
        Playlist_Get.FolderCreate(self)
        self.SongInfo = SongInfo
    def FolderCreate(self):
        try: os.makedirs(self.Path)
        except FileExistsError: pass
        return
    def DownloadSums(self):
        if self.isDownload: return self.DownloadSum
        else: return -1
    def ListTot(self):
        if self.SongInfo == []: return -1
        else: return len(self.SongInfo)
    def Finished(self): return self.isFinished
    def Download_Main(self):
        self.DownloadSum = 0
        self.isDownload = True
        self.isFinished = False
        #SuccessfulSum = 0
        #HeadThread = Downloading(self.DownloadSum,len(self.SongInfo))
        #HeadThread.start()
        while self.DownloadSum < len(self.SongInfo):
            while threading.activeCount() <= self.MaxThread and self.DownloadSum < len(self.SongInfo):
                NewThread = Playlist_Download(self.Args, self.Path, self.SongInfo[self.DownloadSum])
                NewThread.start()
                time.sleep(0.01)
                self.DownloadSum += 1
            while threading.activeCount() >= self.MaxThread: time.sleep(0.01)
        self.isDownload = False
        self.isFinished = True
        #HeadThread.kill()
'''
class Downloading(threading.Thread):
    def __init__(self, sum, tot):
        threading.Thread.__init__(self)
        self.sum = sum
        self.tot = tot
        self.killed = False
    def run(self):
        while self.killed == False:
            print(f"{int(self.sum)}/{int(self.tot)}")
            time.sleep(0.5)
    def kill(self): self.killed = True
'''        
class Playlist_Download(threading.Thread):
    def __init__(self, Args, Path, Info):
        threading.Thread.__init__(self)
        self.Args = Args #一个列表，包括[歌曲下载，歌词下载，属性编辑，封面编辑]
        self.Path = Path
        self.Info = Info
    def run(self):
        print(self.Info['name'] + " - " + self.Info['artists'])
        if self.Args[0] == True:
            DownloadURL = "https://music.163.com/song/media/outer/url?id=" + self.Info['id'] + ".mp3"
            Filename = self.Info['name'] + " - " + self.Info['artists'] + ".mp3"
            File = open(self.Path + Filename,'wb+')
            try: Get = requests.get(DownloadURL,allow_redirects = True,stream=True)
            except ConnectionError: Playlist_Download([True,False,False,False], self.Path, self.Info)
            else: pass
            #FileSize = int(Get.headers.get("content-length",0))
            ChunkSize = 1024
            Now_Size = 0
            for Data in Get.iter_content(chunk_size = ChunkSize):
                File.write(Data)
                Now_Size += len(Data)
                # print(f"{Now_Size / FileSize * 100}%")
            time.sleep(0.05)
            File.close()
            Test = eyed3.load(self.Path + Filename)
            try: Test.tag.artist = self.Info['artists']
            except AttributeError:
                time.sleep(0.1)
                os.remove(self.Path + Filename)
                return
        if self.Args[1] == True:
            LyricAPI = 'https://music.163.com/weapi/song/lyric?csrf_token='
            try: Lyric = Netease_params(
                    {
                        'csrf_token':"", 
                        'id':self.Info['id'], 
                        'lv':'-1', 
                        'tv':'-1'
                    }   
                ).run(LyricAPI)
            except ConnectionError: Playlist_Download([False,True,False,False], self.Path, self.Info)
            ReturnLyric = Lyric['lrc']['lyric'].replace("\n",'\n')
            Filename = self.Info['name'] + " - " + self.Info['artists'] + ".lrc"
            File = open(self.Path + Filename,'w+',encoding = 'UTF-8')
            File.write(ReturnLyric)
            File.close()
        if self.Args[3] == True:
            Filename = self.Info['name'] + " - " + self.Info['artists'] + ".jpg"
            File = open(self.Path + Filename,'wb+')
            Get = requests.get(self.Info['album_picture_url'],allow_redirects = True)
            File.write(Get.content)
            File.close()
            if self.Args[0] == True:
                Musicname = self.Info['name'] + " - " + self.Info['artists'] + ".mp3"
                File = open(self.Path + Filename,'rb+')
                audio = ID3(self.Path + Musicname)
                audio.add(APIC(encoding = 3,mime = 'image/jpeg',type = 3,desc = u'Cover',data = File.read()))
                audio.save(v2_version=3)
                File.close()
                os.remove(self.Path + Filename)
        if self.Args[0] == True and self.Args[2] == True:
            Filename = self.Info['name'] + " - " + self.Info['artists'] + ".mp3"
            File = eyed3.load(self.Path + Filename)
            File.tag.artist = self.Info['artists']
            File.tag.album = self.Info['album']
            File.tag.save()

'''
Playlist = Playlist_Get("ID","163LD_Download",[True,True,True,True],64)
Playlist.DownloadPrepare()
pprint.pprint(Playlist.SongInfo)
print(f"Tot = {int(Playlist.ListTot())}")
Playlist.Download_Main()
'''