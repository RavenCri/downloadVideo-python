from tkinter import messagebox
from tkinter import ttk
import tkinter.filedialog
import json
import os
import time
import requests
import threading
import tkinter as tk
from tkinter import *

def initWindow():
    global alignstr
    #设置窗口大小
    width = 600
    height = 600
    # 设置标题
    myWindow.title('视频下载器（@version:1.0.0）')

    #获取屏幕尺寸以计算布局参数，使窗口居屏幕中央
    screenwidth = myWindow.winfo_screenwidth()
    screenheight = myWindow.winfo_screenheight()
    alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth-width)/2, (screenheight-height)/2)
    myWindow.geometry(alignstr)
    # 设置窗口是否可变长、宽，True：可变，False：不可变
    myWindow.resizable(width=False, height=True)
def wedFunc(wedSelect,wedMap):
    global  videoRescous
    print((int(wedMap[wedSelect.get()]) +1))
    videoRescous = readFile("video%d.json" %  (int(wedMap[wedSelect.get()]) +1))
    print(videoRescous)
    gradesBox()
    subjectBox()
    editionBox()
def phasesFunc(phasesSelect):
    gradesBox()
    subjectBox()
    editionBox()
def gradesFunc(gradesSelect):
    subjectBox()
    editionBox()
def subjectsFunc(subjectsSelect):
    editionBox()
def selectAllItem():
    global checkVar,videos


    #print(checkVar.get())
    if checkVar.get() == 0:
        checkVar.set(1)
        listBox.select_set(0, len(videos) - 1)
        selectVar.set('共获取到：%d个视频,已选中%d个' % (len(videos), len(videos)))
        tip = tk.Label(myWindow, text=selectVar.get(), font=('Arial', 12), bg='green', fg="white")
    else:
        checkVar.set(0)
        listBox.select_clear(0, len(videos) - 1)
        selectVar.set('共获取到：%d个视频,已选中%d个' % (len(videos), 0))
        tip = tk.Label(myWindow, text=selectVar.get(), font=('Arial', 12), bg='green', fg="white")
    tip.place(x=200, y=460)
def load():

    #print(pha[phasesSelect.get()])
    #print(grad[gradesSelect.get()])
    #print(subj[subjectsSelect.get()])
    #print(edit[editionsSelect.get()])
    listBox.delete(0,END)
    videos.clear()
    global checkVar,selectVar
    i = 0;
    print(pha[phasesSelect.get()])
    print(grad[gradesSelect.get()])
    print(subj[subjectsSelect.get()])
    print(edit[editionsSelect.get()])
    for index,video in enumerate(videoRescous['content']):
        #print(video)
        #print(video)
        if (pha[phasesSelect.get()] == '00' or video['phase'] == pha[phasesSelect.get()]  ) and \
            (grad[gradesSelect.get()] == '00' or video['grade'].find(grad[gradesSelect.get()]) >= 0 ) and \
           (subj[subjectsSelect.get()] == '00' or video['subject'] == subj[subjectsSelect.get()]  ) and \
           (edit[editionsSelect.get()] == '00' or video['edition'] == edit[editionsSelect.get()]):
           videos.append(video)
           i += 1
           listBox.insert(index,str(i)+"、"+video['package_name'])
    selectVar = tk.StringVar()

    selectVar.set('共获取到：' + str(len(videos)) + '个视频,已选中0个')
    tip = tk.Label(myWindow, text =selectVar.get(),font=('Arial', 12),bg='green',fg="white")
    tip.place(x=200, y=460)

    checkVar = tk.IntVar()
    checkVar.set(0)
    selectAll = tk.Checkbutton(myWindow, text="选中所有视频", variable=checkVar, \
                     onvalue=1, offvalue=0, height=1,command=selectAllItem)
    selectAll.place(x=250,y=490)




