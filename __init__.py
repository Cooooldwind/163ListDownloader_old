'''
163ListDownloader by CooooldWind_
Version 1.3.0-23017a
Sourcecode follows GPL-3.0 licence.
Updates: 
1. 修复漏洞
'''

import random,time,os,eyed3,requests,threading,pprint,shutil
from mutagen.id3 import ID3,APIC
from PIL import Image
from .params_encSecKey import *

playlist_api = "https://music.163.com/weapi/v6/playlist/detail?"
music_info_api = "https://music.163.com/weapi/v3/song/detail"
lyric_api = "https://music.163.com/weapi/song/lyric?csrf_token="

class playlist():
    def __init__(self, id):
        self.id = id
        self.longlist = "[Error] Didn't run data_get function."
        self.shortlist = "[Error] Didn't run data_get function."
        self.creater = "[Error] Didn't run data_get function."
        self.playlist_name = "[Error] Didn't run data_get function."
    def data_get(self):
        '全局一下API'
        global playlist_api
        global music_info_api
        '爬歌曲ID'
        try: get_list = Netease_params(
                {'csrf_token': "", 'id': str(self.id), 'n': "0"}
            ).run(playlist_api)['playlist']
        except KeyError: pass
        else: pass
        '存创建者ID待会儿仿ta本人获取详细信息，顺便测下爬没爬成'
        try: self.creater = str(get_list['userId'])
        except: 
            raise Exception("Playlist-Get Error: Server refused the request, this playlist may not be accessible.")
        self.playlist_name = get_list['name']
        '存下所有歌ID'
        self.shortlist = [{'id':i['id']} for i in get_list['trackIds']]
        '爬歌曲详细信息'
        try: get_music = Netease_params(
                {'c': str(self.shortlist), 'csrf_token': '', 'userId': self.creater}
            ).run(music_info_api)['songs']
        except TimeoutError: 
            raise Exception("Playlist-Get Error: Connect time is too long to wait.")
        else: pass
        'longlist就是包含各种信息的大表'
        self.longlist = []
        '开始填写信息'
        now = 0
        for i in range(len(get_music)):
            '伪随机种子，基于歌曲id'
            random.seed(get_music[i]['id'])
            '歌曲名'
            name = get_music[i]['name']
            '艺人'
            artists = ""
            for j in get_music[i]['ar']:
                artists += j['name'] + ","
            artists = artists[0: len(artists) - 1]
            '专辑'
            album = get_music[i]['al']['name']
            '歌名、艺人、专辑检测违规字符并去除'
            dirty = ["/","\\",":","*","\"","?","|","<",">"]
            for j in dirty:
                name = name.replace(j,"")
                artists = artists.replace(j,"")
                album = album.replace(j,"")
                self.playlist_name = self.playlist_name.replace(j,"")
            '歌曲、歌词、专辑封面文件名'
            music_filename = name + " - " + artists + ".mp3"
            lyric_filename = name + " - " + artists + ".lrc"
            cover_filename = name + " - " + artists + ".jpg"
            '封面和音乐的链接'
            cover_link = get_music[i]['al']['picUrl']
            music_link = "https://music.163.com/song/media/outer/url?id=" + str(get_music[i]['id']) + ".mp3"
            'uid获取，为25位包含26个大写字母和数字的字符串，每五个用横杠隔开'
            uid = ""
            for i in range(5):
                uid += "".join(random.sample('1234567890QWERTYUIOPASDFGHJKLZXCVBNM',5))
                uid += "-"
            uid = uid[0: len(uid) - 1]
            '最后把以上信息汇总到一起'
            appending = {
                'name': name,
                'artists': artists,
                'album': album,
                'music_filename': music_filename,
                'lyric_filename': lyric_filename,
                'cover_filename': cover_filename,
                'cover_link': cover_link,
                'music_link': music_link,
                'uid': uid,
                'id': now,
                'music_id': get_music[i]['id']
            }
            self.longlist.append(appending)
            now += 1
    def download_info_add(self, path, args):
        '针对每首歌都添加参数和地址'
        for i in range(len(self.longlist)):
            '补充斜杠'
            if path[len(path) - 1] != "/": path += "/"
            self.longlist[i]['path'] = path
            '参数第一项是是否分类文件夹，为true自动添加一个uid子文件夹'
            if args[0]:
                self.longlist[i]['path'] += self.playlist_name + "/"
            '参数第2-5项'
            self.longlist[i]['path'] += self.longlist[i]['uid'] + "/"
            self.longlist[i]['path'] = self.longlist[i]['path'].replace("/","\\")
            self.longlist[i]['args'] = args[1: len(args)]
    def download_main(self, thread_sum):
        self.download_status = []
        for i in self.longlist:
            self.download_status.append({
                'state': 0,
                'value': "Waiting",
                'name': i['name'] + " - " + i['artists']
            })
        self.total_size = len(self.longlist)
        self.now_size = 0
        self.failure_size = 0
        self.success_size = 0
        thread_controller = threading.Semaphore(thread_sum)
        for i in self.longlist:
            '向music内参传入playlist外参就能让它修改文件了（吧？）'
            thread = music(i, thread_controller, self)
            thread.start()
            time.sleep(0)

