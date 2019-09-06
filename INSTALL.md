安装说明
-------

获取项目源码 :

    # clone the repository
    $ git clone https://github.com/4keyboardman/StandpointExtract.git
    $ cd StandpointExtract

创建虚拟环境并激活:

linux系统运行

    $ python3 -m venv venv
    $ . venv/bin/activate

Windows系统运行cmd

    $ py -3 -m venv venv
    $ venv\Scripts\activate.bat

安装项目:

    $ pip install -e .

pyhanlp需要下载数据包，详情参考：https://github.com/hankcs/pyhanlp/wiki/%E6%89%8B%E5%8A%A8%E9%85%8D%E7%BD%AE

下载模型文件放在项目根目录下：https://pan.baidu.com/s/1hE-p3YTMnxJebzthDNPJbw

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

使用gunicorn启动：
    $ gunicorn -D -w 1 -b 0.0.0.0:8871 "flaskr:create_app()"

api命令
---
    GET /cmd/model/reload: 重新加载instance中的模型文件
    GET /cmd/extractor: 查询当前使用的判断句子结束的模型类型
    GET /cmd/extractor/{type}: 设置判断句子结束的方法，type类型: 
        sif-句子相似度
        rnn-是否是人说的话
        mix-两者综合，默认类型