def downLoadVideo():
    global selectIndexs,downPath
    selectIndexs = listBox.curselection()
    #print(selectIndexs)
    if len(selectIndexs) == 0:
        messagebox.showwarning('选中为空', '选中项为空，请先获取视频！')
        return
    else:

        #filename = tkinter.filedialog.askopenfilename()
        downPath = tkinter.filedialog.askdirectory()
        downPath = downPath.replace('/', '\\')
        if downPath != '':
            t = time.gmtime()
            print("您选择的文件是：" + downPath)
            downPath = os.path.join(downPath,time.strftime("video-%Y-%m-%d-%H-%M-%S"))
            show()
        else:
            print("取消了下载")
def run():

    dowmThread = threading.Thread(target=update_progress_bar)
    #dowmThread.setDaemon(True)
    dowmThread.start()
    UiThread = threading.Thread(target=UIFlush)
    #UiThread.setDaemon(True)
    UiThread.start()


def UIFlush():
    global done,top
    top.update()
    top.deiconify()

    percent = 0
    var_progress_bar_percent = tk.StringVar()
    var_progress_bar_percent.set('00.00 %')
    # 百分比标签
    label_progress_bar_percent = Label(top, textvariable=var_progress_bar_percent, fg='#F5F5F5', bg='#535353')

    label_progress_bar_percent.place(relx=0.89, rely=0.4, anchor=CENTER)

    while TRUE and not closeWindow:

        percent += 1
        hour = int(percent / 3600)
        minute = int(percent / 60) - hour * 60
        second = percent % 60
        green_length = int(10 * done)
        canvas_progress_bar.coords(canvas_shape, (0, 0, green_length, 25))
        #设置时间
        canvas_progress_bar.itemconfig(canvas_text, text='已用时间：%02d:%02d:%02d' % (hour, minute, second))
        # 设置百分比
        var_progress_bar_percent.set('%0.2f %%' % (done*2))
        time.sleep(1)
        #print("UI的done:" + str(done))
def update_progress_bar():
    global done,closeWindow
    os.mkdir(downPath)
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.13 Safari/537.36",
        "Referer": "http://jiaoxue.ahedu.cn/index.html"
    }
    currVar = tk.StringVar()

    for index,item in enumerate(selectIndexs):


        currVar.set("共有%d个任务,当前下载第%d个视频:%s" % (
            len(selectIndexs), (index + 1), videos[selectIndexs[index]]['package_name']))
        cu = tk.Label(top, text=currVar.get(), bg="white", fg="green", font=('Arial', 13))
        cu.place(x=20, y=20)
        #print(currVar.get())
        fileName = "%s-%s-%s-%s" % (
            contect['GLOBAL_GRADES'][ videos[selectIndexs[index]]['grade'] ]['name']
            ,
            contect['GLOBAL_SUBJECTS'][videos[selectIndexs[index]]['subject']]['name'],
            #subjectsSelect.get(),
            contect['GLOBAL_EDITIONS'][videos[selectIndexs[index]]['edition']]['name'],
            #editionsSelect.get(),
            videos[item]['package_name'])
        #print(fileName)
        r = requests.get(videos[item]['url'], headers=header, stream=True, verify=False)
        print("当前链接：" + videos[item]['url'])
        # 既然要实现下载进度，那就要知道你文件大小啊，下面这句就是得到总大小
        total_size = int(r.headers['Content-Length'])
        temp_size = 0
        done = 0

        currPath = os.path.join(  downPath,contect['GLOBAL_GRADES'][ videos[selectIndexs[index]]['grade'] ]['name'],
                                  contect['GLOBAL_SUBJECTS'][videos[selectIndexs[index]]['subject']]['name'],
                                  contect['GLOBAL_EDITIONS'][videos[selectIndexs[index]]['edition']]['name']
                                  )
        print(currPath)
        if  not os.path.exists(currPath):
            os.makedirs(currPath)
        with open(currPath+'\\' + fileName + "." + videos[item]['url'].split('.')[-1], 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024) :
                if chunk:
                    temp_size += len(chunk)
                    f.write(chunk)
                    f.flush()
                    done = int(50 * temp_size / total_size)
                    #print("下载的done:"+str(done))
                    if  closeWindow:
                        print("用户取消下载" )
                        return
    messagebox.showinfo("下载完成","您的任务已下载完毕~")
    top.withdraw()
    closeWindow = TRUE

    os.system("start explorer " + downPath.replace('/','\\'))

                   # sys.stdout.write(
                       # "\r[%s%s] %d%%" % ('█' * done, ' ' * (50 - done), 100 * temp_size / total_size))
                    #sys.stdout.flush()
