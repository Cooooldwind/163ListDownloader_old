import time,requests,os,eyed3,multitasking,base64
from tkinter import *
from params_encSecKey import *
from eyed3.id3.frames import ImageFrame
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error
from NC_Logo import img



root = Tk()
info_screen = Tk()
isRunning = False
playlist_UserID = 0



def Get_Listinfo(ID):
    playlist_api = 'https://music.163.com/weapi/v6/playlist/detail?'
    try:
        response = Netease_params({'csrf_token': "", 'id': str(ID), 'n': "0"}).run(playlist_api)['playlist']
    except KeyError: return "ListGetError"
    else: pass
    playlist_UserID = response['userId']
    playlist_info = dict()
    playlist_info['name'] = response['name']
    playlist_info['description'] = response['description']
    playlist_info['songs'] = []
    id_list = [i['id'] for i in response['trackIds']]
    for i in id_list:
        info = {'id':i}
        playlist_info['songs'].append(info)
    return playlist_info



def Get_Songinfo(ID):
    song_api = 'https://music.163.com/weapi/v3/song/detail'
    while True:
        try:
            response = Netease_params({'c': str(ID),'csrf_token': '','userId': playlist_UserID}).run(song_api)['songs']
        except TimeoutError: return "SongGetError"
        else: break
    song_info = []
    
    for i in range(len(response)):
        artist_list = ""
        for j in response[i]['ar']:
            artist_list = artist_list + j['name'] + ","
        appending = {
            'name':response[i]['name'],
            'id':response[i]['id'],
            'artists':artist_list[0:len(artist_list) - 1],
            'album':response[i]['al']['name'],
            'album_picture':response[i]['al']['picUrl']
        }
        song_info.append(appending)

    return song_info



def Download_Music(Info,Path):
    filename = f"{Info['name']} - {Info['artists']}.mp3"
    url = f"https://music.163.com/song/media/outer/url?id={Info['id']}.mp3"
    dirty = ["/","\\",":","*","\"","?","|","<",">"]
    for stuff in dirty:
        filename = filename.replace(stuff,"")
    filename = Path + filename
    while True:
        try: file_get = requests.get(url,allow_redirects = True)
        except ConnectionResetError: break
        else: break
    save_file = open(filename,'wb+')
    save_file.write(file_get.content)
    save_file.close()



def Download_Lyric(Info,Path):
    filename_Display = Info['name'] + "-" + Info['artists']
    lyric_api = 'https://music.163.com/weapi/song/lyric?csrf_token='
    lyric_Return = Netease_params({'csrf_token':"", 'id':Info['id'], 'lv':'-1', 'tv':'-1'}).run(lyric_api)
    lyric_Return = lyric_Return['lrc']['lyric'].replace("\n",'\n')
    filename = f"{Info['name']} - {Info['artists']}.lrc"
    dirty = ["/","\\",":","*","\"","?","|","<",">"]
    for stuff in dirty:
        filename = filename.replace(stuff,"")
    filename = Path + filename
    save_file = open(filename,'w+',encoding = 'UTF-8')
    save_file.write(lyric_Return)
    save_file.close()



def Download_Cover(Info,Path):
    pic_fileurl = Info['album_picture']
    filename = f"{Info['name']} - {Info['artists']}.mp3"
    dirty = ["/","\\",":","*","\"","?","|","<",">"]
    for stuff in dirty:
        filename = filename.replace(stuff,"")
    filename = Path + filename
    pic_get = requests.get(pic_fileurl,allow_redirects = True)
    pic_filename = f"{Info['name']} - {Info['artists']}.jpg"
    dirty = ["/","\\",":","*","\"","?","|","<",">"]
    for stuff in dirty:
        pic_filename = pic_filename.replace(stuff,"")
    pic_filename = Path + pic_filename
    save_file = open(pic_filename,'wb+')
    save_file.write(pic_get.content)
    save_file.close()
    pic_file = open(pic_filename,'rb+')
    audio = ID3(filename)
    audio.update_to_v23()
    audio.add(APIC(encoding = 3,mine = 'image/jpeg',type = 3,desc = u'Cover',data = pic_file.read()))
    audio.save(v2_version=3)
    pic_file.close()
    os.remove(pic_filename)
    



def Edit_Attribute(Info,Path):
    filename = f"{Info['name']} - {Info['artists']}.mp3"
    dirty = ["/","\\",":","*","\"","?","|","<",">"]
    for stuff in dirty:
        filename = filename.replace(stuff,"")
    filename = Path + filename
    audiofile = eyed3.load(filename)
    audiofile.tag.artist = Info['artists']
    audiofile.tag.title = Info['name']
    audiofile.tag.album = Info['album']
    audiofile.tag.save()



