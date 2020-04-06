# downloadVideo-python
用来爬取安徽基础教育资源页面的视频
＃使用步骤
## 先克隆项目到本地
git clone https://github.com/clothesack/downloadVideo-python
## 进入主目录
cd downloadVideo-python/src/code
## 启动主程序
python main.py
#说明
然后设置相应的参数进行下载视频，您也可以使用如下命令自主打包成exe二进制可执行文件。
pyinstaller -F -w -i i.ico main.py -p D:\pyCode\video\venv\Lib\site-packages