def on_closing():
    global closeWindow
    if messagebox.askyesno("Quit", "关闭窗口将会取消下载任务！确认要关闭窗口吗？"):
        top.withdraw()
        closeWindow = TRUE
def on_closing2():
    global closeWindow

    if  closeWindow and messagebox.askyesno("Quit", "关闭窗口将会取消下载任务！确认要关闭窗口吗？"):
        top.destroy()
        myWindow.destroy()
    elif messagebox.askyesno("Quit", "确认要退出程序吗？"):
        myWindow.destroy()
        top.destroy()

def show():

    global canvas_progress_bar,sum_length,canvas_shape,canvas_text,closeWindow

    top.title('下载进程')
    closeWindow = FALSE
    screenwidth = top.winfo_screenwidth()
    screenheight = top.winfo_screenheight()
    alignstr = '%dx%d+%d+%d' % (630, 200, (screenwidth - 630) / 2, (screenheight - 200) / 2)
    top.geometry(alignstr)
    top.resizable(False, False)
    top.config(bg='#535353')
    # 进度条
    sum_length = 500
    # 画一个进度条
    canvas_progress_bar = Canvas(top, width=sum_length, height=20)
    #画一个绿色的长方体
    canvas_shape = canvas_progress_bar.create_rectangle(0, 0, 0, 25, fill='green')
    # 已用时间
    canvas_text = canvas_progress_bar.create_text(292, 4, anchor=NW)
    canvas_progress_bar.itemconfig(canvas_text, text='已用时间：00:00:00')


    #设置位置
    canvas_progress_bar.place(relx=0.45, rely=0.4, anchor=CENTER)

    # 按钮
    #button_start = Button(top, text='开始', fg='#F5F5F5', bg='#7A7A7A', command=run, height=1, width=15, relief=GROOVE,
                          #bd=2, activebackground='#F5F5F5', activeforeground='#535353')
    #button_start.place(relx=0.45, rely=0.5, anchor=CENTER)

    run()
    top.protocol('WM_DELETE_WINDOW', on_closing)
    top.mainloop()
def listBoxMouseClick(event):
   if len(videos) > 0:
       for i in range(listBox.size()):

        selectVar.set('共获取到：%d个视频,已选中%d个' % (len(videos),len(listBox.curselection())))
        tip = tk.Label(myWindow, text=selectVar.get(), font=('Arial', 12), bg='green', fg="white")
        tip.place(x=200, y=460)
