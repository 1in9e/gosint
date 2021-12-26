## naabu组件

该组件调用了naabu和nmap



#### 传入参数格式

传入待扫描的target，可以是ip，也可以是域名，但只能传单个str类型，如

```
run('')
```



#### 返回参数格式

返回字典

tool字段内容为该组件名字

result字段内容为list，每个list是一个字典包含host，ip，port，server，4个值

