readme
# xray_subdomain
> 使用xray高级版子域名发现功能

## command
```
./xray subdomain --target ohlinge.cn --text-output ohlinge.cn.txt
```
## output
```
jump.qt.qq.com,
update2.cc.cdn.qq.com,
mail.qq.com,14.18.245.237
e.t.qq.com,0.0.0.1
qzone.qq.com,119.167.134.109
report.b.qq.com,183.3.226.70
m.qq.com,101.91.69.89
...
```
### 处理后的格式，输出为仅域名

## 注意事项
- 配置中关闭了brute
- 配置中确定了结果只显示解析到IP的结果
```

```