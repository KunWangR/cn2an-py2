# cn2an-py2: Chinese Numerals To Arabic Numerals for python 2.7

📦 **`cn2an`** 是一个快速转化 `中文数字` 和 `阿拉伯数字` 的工具包！

🔗[点击访问  cn2an](https://github.com/Ailln/cn2an)

> 🎈 `v0.5.14 update`: fix [#42](https://github.com/Ailln/cn2an/issues/42)


## 1 安装

> ⚠️ 注意：
> 1. 本地安装仅支持 Python 的 2.7 版本，其他版本未做验证；
> 2. py3版本请查看[cn2an](https://github.com/Ailln/cn2an)，尽可能使用 `cn2an` 的最新版本；
> 3. 其他语言用户可以考虑使用 [HTTP API](https://www.dovolopor.com/api/cn2an) 。

### 1.1 从代码库安装

```shell
git clone git@github.com:KunWangR/cn2an-py2.git
cd cn2an
pip install -r requirement.txt
python setup.py install
```

### 1.2 常见问题

regex包安装，特别需要注意在Linux系统下安装，需要先执行如下操作。
```
yum install python-devel
yum install python2-regex
```

## 3 使用

```python
# 在文件首部引入包
import cn2an

# 查看当前版本号
print(cn2an.__version__)
# 0.5.14
```

### 3.1 `中文数字` => `阿拉伯数字`

> 最大支持到 `10**16`，即 `千万亿`，最小支持到 `10**-16`。

```python
import cn2an

# 在 strict 模式（默认）下，只有严格符合数字拼写的才可以进行转化
output = cn2an.cn2an(u"一百二十三")
# 或者
output = cn2an.cn2an(u"一百二十三", u"strict")
# output:
# 123

# 在 normal 模式下，可以将 一二三 进行转化
output = cn2an.cn2an(u"一二三", u"normal")
# output:
# 123

# 在 smart 模式下，可以将混合拼写的 1百23 进行转化
output = cn2an.cn2an(u"1百23", u"smart")
# output:
# 123

# 以上三种模式均支持负数
output = cn2an.cn2an(u"负一百二十三", u"strict")
# output:
# -123

# 以上三种模式均支持小数
output = cn2an.cn2an(u"一点二三", u"strict")
# output:
# 1.23
```

### 3.2 `阿拉伯数字` => `中文数字`

> 最大支持到`10**16`，即`千万亿`，最小支持到 `10**-16`。

```python
import cn2an

# 在 low 模式（默认）下，数字转化为小写的中文数字
output = cn2an.an2cn(u"123")
# 或者
output = cn2an.an2cn("123", u"low")
# output:
# 一百二十三

# 在 up 模式下，数字转化为大写的中文数字
output = cn2an.an2cn(u"123", u"up")
# output:
# 壹佰贰拾叁

# 在 rmb 模式下，数字转化为人民币专用的描述
output = cn2an.an2cn(u"123", u"rmb")
# output:
# 壹佰贰拾叁元整

# 以上三种模式均支持负数
output = cn2an.an2cn(u"-123", u"low")
# output:
# 负一百二十三

# 以上三种模式均支持小数
output = cn2an.an2cn(u"1.23", u"low")
# output:
# 一点二三
```

### 3.3 句子转化

> ⚠️：试验性功能，可能会造成不符合期望的转化。

```python
import cn2an

# 在 cn2an 方法（默认）下，可以将句子中的中文数字转成阿拉伯数字
output = cn2an.transform(u"小王捡了一百块钱")
# 或者
output = cn2an.transform(u"小王捡了一百块钱", u"cn2an")
# output:
# u'\u5c0f\u738b\u6361\u4e86100\u5757\u94b1'
# 小王捡了100块钱

# 在 an2cn 方法下，可以将句子中的中文数字转成阿拉伯数字
output = cn2an.transform(u"小王捡了100块钱", u"an2cn")
# output:
# u'\u5c0f\u738b\u6361\u4e86100\u5757\u94b1'
# 小王捡了一百块钱


## 支持日期
output = cn2an.transform(u"小王的生日是二零零一年三月四日", "cn2an")
# output:
# u'\u5c0f\u738b\u7684\u751f\u65e5\u662f2001\u5e743\u67084\u65e5'
# 小王的生日是2001年3月4日

output = cn2an.transform(u"小王的生日是2001年3月4日", "an2cn")
# output:
# u'\u5c0f\u738b\u7684\u751f\u65e5\u662f\u4e8c\u96f6\u96f6\u4e00\u5e74\u4e09\u6708\u56db\u65e5'
# 小王的生日是二零零一年三月四日

## 支持分数
output = cn2an.transform(u"抛出去的硬币为正面的概率是二分之一", "cn2an")
# output:
# 
# 抛出去的硬币为正面的概率是1/2

output = cn2an.transform(u"抛出去的硬币为正面的概率是1/2", "an2cn")
# output:
# u'\u629b\u51fa\u53bb\u7684\u786c\u5e01\u4e3a\u6b63\u9762\u7684\u6982\u7387\u662f\u4e8c\u5206\u4e4b\u4e00'
# 抛出去的硬币为正面的概率是二分之一
```
