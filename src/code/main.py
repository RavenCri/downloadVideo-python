import re
import sys
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
from fileUtil.fileUtil import *
from httpreq.online import updateData


def initWindow():
    global alignstr
    # 设置窗口大小
    width = 600
    height = 600
    # 设置标题
    myWindow.title('视频下载器（@version:1.0.0）')
    myWindow.resizable(width=False, height=False)
    # 获取屏幕尺寸以计算布局参数，使窗口居屏幕中央
    screenwidth = myWindow.winfo_screenwidth()
    screenheight = myWindow.winfo_screenheight()
    alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width ) /2, (screenheight - height ) /2)
    myWindow.geometry(alignstr)
    # 设置窗口是否可变长、宽，True：可变，False：不可变
    myWindow.resizable(width=False, height=True)
    # 设置关闭事件
    myWindow.protocol('WM_DELETE_WINDOW', on_closing2)
    # 隐藏窗口
    # myWindow.withdraw()
    # 显示窗口
    #top.update()
    #top.deiconify()
'''
    选择周数将会触发重新读取视频json文件
'''
def wedFunc(wedSelect ,wedMap):
    global videoRescous
    # print((int(wedMap[wedSelect.get()]) +1))
    if wedMap[wedSelect.get()] == '00':
        for i in range(1 ,len(wedMap.keys())):
            videoRescous[str(i)] = readFile("video%d.json" %  (i))[str(i)]
    else:
        videoRescous = readFile("video%d.json" %  (int(wedMap[wedSelect.get()]) +1))
    # print(videoRescous)
    gradesBox()
    subjectBox()
    editionBox()


'''
    选择学段后将会更新年级、科目、出版社
'''


def phasesFunc(phasesSelect):
    gradesBox()
    subjectBox()
    editionBox()


'''
    更新年级后将会更新科目、出版社
'''


def gradesFunc(gradesSelect):
    subjectBox()
    editionBox()


'''
    更新科目后将会更新出版社
'''


def subjectsFunc(subjectsSelect):
    editionBox()


'''
     当点击了选中所有视频
'''


def selectAllItem():
    global checkVar, videos,selectVar
    #print(checkVar.get())
    # 如果之前的状态是没有选择，那么直接全选，否则全部取消选择
    if checkVar.get() == 0:
        listBox.select_clear(0, len(videos) - 1)
        selectVar.set('共获取到：%d个视频,已选中%d个' % (len(videos), 0))
    else:
        listBox.select_set(0, len(videos) - 1)
        selectVar.set('共获取到：%d个视频,已选中%d个' % (len(videos), len(videos)))


'''
    用于加载视频
'''


def load():
    listBox.delete(0, tk.END)
    videos.clear()
    global checkVar, selectVar
    i = 0
    print("学段编码：" + pha[phasesSelect.get()])
    print("年级编码：" + grad[gradesSelect.get()])
    print("科目编码：" + subj[subjectsSelect.get()])
    print("出版编码：" + edit[editionsSelect.get()])

    # 遍历加载好的视频
    for index, item in enumerate(videoRescous):
        # 取出视频条目 是个json对象
        for video in videoRescous[item]:
            # 如果视频与所选择的项目匹配，则添加到列表框
            if (pha[phasesSelect.get()] == '00' or video['phase'] == pha[phasesSelect.get()]) and \
                    (grad[gradesSelect.get()] == '00' or video['grade'].find(grad[gradesSelect.get()]) >= 0) and \
                    (subj[subjectsSelect.get()] == '00' or video['subject'] == subj[subjectsSelect.get()]) and \
                    (edit[editionsSelect.get()] == '00' or video['edition'] == edit[editionsSelect.get()]):
                videos.append(video)
                i += 1
                listBox.insert(tk.END, str(i) + "、" + video['package_name'])

    selectVar = tk.StringVar()
    selectVar.set('共获取到：%d个视频,已选中0个' % len(videos))

    tip = tk.Label(myWindow, textvariable=selectVar, bg='#DA70D6', fg="white", font=('Arial', 12))
    tip.place(x=200, y=460)

    checkVar = tk.IntVar()

    selectAll = tk.Checkbutton(myWindow, text="选中所有视频", variable=checkVar,
                               onvalue=1, offvalue=0, height=1, command=selectAllItem)
    selectAll.place(x=250, y=490)


