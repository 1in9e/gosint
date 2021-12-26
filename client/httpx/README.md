## httpx组件

该组件调用了httpx



#### 传入参数格式

传入待扫描的list，如

```
run(['auth.vivo.com', 'www.vivo.com'])
```


#### 返回参数格式

返回字典

tool字段内容为该组件名字

result字段内容为list，每个list是一个字典包含url，content-length，status-code，title，cdn5个值

```
{'tool': 'httpx', 'result': [{'url': 'https://www.vivo.com', 'content-length': 171129, 'status-code': 200, 'title': 'vivo智能手机官方网站-X50系列丨专业影像旗舰', 'cdn': False}, {'url': 'https://auth.vivo.com', 'content-length': 507, 'status-code': 500, 'title': 'Error', 'cdn': False}]}
```