class music(threading.Thread):
    def __init__(self, info, thread_controller, father):
        threading.Thread.__init__(self)
        self.info = info
        self.thread_controller = thread_controller
        self.father = father
        self.music_download = self.info['args'][0]
        self.lyric_download = self.info['args'][1]
        self.cover_download = self.info['args'][2]
        self.attribute_write = self.info['args'][3]
        self.id = self.info['id']
    def run(self):
        with self.thread_controller:
            try: os.makedirs(self.info['path'])
            except: pass
            '下载音乐'
            if self.music_download: 
                self.father.download_status[self.id]['state'] = 1
                music_file = open(self.info['path'] + self.info['music_filename'],'wb+')
                '获取请求头'
                while True:
                    try: music_source = requests.get(self.info['music_link'], allow_redirects = True, stream = True)
                    except: pass
                    else: break
                '计数器'
                rate = int(0)
                if music_source.headers['Content-Type'] == 'text/html;charset=utf8':
                    music_file.close()
                    time.sleep(0.05)
                    os.remove(self.info['path'] + self.info['music_filename'])
                    os.removedirs(self.info['path'])
                    self.father.download_status[self.id]['value'] = "Error:It's a VIP song, so we can't download it."
                    self.father.download_status[self.id]['state'] = 6
                    self.father.failure_size += 1
                    self.father.now_size += 1
                    return None
                else: totalsize = int(music_source.headers['Content-Length'])
                '开始下载'
                for data in music_source.iter_content(chunk_size = 1024):
                    music_file.write(data)
                    rate += len(data)
                    self.father.download_status[self.id]['value'] = round(float(rate / totalsize), 2)
                    
                    '别一直干活，人总是要休息的，服务器也一样，别累坏人家了'
                    if random.randint(0,1000) % 200 == 0:
                        time.sleep(0.01)     
                music_file.close()
                time.sleep(0.5)
            '歌词下载'
            if self.lyric_download: 
                self.father.download_status[self.id]['state'] = 2
                self.father.download_status[self.id]['value'] = 0
                lyric_file = open(self.info['path'] + self.info['lyric_filename'],'w+',encoding = 'utf-8')
                '调用api'
                global lyric_api
                '请求歌词'
                while True:
                    try: data = Netease_params({
                        'csrf_token':"",
                        'id':self.info['music_id'],
                        'lv':'-1',
                        'tv':'-1'}).run(lyric_api)
                    except: pass
                    else: break
                '写入并替换换行符'
                lyric_file.write(data['lrc']['lyric'].replace("\n",'\n'))
                lyric_file.close()
                self.father.download_status[self.id]['value'] = 1
                time.sleep(0.5)
            '封面下载'
            if self.cover_download: 
                self.father.download_status[self.id]['state'] = 3
                self.father.download_status[self.id]['value'] = 0
                cover_file = open(self.info['path'] + self.info['cover_filename'],'wb+')
                '获取请求头'
                while True:
                    try: cover_source = requests.get(self.info['cover_link'], allow_redirects = True, stream = True)
                    except: pass
                    else: break
                '计数器'
                rate = int(0)
                totalsize = int(cover_source.headers['Content-Length'])
                '开始下载'
                for data in cover_source.iter_content(chunk_size = 1024):
                    cover_file.write(data)
                    rate += len(data)
                    self.father.download_status[self.id]['value'] = round(float(rate / totalsize * 0.8), 2)
                    '别一直干活，人总是要休息的，服务器也一样，别累坏人家了'
                    if random.randint(0,1000) % 200 == 0:
                        time.sleep(0.01)
                cover_file.close()
                '换一种打开方式'
                cover_file = Image.open(self.info['path'] + self.info['cover_filename'])
                '更换通道'
                cover_file = cover_file.convert("RGB")
                cover_file_type = cover_file.format
                '压缩边长'
                cover_file_out = cover_file.resize((800,800), Image.NEAREST)
                '保存'
                cover_file_out.save(self.info['path'] + self.info['cover_filename'], cover_file_type)
                self.father.download_status[self.id]['value'] = 1
                time.sleep(0.5)
            '属性填写'
            if self.attribute_write: 
                '利用eyed3完成第一步骤'
                self.father.download_status[self.id]['state'] = 4
                self.father.download_status[self.id]['value'] = 0
                music_file = eyed3.load(self.info['path'] + self.info['music_filename'])
                music_file.tag.artist = self.info['artists']
                self.father.download_status[self.id]['value'] = 0.25
                music_file.tag.artist = self.info['album']
                self.father.download_status[self.id]['value'] = 0.5
                music_file.tag.save()
                '改用ID3完成第二步骤，需要图像文件支持'
                if self.cover_download:
                    cover_file = open(self.info['path'] + self.info['cover_filename'],'rb+')
                    music_file = ID3(self.info['path'] + self.info['music_filename'])
                    music_file.add(APIC(encoding = 3,mime = 'image/jpeg',type = 3,desc = u'Cover',data = cover_file.read()))
                    music_file.save(v2_version = 3)
                    cover_file.close()
                    '过 河 拆 桥'
                    os.remove(self.info['path'] + self.info['cover_filename'])
                self.father.download_status[self.id]['value'] = 1
                time.sleep(0.5)
            '最后的修改：剪切并删除文件夹'
            self.father.download_status[self.id]['state'] = 5
            self.father.download_status[self.id]['value'] = "Finishing"
            self.copy_to_path = self.info['path'][0: len(self.info['path']) - 31]
            try: shutil.move(self.info['path'] + self.info['music_filename'], self.copy_to_path)
            except: 
                os.remove(self.copy_to_path + "\\" + self.info['music_filename'])
                shutil.move(self.info['path'] + self.info['music_filename'], self.copy_to_path)
            try: shutil.move(self.info['path'] + self.info['lyric_filename'], self.copy_to_path)
            except: 
                os.remove(self.copy_to_path + "\\" + self.info['lyric_filename'])
                shutil.move(self.info['path'] + self.info['lyric_filename'], self.copy_to_path)
            shutil.rmtree(self.info['path'])
            self.father.download_status[self.id]['state'] = 6
            self.father.download_status[self.id]['value'] = "Successful"
            self.father.now_size += 1
            self.father.success_size += 1
            return None

