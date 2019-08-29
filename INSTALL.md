安装说明
-------

获取项目源码 :

    # clone the repository
    $ git clone https://github.com/4keyboardman/StandpointExtract.git
    $ cd StandpointExtract

创建虚拟环境并激活:

linux系统运行

    $ python3 -m venv flaskr
    $ . venv/bin/activate

Windows系统运行cmd

    $ py -3 -m venv venv
    $ venv\Scripts\activate.bat

安装项目:

    $ pip install -e .


下载模型文件https://pan.baidu.com/s/1hE-p3YTMnxJebzthDNPJbw放在项目根目录下

解压文件:
    $ unzip instance.zip


运行
---

linux系统运行:

    $ export FLASK_APP=flaskr
    $ export FLASK_ENV=development
    $ flask run

Windows系统运行cmd:

    > set FLASK_APP=flaskr
    > set FLASK_ENV=development
    > flask run

打开浏览器访问 http://127.0.0.1:5000

