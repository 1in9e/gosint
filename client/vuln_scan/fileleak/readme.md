## fileleak组件
> 多功能获取网站path fuzz结果
- 调用fileleak对top1000/top8000路径字典进行fuzz


#### 传入参数格式

传入待扫描的target,单个目标且为str类型，如

```
run('https://www.ohlinge.cn')
```



#### 返回参数格式

返回字典

tool字段内容为该组件名字

result字段内容为list，每个list是一个字典包含host，path，content-length,status-code, title  5个值

```
{'tool': 'fileleak', 'result': [{'host': 'https://www.ohlinge.cn', 'path': '/index.php', 'content-length': '44121', 'status-code': '200', 'title': "0h1in9e' s Blog | 林歌博, {'host': 'https://www.ohlinge.cn', 'path': '/robots.txt', 'content-length': '41', 'status-code': '200', 'title': ''}]}
```