'''
    点击下载视频触发
'''


def downLoadVideo():
    global selectIndexs, downPath
    selectIndexs = listBox.curselection()
    # print(selectIndexs)
    if len(selectIndexs) == 0:
        messagebox.showwarning('选中为空', '选中项为空，请先获取视频！')
        return
    else:
        downPath = filedialog.askdirectory()
        downPath = downPath.replace('/', '\\')
        if downPath != '':
            # 获取时间 生成文件夹保存视频
            t = time.gmtime()
            print("您选择的文件是：" + downPath)
            downPath = os.path.join(downPath, time.strftime("video-%Y-%m-%d-%H-%M-%S"))
            run()

        else:
            print("取消了下载")

# 开启UI更新、以及下载视频的线程
def run():
    global total_size,temp_size,percent,currVar,var_progress_bar_percent,speedSecond,var_progress_bar_percent

    total_size = 0
    #
    temp_size = 0

    percent = 0
    #下载速度
    speedSecond = '0kb/s'
    currVar = tk.StringVar()
    var_progress_bar_percent = tk.StringVar()
    # 显示下载进度界面
    downWindowThread = threading.Thread(target=showDownUI)
    #downWindowThread.setDaemon(True)
    downWindowThread.start()
    # 下载线程
    dowmThread = threading.Thread(target=downVideo)
    #dowmThread.setDaemon(True)
    dowmThread.start()
    # UI更新线程
    UiThread = threading.Thread(target=flushUi)
    #UiThread.setDaemon(True)
    UiThread.start()

    timeThread = threading.Thread(target=flushTime)
    #timeThread.setDaemon(True)
    timeThread.start()
'''
    UI界面刷新（更新下载进度、当前下载视频内容）
'''

def flushTime():
    global percent
    while True:
        percent += 1
        time.sleep(1)



def flushUi():
    global total_size,temp_size,speedSecond,var_progress_bar_percent

    while True and not closeWindow:
        hour = int(percent / 3600)
        minute = int(percent / 60) - hour * 60
        second = percent % 60
        if total_size != 0:
            # 计算绿线的距离
            green_length = int(500 * temp_size/ total_size)
            # 画定义好的长方体
            canvas_progress_bar.coords(canvas_shape, (0, 0, green_length, 25))
            # 设置时间
            canvas_progress_bar.itemconfig(canvas_text, text='已用时间：%02d:%02d:%02d 当前任务进度：%0.2f%%(下载速率：%s)' %
                                                             (hour, minute, second,100*temp_size/ total_size,speedSecond))
            # 设置百分比
            var_progress_bar_percent.set('%0.2f %%' % (100*temp_size/ total_size))
            time.sleep(0.05)
            # print("UI的done:" + str(done))


'''
    用于下载视频
'''


