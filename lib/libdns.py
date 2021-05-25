import queue
import dns.resolver
import re
import os
import threading
import sys
import time
countlock = threading.Lock()
runcount = 0
localdomain = ""
findcount = 0
logLock = threading.Lock()


class DnsImp():
    """
        一个DNS解析的实现类(实现层)
    """

    def __init__(self, domain, domainlist, subdomainlist, dnslist):
        self.domain = domain
        self.domainlist = domainlist
        self.submainlist = subdomainlist
        self.domainqueues = self.loadDomain(self.domainlist)
        self.subdomainqueues = self.loadDomain(self.submainlist)
        self.result = queue.Queue()
        self.error = 0
        self.resolver = dns.resolver.Resolver()
        if dnslist != []:
            self.resolver.nameservers = dnslist
        self.finddict = {}
        self.log = ""

    def loadDomain(self, name):
        ''' 从指定字典加载子域名 '''
        q = queue.Queue()
        with open(name, 'r') as fp:
            for line in fp.readlines():
                q.put(line.strip('\n'))
        return q

    def sendRequest(self, name, speed, printcmd, quiet=False,):
        global localdomain
        global findcount
        global runcount
        countlock.acquire()
        runcount = runcount + 1
        countlock.release()
        domain = name + "." + self.domain
        localdomain = domain
        os.system(printcmd)
        print(self.log + "request the dns count: {:^5} |domain：{:^10}|speed {:^4} Thread |find count: {find}".format(
            runcount, localdomain, speed,  find=findcount))
        try:
            answer = self.resolver.resolve(domain, lifetime=2)
            self.result.put(answer)
            findcount = findcount + 1

        except dns.resolver.NXDOMAIN:
            if not quiet:
                print(domain + "[.] Resolved but no entry for ")
        except dns.resolver.NoNameservers:
            if not quiet:
                print(domain + "[-] Answer refused for ")
        except dns.resolver.NoAnswer:
            if not quiet:
                print(domain + "[-] No answer section for ")
        except dns.exception.Timeout:
            if not quiet:
                self.log = self.log + domain + "[-] Timeout\n"

    def FindDict(self):
        ''' 
            对result结果集进行抽取{域名}->{IP}键值对
        '''
        while not self.result.empty():
            temp = []
            items = str(self.result.get().response.answer[0]).split("\n")
            # print(items)
            for item in items:
                re_result = re.search(r"(.*)\. .* IN CNAME (.*)", str(item))
                if not re_result:
                    re_result = re.search(r"(.*)\. .* IN A (.*)", str(item))
                if not re_result:
                    self.error = self.error + 1
                    continue
                re_result = re_result.groups()
                temp.append(re_result[1])
                self.finddict[re_result[0]] = temp

    def getFindDict(self):
        ''' 
            在FindDict()之后使用，返回结果字典
        '''
        return self.finddict

    def couterror(self):
        return self.error

    def logresult(self):
        ''' 
            返回日志记录
        '''
        return self.log
