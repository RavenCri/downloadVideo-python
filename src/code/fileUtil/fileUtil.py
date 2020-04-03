import os
import json
def readFile(fileName):
    print("已加载资源文件："+os.path.join(os.path.abspath('../'), "rescouse",fileName) )
    fileName = os.path.join(os.path.abspath('../'), "rescouse",fileName)
    with open(fileName,'r',encoding='utf-8',errors='ignore') as f:
        fstr = f.read()
        jstr = json.loads(fstr)
        #print(jstr)
    return jstr


import tkinter


from tkinter import ttk, messagebox
import tkinter
def click():
    select = tkinter.StringVar()
    select.set("dd")
    label = tkinter.Label(l, textvariable=select, font=('Arial', 12), bg='green', fg="white")
    label.place(x=100, y=100)

    window = tkinter.Tk()
    window.title('new window')
    # 为什么 label取不到数据
    label2 = tkinter.Label(window, textvariable=select, font=('Arial', 12), bg='green', fg="white")
    label2.place(x=100, y=100)
    window.mainloop()
if __name__ == '__main__':
    l = tkinter.Tk()
    bt = tkinter.Button(l, text ="下载视频", font=('Arial', 15),command = click)
    bt.place(x=50,y=50)
    l.mainloop()