def downVideo():
    global total_size,temp_size, closeWindow,top,currVar,done,speedSecond
    temp_size = 0
    os.mkdir(downPath)

    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.13 Safari/537.36",
        "Referer": "http://jiaoxue.ahedu.cn/index.html"
    }


    for index, item in enumerate(selectIndexs):
        currVar.set("共有%d个任务,当前下载第%d个视频:%s" % (
            len(selectIndexs), (index + 1), videos[selectIndexs[index]]['package_name']))

        fileName = "第%s课时-%s-%s-%s-%s" % (
            videos[item]['class_period'],
            # (int(wedMap[wedSelect.get()])+1)*5,
            contect['GLOBAL_GRADES'][videos[selectIndexs[index]]['grade']]['name'],
            contect['GLOBAL_SUBJECTS'][videos[selectIndexs[index]]['subject']]['name'],
            contect['GLOBAL_EDITIONS'][videos[selectIndexs[index]]['edition']]['name'],
            re.sub('[\/:*?"<>|]', '-', videos[item]['package_name']))
        r = requests.get(videos[item]['url'], headers=header, stream=True, verify=False)
        print("当前链接：" + videos[item]['url'])
        # 既然要实现下载进度，那就要知道你文件大小啊，下面这句就是得到总大小
        total_size = int(r.headers['Content-Length'])
        temp_size = 0
        done = 0
        currPath = os.path.join(downPath, contect['GLOBAL_GRADES'][videos[selectIndexs[index]]['grade']]['name'],
                                contect['GLOBAL_SUBJECTS'][videos[selectIndexs[index]]['subject']]['name'],
                                contect['GLOBAL_EDITIONS'][videos[selectIndexs[index]]['edition']]['name']
                                )
        print(currPath)
        if not os.path.exists(currPath):
            os.makedirs(currPath)
        # 请求开始的时间
        start_time = time.time()
        # 上秒的下载大小
        last_size = 0
        with open(currPath + '\\' + fileName + "." + videos[item]['url'].split('.')[-1], 'wb') as f:

            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    temp_size += len(chunk)
                    f.write(chunk)
                    f.flush()
                    # sys.stdout.write(
                    #     "\r[%s%s] %d%%" % ('█' * done, ' ' * (50 - done), 100 * temp_size / total_size))
                    # sys.stdout.flush()
                    done = int(( temp_size / total_size) *100)

                    if time.time() - start_time > 1:
                        # 重置开始时间
                        start_time = time.time()
                        # 每秒的下载量
                        speed = temp_size - last_size

                        # KB级下载速度处理
                        if 0 <= speed < (1024 ** 2):
                            speedSecond = '%.2fKB/s' % (speed / 1024)

                        # MB级下载速度处理
                        elif (1024 ** 2) <= speed < (1024 ** 3):
                            speedSecond = '%.2fMB/s'% (speed / (1024 ** 2) )

                        # GB级下载速度处理
                        elif (1024 ** 3) <= speed < (1024 ** 4):
                            speedSecond = '%.2fGB/s' % (speed / (1024 ** 3))
                        # TB级下载速度处理
                        else:
                            speedSecond = '%.2f TB/s' % (speed / (1024 ** 4))
                        # 重置以下载大小
                        last_size = temp_size
                        #print(speedSecond)
                    if closeWindow:
                        print("用户取消下载")
                        return
    messagebox.showinfo("下载完成", "您的任务已下载完毕~")
    top.withdraw()
    closeWindow = True
    # 下载完弹出下载文件夹 方便查看
    os.system("start explorer " + downPath.replace('/', '\\'))

'''
    关闭下载窗口时
'''
def on_closing():
    global closeWindow
    if messagebox.askyesno("Quit", "关闭窗口将会取消下载任务！确认要关闭窗口吗？"):
        top.withdraw()
        closeWindow = True


'''
    关闭主窗口时
'''
def on_closing2():
    global closeWindow,top
    flag = False
    if closeWindow :
        flag =messagebox.askyesno("Quit", "关闭窗口将会取消下载任务！确认要关闭窗口吗？")
    else:
        flag = messagebox.askyesno("Quit", "确认要退出程序吗？")
    if flag:
        myWindow.destroy()
    try:
        top.destroy()
    except:
        print("窗口未定义")


