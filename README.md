# submainrun第一版
## 说明
  本软件主要用于渗透测试的子域名把爆破使用，仅供学习参考!

## TIPS
在windows上存在无法中途中断程序的BUG。下一版更新修订

## 环境说明

编译环境: python3(不支持python2)

编译环境:windows/Linux

需要导入的模块已经在env.txt

下载依赖包

```python
pip3 install -r env.txt
```

## 参数使用

|      参数      | 说明                                                         |
| :------------: | ------------------------------------------------------------ |
|  -d(--domain)  | 目标域名(此选项不能忽略)                                     |
|  -s(--speed)   | 分为三个等级的线程数:low(5)、mid(15)、high(25)               |
| -S(--savedir)  | 遍历结果的保存目录                                           |
| -c(--savefile) | 遍历结果的保存文件名                                         |
| -x(dnlistname) | 推荐不开启此参数(默认使用/dict/dnsnameserver.txt的知名域名!)，此参数开启时，仅仅使用物理机上的DNS解析。<font color="red">若想开启此参数，-x后面需要接`no`</font> |
|      -l1       | 二级域名列表(默认./dict/domainlist)                          |
|       l2       | 三级域名列表(暂时无法使用)                                   |
|       -t       | 具体使用的线程数(提供比-s更精确的控制),使用-t时覆盖-s作用域  |
|       -q       | 不打印日志                                                   |