def initUI():

    '''
                 初始化事件
    '''

    global phasesSelect, subjectsSelect, editionsSelect, gradesSelect, listBox
    wed = tk.Label(myWindow, text='周数：', font=('Arial', 12))
    wedMap = {
        '第一周3.2-3.6': "0",
        '第二周3.9-3.13': "1",
        '第三周3.16-3.20': "2",
        '第四周3.23-3.27': "3",
        '第五周3.30-4.3': "4"
    }
    recousePath = os.path.join(os.path.abspath('./'), "rescouse")
    files = os.listdir(recousePath)
    fileNum = len(files)

    while fileNum > 6:
        key = '第%d周' % (fileNum - 1)
        val = ('%d' % (fileNum-2))
        wedMap[key]  = val
        fileNum -= 1

    wed.place(x=200, y=20)
    wedSelect = ttk.Combobox(myWindow)
    wedSelect.pack()
    wedSelect.bind("<<ComboboxSelected>>", lambda event: wedFunc(wedSelect,wedMap))  # #给下拉菜单绑定事件

    wedSelect['value'] = list(wedMap.keys())
    wedSelect.place(x=260, y=20)
    wedSelect.current(len(wedSelect['value'] )-1)


    '''
               初始化年级阶段
    '''
    global phasesSelect,subjectsSelect,editionsSelect,gradesSelect,listBox
    phases = tk.Label(myWindow, text='学段：', font=('Arial', 12))
    phases.place(x=200, y=60)
    phasesSelect = ttk.Combobox(myWindow)
    phasesSelect.pack()
    phasesSelect.bind("<<ComboboxSelected>>", lambda event: phasesFunc(phasesSelect))  # #给下拉菜单绑定事件
    phasesBox()
    '''
           初始化年级
    '''
    grades = tk.Label(myWindow, text='年级：', font=('Arial', 12))
    grades.place(x=200, y=100)
    gradesSelect = ttk.Combobox(myWindow)
    gradesSelect.pack()
    gradesSelect.bind("<<ComboboxSelected>>", lambda event: gradesFunc(gradesSelect))  # #给下拉菜单绑定事件
    gradesBox()

    subjects = tk.Label(myWindow, text='学科：', font=('Arial', 12))
    subjects.place(x=200, y=140)
    subjectsSelect = ttk.Combobox(myWindow)
    subjectsSelect.pack()
    subjectsSelect.bind("<<ComboboxSelected>>", lambda event: subjectsFunc(subjectsSelect))
    subjectBox()

    editions = tk.Label(myWindow, text='出版社：', font=('Arial', 12))
    editions.place(x=200, y=180)
    editionsSelect = ttk.Combobox(myWindow)
    editionsSelect.pack()


    editionBox()

    button = tk.Button(myWindow, text ="获取视频", font=('Arial', 12),command = load,bg="white")
    button.place(x=270,y=220)

    listBox = tk.Listbox(myWindow, selectmode=tk.MULTIPLE,width=80)
    listBox.place(x=20,y=260)
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
    siveButton = tk.Button(myWindow, text ="下载视频",width=20, font=('Arial', 15),command = downLoadVideo,bg="white")
    siveButton.place(x=190,y=520)

    auther = tk.Label(myWindow, text='@Raven版权所有（2020）', font=('华文行楷', 12),bg='blue',fg="white")
    auther.place(x=220, y=570)

def phasesBox():



    global pha
    pha = {}
    for ph in contect['GLOBAL_PHASES']:
        pha[ph['name']] =ph['code']
    phasesSelect['value'] = list(pha.keys())

    phasesSelect.place(x = 260,y = 60)
    phasesSelect.current(0)


def gradesBox():


    global  grad

    grad = {}
    grad['全部'] = '00'
    for gr in contect['GLOBAL_GRADES'].keys():
        #print(contect['GLOBAL_GRADES'][gr]['phaseCode'])
        # 如果是小学的年级 03 则添加进去
        if contect['GLOBAL_GRADES'][gr]['phaseCode'] == pha[phasesSelect.get()] or pha[phasesSelect.get()] == '00':
            # 这里应该是年级代码 contect['GLOBAL_GRADES'][gr]['code']，而不能是contect['GLOBAL_GRADES'][gr]['phaseCode']
            grad[contect['GLOBAL_GRADES'][gr]['name']] = contect['GLOBAL_GRADES'][gr]['code']
            #grad['childrenCodes'] = contect['GLOBAL_GRADES'][gr]['childrenCodes']

    gradList = list(grad.keys())
    gradesSelect['value'] = gradList
    gradesSelect.place(x = 260,y = 100)
    gradesSelect.current(0)