def showDownUI():
    global canvas_progress_bar, canvas_shape, canvas_text, closeWindow,top
    top = tk.Tk()
    top.title('下载进程')
    closeWindow = False
    screenwidth = top.winfo_screenwidth()
    screenheight = top.winfo_screenheight()
    alignstr = '%dx%d+%d+%d' % (700, 200, (screenwidth - 700) / 2, (screenheight - 200) / 2)
    top.geometry(alignstr)
    top.resizable(False, False)
    top.config(bg='#535353')
    # 进度条长度
    sum_length = 500
    # 画一个进度条
    canvas_progress_bar = tk.Canvas(top, width=sum_length, height=20)
    # 创建绿色的长方体 （0,0）宽0 高25
    canvas_shape = canvas_progress_bar.create_rectangle(0, 0, 0, 25, fill='blue')
    # 创建文字（时间）
    canvas_text = canvas_progress_bar.create_text(100, 4, anchor=tk.NW)
    # 进度条添加文字
    canvas_progress_bar.itemconfig(canvas_text, text='已用时间：00:00:00',fill='red')
    # 设置进度条位置
    canvas_progress_bar.place(relx=0.45, rely=0.4, anchor=tk.CENTER)

    cu = tk.Label(top, text=currVar.get(), bg="white", fg="green", font=('Arial', 13))
    cu.place(x=20, y=20)

   # var_progress_bar_percent.set('00.00 %')
    var_progress_bar_percent.set('')
    # 百分比标签  不能正常显示 ！！！
    label_progress_bar_percent = tk.Label(top, text=var_progress_bar_percent.get(),fg='#F5F5F5', bg='#535353')
    label_progress_bar_percent.place(relx=0.89, rely=0.4, anchor=tk.CENTER)

    top.protocol('WM_DELETE_WINDOW', on_closing)

    top.mainloop()



'''
    点击列表视频 同步更新选中个数
'''


def listBoxMouseClick(event):
    global  selectVar
    # 如果选中大于0
    if len(videos) > 0:
        selectVar.set('共获取到：%d个视频,已选中%d个' % (len(videos), len(listBox.curselection())))
        # tip = tk.Label(myWindow, text=selectVar.get(), font=('Arial', 12), bg='green', fg="white")
        # tip.place(x=200, y=460)


'''
    用于更新窗口主要控件
'''


def initUI():
    global phasesSelect, subjectsSelect, editionsSelect, gradesSelect, listBox, wedSelect, wedMap
    wed = tk.Label(myWindow, text='周数：', font=('Arial', 12))
    wedMap = {
        '全部周数': "00",
        '第一周3.2-3.6': "0",
        '第二周3.9-3.13': "1",
        '第三周3.16-3.20': "2",
        '第四周3.23-3.27': "3",
        '第五周3.30-4.3': "4"
    }
    recousePath = os.path.join(os.path.abspath('../'), "rescouse")
    files = os.listdir(recousePath)
    fileNum = len(files)
    # 因为目前只有五周的课程，后面应该显示更新后的课程
    while fileNum > 6:
        key = '第%d周' % (fileNum - 1)
        val = ('%d' % (fileNum - 2))
        wedMap[key] = val
        fileNum -= 1

    wed.place(x=200, y=20)
    wedSelect = ttk.Combobox(myWindow)
    wedSelect.pack()
    wedSelect.bind("<<ComboboxSelected>>", lambda event: wedFunc(wedSelect, wedMap))
    wedSelect['value'] = list(wedMap.keys())
    wedSelect.place(x=260, y=20)
    # 默认选中最后一个
    wedSelect.current(len(wedSelect['value']) - 1)

    '''
               初始化年级阶段
    '''
    global phasesSelect, subjectsSelect, editionsSelect, gradesSelect, listBox
    phases = tk.Label(myWindow, text='学段：', font=('Arial', 12))
    phases.place(x=200, y=60)
    phasesSelect = ttk.Combobox(myWindow)
    phasesSelect.pack()
    phasesSelect.bind("<<ComboboxSelected>>", lambda event: phasesFunc(phasesSelect))  # #给下拉菜单绑定事件
    # 执行初始化更新
    phasesBox()

    '''
           初始化年级
    '''
    grades = tk.Label(myWindow, text='年级：', font=('Arial', 12))
    grades.place(x=200, y=100)
    gradesSelect = ttk.Combobox(myWindow)
    gradesSelect.pack()
    gradesSelect.bind("<<ComboboxSelected>>", lambda event: gradesFunc(gradesSelect))  # #给下拉菜单绑定事件
    # 执行初始化更新
    gradesBox()
    '''
             初始化科目
    '''
    subjects = tk.Label(myWindow, text='学科：', font=('Arial', 12))
    subjects.place(x=200, y=140)
    subjectsSelect = ttk.Combobox(myWindow)
    subjectsSelect.pack()
    subjectsSelect.bind("<<ComboboxSelected>>", lambda event: subjectsFunc(subjectsSelect))
    subjectBox()

    '''
         初始化出版社
    '''
    editions = tk.Label(myWindow, text='出版社：', font=('Arial', 12))
    editions.place(x=200, y=180)
    editionsSelect = ttk.Combobox(myWindow)
    editionsSelect.pack()
    editionBox()

    button = tk.Button(myWindow, text="获取视频", font=('Arial', 12), command=load, bg="white")
    button.place(x=270, y=220)

    listBox = tk.Listbox(myWindow, selectmode=tk.MULTIPLE, width=80)
    listBox.place(x=20, y=260)
    '''
        <Button-1>  鼠标左键
        <Button-2>   鼠标中间键（滚轮）
        <Button-3>  鼠标右键
        <Double-Button-1>   双击鼠标左键
        <Double-Button-3>   双击鼠标右键
        <Triple-Button-1>   三击鼠标左键
        <Triple-Button-3>   三击鼠标右键
    '''
    listBox.bind('<<ListboxSelect>>', listBoxMouseClick)
    siveButton = tk.Button(myWindow, text="下载视频", width=20, font=('Arial', 15), command=downLoadVideo, bg="white")
    siveButton.place(x=190, y=520)

    auther = tk.Label(myWindow, text='@Raven版权所有（2020）', font=('华文行楷', 12), bg='blue', fg="white")
    auther.place(x=220, y=570)