'''----------入门教学----------'''
'''定义类 '''
# p = playlist("YOUR ID HERE")
'''定义完不会自动获取数据，请对它下读取命令''' 
# p.data_get()
'''
下载启动前请存入下载信息，分别是
("存储路径",[歌单文件夹分类(T/F),下载歌曲(T/F),下载歌词(T/F),下载专辑封面(T/F),属性编辑(T/F)])
(T/F)代表该部分填入True/False。
'''
# p.download_info_add("D:/Test",[True,True,True,True,True])
'''下载开始时请传入线程数量'''
# p.download_main(4)
'''
其他信息
p.longlist - 歌曲全部信息
p.now_size - 下载进度
p.success_size - 下载成功的个数
p.failure_size - 下载失败的个数
p.total_size - 歌曲总数
download_status - 下载详情，以[{'state':数字,'value':数值或报错,'name':歌曲名称},...]组成
以下是例子
它的输出：
进度: 0.0% (0/0/10)
进度: 0.0% (0/0/10)
......
进度: 70.0% (7/0/10)
进度: 70.0% (7/0/10)
进度: 90.0% (9/0/10)
成功: 10; 失败: 0
'''
'''
while p.now_size != p.total_size:
    now = round(p.now_size / p.total_size * 100, 3)
    print("进度: " + str(now) + "% (" + str(p.success_size) + "/" + str(p.failure_size) + "/" + str(p.total_size) + ")")
    time.sleep(1)
print("成功: " + str(p.success_size) + "; 失败: " + str(p.failure_size))
'''