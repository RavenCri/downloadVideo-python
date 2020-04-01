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