'''
    选择学段
'''


def phasesBox():
    global pha
    # 用于保存要显示的学段
    pha = {}
    # 把科目的名字和代码编号保存到pha变量
    for ph in contect['GLOBAL_PHASES']:
        pha[ph['name']] = ph['code']
    phasesSelect['value'] = list(pha.keys())
    phasesSelect.place(x=260, y=60)
    phasesSelect.current(0)


'''
    用于年级因级联操作带来的更新
'''


def gradesBox():
    global grad

    grad = {}
    grad['全部年级'] = '00'
    for gr in contect['GLOBAL_GRADES'].keys():
        # print(contect['GLOBAL_GRADES'][gr]['phaseCode'])
        # 如果是学段满足 ，则添加该年级 到要显示的列表
        if contect['GLOBAL_GRADES'][gr]['phaseCode'] == pha[phasesSelect.get()] or pha[phasesSelect.get()] == '00':
            # 保存年级名称和它的编码
            grad[contect['GLOBAL_GRADES'][gr]['name']] = contect['GLOBAL_GRADES'][gr]['code']

    gradList = list(grad.keys())
    gradesSelect['value'] = gradList
    gradesSelect.place(x=260, y=100)
    gradesSelect.current(0)


'''
       初始化科目
'''


def subjectBox():
    global subj
    # 用于保存要显示的科目
    subj = {}
    subj['全部科目'] = '00'
    show_subj_code = {}
    # 如果不是全部年级的话，筛选出该年级的科目
    # if grad[gradesSelect.get()] != '00':
    # 找出该年级有的所有科目
    for gradChid in contect['GLOBAL_GRADES']:
        # print(contect['GLOBAL_GRADES'][gradChid]['name'] )
        # 如果年级匹配 或者 学段匹配 则 保存 应该出现的科目
        if (contect['GLOBAL_GRADES'][gradChid]['name'] == gradesSelect.get() or grad[gradesSelect.get()] == '00') and \
                contect['GLOBAL_GRADES'][gradChid]['phaseCode'] == pha[phasesSelect.get()]:
            # print(contect['GLOBAL_GRADES'][gradChid])
            for g in contect['GLOBAL_GRADES'][gradChid]['childrenCodes']:
                # print(contect['GLOBAL_GRADES'][gradChid]['phaseCode'])
                # 年级代码  阶段代码
                show_subj_code[g['subjectCode']] = contect['GLOBAL_GRADES'][gradChid]['phaseCode']

    for su in contect['GLOBAL_SUBJECTS'].keys():

        # 如果科目编码相同 或者选中了所有科目 ，则把科目添加到要显示的科目里
        if (contect['GLOBAL_SUBJECTS'][su]['code'] in show_subj_code.keys() or pha[phasesSelect.get()] == '00'):
            subj[contect['GLOBAL_SUBJECTS'][su]['name']] = contect['GLOBAL_SUBJECTS'][su]['code']

    print("显示的科目" + str(list(subj.keys())))
    subjList = list(subj.keys())
    subjectsSelect['value'] = subjList
    subjectsSelect.place(x=260, y=140)
    subjectsSelect.current(0)


