import argparse
from typing import ChainMap
from config.envconfig import Config
import threading
import os
import csv
from lib.libdns import *
import sys
countlock = threading.Lock()
runcount = 0
localdomain = ""
findcount = 0


class Arg():
    """
    @author 张泽伟
    @desc 本模块提供解析命令行参数的类
    """

    def __init__(self, desc="Submain"):
        self.__arg = argparse.ArgumentParser(description=desc)
        self.getArgsList()
        self.__argslist = self.__arg.parse_args()

    def getArgsList(self):
        """
            解析参数列表
        """
        self.__arg.add_argument(
            "-d", "--domain", metavar="domain", help="目标域名(必填)")
        self.__arg.add_argument("-f", "--domainfile", metavar="file",
                                help="从指定的文件读取目标域名(默认工作目录下的dict/domainlist, 每个域名一行)")
        self.__arg.add_argument("-s", "--speed", metavar="speed",
                                help="速度选项:[low, hig, mid]", default="low")
        self.__arg.add_argument(
            "-S", "--savedir", metavar="save dir", help="保存的路径(默认result)", default="Y")
        self.__arg.add_argument(
            "-c", "--savefile", metavar="save file", help="保存的文件(默认域名名称)", default="Y")
        self.__arg.add_argument("-x", "--dnslistname", metavar="dnslist",
                                help="使用系统默认的DNS解析(不使用从dict/nameserver.txt读取DNS服务器)", default="Y")
        self.__arg.add_argument("-l1", "--domainlist", metavar="domainlist",
                                help="二级域名列表(默认./dict/domainlist)", default="./dict/domainlist")
        self.__arg.add_argument("-l2", "--subdomainlist", metavar="subdomainlist",
                                help="三级域名列表(暂时无法使用)", default="./dict/submainlist")
        self.__arg.add_argument(
            '-q', "--quite", metavar="not print log", help="不打印日志", default="N")
        self.__arg.add_argument('-t', "--thread", metavar="Number of threads",
                                help="线程数(提供比-s更精确的控制),使用-t时覆盖-s作用域", type=int, default=0)

    def returnArgsList(self):
        return self.__argslist

    def help(self):
        self.__arg.print_help()


class LoadController():
    """ 
        用于控制整个环境的类，包括管理config与Arg类中的关系
    """

    def __init__(self, config, args):
        self.config = config
        self.args = args
        self.cmd = ""

    def createResultDir(self, name):
        """ 
            创建结果集的目录
        """
        if re.search('\/', name):
            print("OPTION -S:only one level directory is supported")
            sys.exit(0)
        if not os.path.exists(name):
            print("It Can't find result dir")
            print("Create \"" + name + "\" dir")
            os.mkdir(name)

    def createResultFile(self, dir, name, sep):
        """ 
            创建结果集的文件
        """
        filepath = dir + sep + name + ".csv"
        if not os.access(filepath, os.F_OK):
            with open(filepath, 'a+') as fp:
                pass

    def checkResultDir(self):
        """
            检查目录文件等环境是否正常，并且创建保存的结果目录
            最后设置一个resultfile全路径变量
        """
        self.config.setResultDir(self.args.savedir)
        print(self.config.getResultDir())
        self.createResultDir(self.config.getResultDir())
        self.createResultFile(self.config.getResultDir(
        ), self.config.getResultFile(), self.config.getpathsep())
        self.args.resultfile = self.config.getResultDir() + self.config.getpathsep() + \
            self.config.getResultFile()
        if self.config.getpathsep() != 1:
            self.cmd = "cls"
        else:
            self.cmd = "clear"

    def getResultFile(self):
        try:
            return self.args.resultfile
        except:
            print("please use after checkResultDir()!")
            sys.exit(0)

    def run(self):
        dnslist = []
        if self.args.dnslistname != "N":
            with open(self.args.dnslistname, "r", encoding="utf-8") as fp:
                for line in fp.readlines():
                    dnslist.append(line.strip('\n'))

        dnsimp = DnsImp(self.args.domain, self.args.domainlist,
                        self.args.subdomainlist, dnslist)

        list1 = []
        for i in range(0, self.args.speed):
            list1.append(threading.Thread(target=requestThread,
                         args=(dnsimp, self.args.speed, self.cmd, self.args.quite)))
        for i in list1:
            i.start()
            i.join()
        dnsimp.FindDict()
        sys.stdout.flush()
        print("this is " + str(dnsimp.couterror()) + " Parsing error We find")
        return dnsimp.getFindDict(), dnsimp.logresult()


def requestThread(dnsimp, speed, cmd, flag):
    ''' 
        线程奔跑：需要带入dnsimp类对象
    '''
    while not dnsimp.domainqueues.empty():
        temp = dnsimp.domainqueues.get()
        dnsimp.sendRequest(temp, speed, cmd, flag)


def save_csv(fd, msg_dict):
    csv_write = csv.writer(fd)
    csv_write.writerow(["DOMAIN", "IP"])
    for key, value in msg_dict.items():
        csv_write.writerow([key, value])


if __name__ == '__main__':
    config = Config()
    args = Arg()
    argslist = args.returnArgsList()
    if not argslist.domain:
        sys.stdout.flush()
        args.help()
        exit(0)
    if argslist.savedir == "Y":
        argslist.savedir = "result"
    if argslist.savefile == "Y":
        argslist.savefile = argslist.domain
    if argslist.dnslistname == "Y":
        argslist.dnslistname = "dict/nameserver.txt"
    else:
        argslist.dnslistname = "N"
    if argslist.quite.lower() == 'y':
        argslist.quite = True
    else:
        argslist.quite = False
    if argslist.thread != 0:
        argslist.speed = int(argslist.thread)
    else:
        if argslist.speed == "low":
            argslist.speed = 5
        elif argslist.speed == "mid":
            argslist.speed = 15
        elif argslist.speed == "high":
            argslist.speed = 25
        else:
            print("option -s ,error argment")
            exit(0)

    config.loadtempfile(argslist)
    controller = LoadController(config, argslist)
    controller.checkResultDir()
    print(config.getResultDir() + config.getpathsep() + "log")
    result, log = controller.run()
    with open(controller.getResultFile() + ".csv", "w+", encoding="utf-8")as fp:
        save_csv(fp, result)

    with open(config.getResultDir() + config.getpathsep() + "log", "w+", encoding="utf-8") as fp:
        fp.write(log)
