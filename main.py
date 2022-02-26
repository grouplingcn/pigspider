__author__ = 'GroupLing'
__date__ = '2021/6/3 12:51'

from scrapy.cmdline import execute

import sys
import os

# 将系统当前目录设置为项目根目录
# os.path.abspath(__file__)为当前文件所在绝对路径
# os.path.dirname为文件所在目录
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# 执行命令，相当于在控制台cmd输入改名了  execute不支持连续执行
# execute(["scrapy", "crawl", "lianjia"])
# execute('scrapy crawl lianjia -a city=gy'.split())
# execute('scrapy crawl lianjia -a city=sz'.split())
# execute('scrapy crawl lianjia -a city=bj'.split())
# execute('scrapy crawl lianjia -a city=sh'.split())
# execute('scrapy crawl lianjia -a city=gz'.split())

os.system("scrapy crawl lianjia -a city=gy")
os.system("scrapy crawl lianjia -a city=sz")
os.system("scrapy crawl lianjia -a city=bj")
os.system("scrapy crawl lianjia -a city=sh")
os.system("scrapy crawl lianjia -a city=gz")