def editionBox():
    '''
           初始化出版社
    '''

    global edit
    # 用于保存要显示的出版社
    edit = {}
    show_edit_code = []
    # 如果不是全部科目的话，筛选出该科目的所有出版社
    if subj[subjectsSelect.get()] != '00':
        # 找出该学科有的所有出版社
        for gradChid in contect['GLOBAL_SUBJECTS']:

            # 如果学科编码与当前选择的一样，则取出它的子孩子编码 即为 该科目的所有出版社
            if contect['GLOBAL_SUBJECTS'][gradChid]['code'] == subj[subjectsSelect.get()]:
                print(contect['GLOBAL_SUBJECTS'][gradChid])
                show_edit_code = contect['GLOBAL_SUBJECTS'][gradChid]['childrenCodes']
        print("出版社" + str(show_edit_code))
    # print(grad)
    # 找到所有出版社
    for ed in contect['GLOBAL_EDITIONS'].keys():
        # 匹配出版社code，若 再要显示的列表里，则添加进去
        if (contect['GLOBAL_EDITIONS'][ed]['code'] in show_edit_code
                or subj[subjectsSelect.get()] == '00'):
            # 保存出版社的名字和编码即可
            edit[contect['GLOBAL_EDITIONS'][ed]['name']] = contect['GLOBAL_EDITIONS'][ed]['code']

    # 用于保存视频内容不为空的出版社
    temp = []
    for e in list(edit.keys()):
        for i in videoRescous:
            for index in videoRescous[i]:
                # 遍历所有 判断该出版社是否有视频 , 如果有的话放到临时列表里 等会遍历所有出版社，如果哪个出版社不在这个列表里
                # 则说明他没有视频文件，删除掉他。
                if (pha[phasesSelect.get()] == '00' or index['phase'].find(pha[phasesSelect.get()]) >= 0) and \
                        (grad[gradesSelect.get()] == '00' or index['grade'].find(grad[gradesSelect.get()]) >= 0) and \
                        index['subject'] == subj[subjectsSelect.get()] and \
                        index['edition'] == edit[e]:
                    if e not in temp:
                        temp.append(e)
                    continue;
    # 遍历当前要显示的出版社
    for t in list(edit.keys()):
        # 如果 不在该列表里 并且选择的科目不是全部 才删除
        if t not in temp and subj[subjectsSelect.get()] != '00':
            # print(t)
            del (edit[t])
    print(temp)
    edit['全部出版社'] = '00'
    editList = list(edit.keys())
    editionsSelect['value'] = editList
    editionsSelect.place(x=260, y=180)
    editionsSelect.current(len(edit.keys()) - 1)

if __name__ == '__main__':

    # 默认没有关闭窗口
    closeWindow = False
    videos = []


    # 初始化Tk()
    myWindow = tk.Tk()
    # 读取解析文件
    contect = readFile("contect.json")
    # 获取更新数据并返回最新一周的数据
    videoRescous = updateData()
    # 初始化主窗口
    initWindow()
    # 初始化窗口控件
    initUI()

    # 进入消息循环
    myWindow.mainloop()
    # pyinstaller -F -w -i i.ico main.py -p D:\pyCode\video\venv\Lib\site-packages
