## nuclei组件

该组件调用了nuclei，会先用git pull更新templates（nuclei -update-templates实际更新不了），然后进行nuclei内置全poc扫描


#### 传入参数格式

传入待扫描的list，如

```
run(['https://www.ohlinge.cn'])
```



#### 返回参数格式

返回字典

tool字段内容为该组件名字

result字段内容为list，每个list是一个字典包含url，level，poc_name，detect，vuln_path 5个值

其中url, level 为都有的字段

如果poc是detect即指纹的poc的话，会返回detect字段

如果poc没有detect字符串，则说明是其他类型的poc，会返回poc_name和vuln_path字段


```
{'tool': 'nuclei', 'result': ['{"severity":"info","matcher_name":"apachegeneric","matched":"https://www.ohlinge.cn/","template":"waf-detect","type":"http","host":"https://www.ohlinge.cn","name":"WAF Detection","author":"dwisiswant0"}\n', '{"template":"apache-version-detect","description":"Some Apache servers have the version on the response header. The OpenSSL version can be also obtained","severity":"info","extracted_results":["Apache/2.4.6 (CentOS) OpenSSL/1.0.2k-fips PHP/5.4.16"],"matched":"https://www.ohlinge.cn","type":"http","host":"https://www.ohlinge.cn","name":"Apache Version","author":"philippedelteil"}\n', '{"name":"Strict Tranposrt Security Not Enforced","author":"Dawid Czarnecki","severity":"info","description":"Checks if the HSTS is enabled by looking for Strict Transport Security response header.","matched":"https://www.ohlinge.cn","template":"missing-hsts","type":"http","host":"https://www.ohlinge.cn"}\n', '{"template":"missing-csp","type":"http","host":"https://www.ohlinge.cn","name":"CSP Not Enforced","author":"geeknik","severity":"info","description":"Checks if there is a CSP header","matched":"https://www.ohlinge.cn"}\n', '{"host":"https://www.ohlinge.cn","name":"Clickjacking (Missing XFO header)","author":"kurohost","severity":"low","matched":"https://www.ohlinge.cn","template":"missing-x-frame-options","type":"http"}\n']}
```