def subjectBox():
    '''
           初始化科目
    '''
    global subj



    subj = {}
    subj['全部'] = '00'
    show_subj_code=[]
    # 如果不是全部年级的话，筛选出该年级的科目
    if grad[gradesSelect.get()] != '00':
        # 找出该年级有的所有科目
        for gradChid in contect['GLOBAL_GRADES']:
            #print(contect['GLOBAL_GRADES'][gradChid]['name'] )
            if contect['GLOBAL_GRADES'][gradChid]['name']  == gradesSelect.get():
                for g in contect['GLOBAL_GRADES'][gradChid]['childrenCodes']:
                    show_subj_code.append(g['subjectCode'])
        print("科目编号："+str(show_subj_code))
    for su in contect['GLOBAL_SUBJECTS'].keys():
        # 如果科目包括在这个年级里
        if contect['GLOBAL_SUBJECTS'][su]['code'] in show_subj_code or grad[gradesSelect.get()]=='00':
            subj[contect['GLOBAL_SUBJECTS'][su]['name']] = contect['GLOBAL_SUBJECTS'][su]['code']

    subjList = list(subj.keys())
    subjectsSelect['value'] = subjList
    subjectsSelect.place(x = 260,y = 140)
    subjectsSelect.current(0)

def editionBox():
    '''
           初始化出版社
    '''

    global edit
    edit = {}
    edit['全部'] = '00'
    show_edit_code = []
    print("年级代码" + grad[gradesSelect.get()])
    print("学科代码" + subj[subjectsSelect.get()])
    # 如果不是全部科目的话，筛选出该科目的所有出版社
    if subj[subjectsSelect.get()] !='00' :
        # 找出该学科有的所有出版社
        for gradChid in contect['GLOBAL_SUBJECTS']:
            #print(contect['GLOBAL_SUBJECTS'][gradChid])

            if contect['GLOBAL_SUBJECTS'][gradChid]['code'] == subj[subjectsSelect.get()]:
                    print(contect['GLOBAL_SUBJECTS'][gradChid])
                    show_edit_code = contect['GLOBAL_SUBJECTS'][gradChid]['childrenCodes']
        print("出版社" + str(show_edit_code))
    #print(grad)

    for ed in contect['GLOBAL_EDITIONS'].keys():
        if contect['GLOBAL_EDITIONS'][ed]['code'] in show_edit_code or subj[subjectsSelect.get()] == '00':
            edit[contect['GLOBAL_EDITIONS'][ed]['name']] = contect['GLOBAL_EDITIONS'][ed]['code']

    editList = list(edit.keys())
    editionsSelect['value'] = editList
    editionsSelect.place(x = 260,y = 180)
    editionsSelect.current(0)

def updateData():
    global videoRescous
    url = 'http://jiaoxue.ahedu.cn/static_zxjx2020/js/json%d.js?version=20200331'
    recousePath = os.path.join(os.path.abspath('./'), "rescouse")
    files= os.listdir(recousePath)
    filesNum = len(files)
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.13 Safari/537.36",
        "Referer": "http://jiaoxue.ahedu.cn/index.html"
    }
    while TRUE:
        r = requests.get((url % filesNum), headers=header, stream=True, verify=False)
        json_str = r.content.decode()
        json_str= json_str.split("=", 1)[1]
        json_str = json.loads(json_str)
        if len(json_str) == 0:
            break
        newJSON={
            "content":json_str
        }
        # 字典转字符串
        #newJSON = json.dumps(newJSON)
        # 字符串 转 字典
        #newJSON = json.loads(newJSON)

        with open(recousePath+("\\video%d.json" % filesNum), 'w',encoding = 'utf-8') as f:
            json.dump(newJSON,f,ensure_ascii=False,indent=4)
        filesNum += 1
    videoRescous = readFile("video%d.json" % (filesNum-1))

def readFile(fileName):
    print(os.path.abspath('./')+'\\rescouse\\'+fileName)
    fileName = os.path.abspath('./')+'\\rescouse\\'+fileName
    with open(fileName,'r',encoding='utf-8',errors='ignore') as f:
        fstr = f.read()
        jstr = json.loads(fstr)
        #print(jstr)
    return jstr

done = 0
closeWindow = FALSE

videos = []
top = Tk()

top.withdraw()
# 初始化Tk()
myWindow = tk.Tk()
videoRescous = {}
contect = readFile("contect.json")
updateData()
initWindow()
initUI()

myWindow.protocol('WM_DELETE_WINDOW', on_closing2)
# 进入消息循环
myWindow.mainloop()
# pyinstaller -F -w -i i.ico main.py -p D:\pyCode\video\venv\Lib\site-packages