def Download_Main(ID,isMusic,isLyric,isCover,isAttribute):
    multitasking.set_max_threads(128)
    global isRunning
    if isRunning == True:
        download_Info.insert("end",f"正在下载其他歌单！")
        return
    isRunning = True
    download_Num = 0
    successful_Num = 0
    list_Info = Get_Listinfo(ID)
    song_Info = Get_Songinfo(list_Info['songs'])
    try: os.mkdir(f"NC_Download//")
    except FileExistsError: pass
    dirty = ["/","\\",":","*","\"","?","|","<",">"]
    for stuff in dirty:
        list_Info['name'] = list_Info['name'].replace(stuff,"")
    try: os.mkdir(f"NC_Download//{list_Info['name']}//")
    except FileExistsError: pass
    Path = f"NC_Download//{list_Info['name']}//"
    while download_Num < len(song_Info):
        clear_name = song_Info[download_Num]['name']
        clear_artists = song_Info[download_Num]['artists']
        dirty = ["/","\\",":","*","\"","?","|","<",">"]
        for stuff in dirty:
            clear_name = clear_name.replace(stuff,"")
            clear_artists = clear_artists.replace(stuff,"")
        if isMusic == 1:
            Download_Music(song_Info[download_Num],Path)
            #判断VIP
            audiofile = eyed3.load(Path + f"{clear_name} - {clear_artists}.mp3")
            try: audiofile.tag.artist = song_Info[download_Num]['artists']
            except AttributeError:
                os.remove(Path + f"{clear_name} - {clear_artists}.mp3")
                download_Num += 1
                download_Info.insert("end",f"下载失败: {clear_name} - {clear_artists}")
                continue
            else:
                download_Info.insert("end",f"歌曲下载成功：{successful_Num + 1}/{len(song_Info)}: {clear_name} - {clear_artists}")
                download_Info.update()
        time.sleep(0.1)
        if isCover == 1: 
            Download_Cover(song_Info[download_Num],Path)
            download_Info.insert("end",f"封面添加成功：{successful_Num + 1}/{len(song_Info)}: {clear_name} - {clear_artists}")
            download_Info.update()
        time.sleep(0.1)
        if isAttribute == 1: 
            Edit_Attribute(song_Info[download_Num],Path)
            download_Info.insert("end",f"属性添加成功：{successful_Num + 1}/{len(song_Info)}: {clear_name} - {clear_artists}")
            download_Info.update()
        time.sleep(0.1)
        if isLyric == 1: 
            Download_Lyric(song_Info[download_Num],Path)
            download_Info.insert("end",f"歌词下载成功：{successful_Num + 1}/{len(song_Info)}: {clear_name} - {clear_artists}")
            download_Info.update()
        time.sleep(0.1)
        download_Info.insert("end",f"完成所有选项：{successful_Num + 1}/{len(song_Info)}: {clear_name} - {clear_artists}")
        download_Info.update()
        download_Num += 1
        successful_Num += 1
    download_Info.insert("end",f"成功下载{successful_Num}/{len(song_Info)}首! ")
    os.system(f"explorer.exe NC_Download")
    isRunning = False



if __name__ == "__main__":
    root.title("NeteaseCrabber V1.2.0 By Cooooldwind_")
    tmp = open("tmp.ico","wb+")
    tmp.write(base64.b64decode(img))
    tmp.close()
    root.iconbitmap("tmp.ico")
    Playlist_ID = StringVar()
    id_Text = Label(root,bd=0,text="输入ID: ")
    id_Entry = Entry(root,textvariable = Playlist_ID)
    isLyric = IntVar()
    isCover = IntVar()
    isMusic = IntVar()
    isAttribute = IntVar()    
    lyric_Check = Checkbutton(root,text = "歌词下载",bd=0,variable = isLyric,onvalue = 1,offvalue = 0)
    cover_Check = Checkbutton(root,text = "封面下载",bd=0,variable = isCover,onvalue = 1,offvalue = 0,takefocus = False)
    music_Check = Checkbutton(root,text = "歌曲下载",bd=0,variable = isMusic,onvalue = 1,offvalue = 0)
    attribute_Check = Checkbutton(root,text = "属性编辑",bd=0,variable = isAttribute,onvalue = 1,offvalue = 0,takefocus = False)
    start_Button = Button(root,text = "开始",width = 10,command = lambda:Download_Main(Playlist_ID.get(),isMusic.get(),isLyric.get(),isCover.get(),isAttribute.get()))
    id_Text.grid(row = 0,column = 1)
    id_Entry.grid(row = 0,column = 2)
    music_Check.grid(row = 0,column = 3)
    attribute_Check.grid(row = 0,column = 4)
    lyric_Check.grid(row = 0,column = 5)
    cover_Check.grid(row = 0,column = 6)
    start_Button.grid(row = 0,column = 7)
    info_screen.title(f"NeteaseCrabber Log")
    info_screen.iconbitmap("tmp.ico")
    os.remove("tmp.ico")
    download_Info = Listbox(info_screen,bd=0,width=60,takefocus=False,height=8,yscrollcommand="")
    download_Info.grid(row = 1,column = 1)
    root.mainloop()
    info_screen.mainloop()
   
# 更新日志 Ver.1.2.0:
# 1. 新增：
# (1) 更新图形化界面（用tkinter写的）；
# (2) 下载后自动打开文件夹；
# (3) Logo在GUI上的显示；
# (4) 解除对下载私密歌单的限制（私密歌单的ID可以在网页版里登录自己账号获取）；
# (1) 往mp3文件里添加封面；
# 2. 部分函数重置；
# 3. 修复bug (#1200000001)： 文件夹名字（也就是歌单名）里的特殊字符没法被移除，导致存不上文件。