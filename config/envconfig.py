import os
from posixpath import pathsep
import sys
import threading
import re


class Config():
    """ 
        一个全局的单例配置类，提供全局的配置的信息
    """
    __instanceLock = threading.Lock()

    def __init__(self):
        pass

    def __new__(cls):
        """
        创建一个全局配置的单例类
        """
        if not hasattr(cls, '__instance'):
            with Config.__instanceLock:
                if not hasattr(cls, '__instance'):
                    Config.__instance = super().__new__(cls)

                    # 获取系统相关资源
                    Config.__systemType = sys.platform
                    Config.__workdir = os.getcwd()
                    Config.__resultdir = os.getcwd()
                    Config.__resultname = ""
                    Config.__pathsep = "/"

                    Config.pathSep(Config.__instance)
            return Config.__instance

    def getSystemType(self):
        """
            操作系统的平台
        """
        return str(self.__systemType)

    def getWorkDir(self):
        """ 
            获取运行的工作目录
        """
        return self.__workdir

    def getPlatsignal(self):
        return self.__plat

    def pathSep(self):
        """
            确定路径是linux的'/'路径分隔符还是windows的'\'路径分隔符
        """
        if self.getSystemType() == 'linux':
            self.__pathsep = '/'
            self.__plat = 0
        elif self.getSystemType() == 'win32':
            self.__pathsep = '\\'
            self.__plat = 1
        else:
            self.__plat = 2

    def getResultDir(self):
        """ 
            获取存取存放结果的目录位置
        """
        result = self.__resultdir
        return result

    def getResultFile(self):
        return self.__resultname

    def setResultDir(self, dirname):
        """
            返回存放结果集的目录
        """
        self.__resultdir = dirname

    def loadtempfile(self, args):
        ''' 
            重新指定结果集的目录和文件名
        '''
        self.__resultdir = args.savedir
        self.__resultname = args.savefile

    def getpathsep(self):
        ''' 返回操作系统的类型:
            0 -> Linux
            1 -> Windows32
            2 -> unknown
        '''
        return self.__pathsep
