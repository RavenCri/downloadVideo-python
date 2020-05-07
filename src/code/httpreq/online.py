import requests
from fileUtil.fileUtil import *

videoRescous = {}
def updateData():
    '''
      用来获取更新
    '''
    url = 'http://jiaoxue.ahedu.cn/static_zxjx2020/js/json%d.js?version=20200331'
    recousePath = os.path.join(os.path.abspath('../'), "rescouse")
    files= os.listdir(recousePath)
    filesNum = len(files)
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.13 Safari/537.36",
        "Referer": "http://jiaoxue.ahedu.cn/index.html"
    }
    while True:
        r = requests.get((url % filesNum), headers=header, stream=True, verify=False)
        json_str = r.content.decode()
        if json_str.find("404 Not Found") > 0:
            break
        json_str= json_str.split("=", 1)[1]

        json_str = json.loads(json_str)
        if len(json_str) == 0:
            break
        newJSON={
            str(filesNum):json_str
        }
        # 字典转字符串
        #newJSON = json.dumps(newJSON)
        # 字符串 转 字典
        #newJSON = json.loads(newJSON)

        with open(recousePath+("\\video%d.json" % filesNum), 'w',encoding = 'utf-8') as f:
            json.dump(newJSON,f,ensure_ascii=False,indent=4)
        filesNum += 1
    videoRescous = readFile("video%d.json" % (filesNum-1))
    return videoRescous

