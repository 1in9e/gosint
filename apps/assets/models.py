from django.db import models
from apps.scans.models import Scans
from apps.targetApp.models import Target
from import_export import resources


# Create your models here.
class SubDomain(models.Model):
    scan_task = models.ForeignKey(Scans, verbose_name='扫描任务', on_delete=models.CASCADE, null=True, blank=True)
    subdomain = models.CharField(max_length=200, verbose_name='子域名', unique=True)
    domain_type = models.CharField(max_length=200, verbose_name='域名解析方式', blank=True, null=True)
    record = models.CharField(max_length=2000, verbose_name='解析记录', null=True, blank=True)
    domain_ips = models.CharField(max_length=2000, verbose_name='IP', null=True, blank=True)
    tools = models.CharField(max_length=100, verbose_name='来源', null=True, blank=False, default='手工导入')
    created = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    modified = models.DateTimeField(auto_now=True, verbose_name='修改时间')
    # target = models.ForeignKey(Target, verbose_name='目标资产', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.subdomain

    # def project_field(self):
    #     return self.target.project

    class Meta:
        verbose_name = '子域名'
        verbose_name_plural = verbose_name


class IP(models.Model):
    """
    ip地址信息
    """
    ip = models.GenericIPAddressField(db_index=True, verbose_name='ip地址')
    scan = models.ForeignKey(Scans, verbose_name='扫描任务', on_delete=models.CASCADE)
    subdomain = models.ForeignKey(SubDomain, on_delete=models.CASCADE, null=True, blank=True, verbose_name='域名')
    is_cdn = models.BooleanField(default=False, verbose_name='是否是CDN')
    tools = models.CharField(max_length=50, verbose_name='来源', null=True, blank=False, default='手工')
    created = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    modified = models.DateTimeField(auto_now=True, verbose_name='修改时间')

    def __str__(self):
        return self.ip

    class Meta:
        verbose_name = 'ip'
        verbose_name_plural = verbose_name

class IPC(models.Model):
    """
    ip c段情报信息
    """
    ipc = models.CharField(max_length=100, db_index=True, verbose_name='C段')
    # ipc_count = models.CharField(max_length=50, null=True, blank=True, verbose_name='目标C段主机数')
    ipc_count = models.SmallIntegerField(verbose_name='目标C段主机数', blank=True, null=True, default=1)
    scan = models.ForeignKey(Scans, verbose_name='扫描任务', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    modified = models.DateTimeField(auto_now=True, verbose_name='修改时间')

class Port(models.Model):
    """
    port information
    """
    ip = models.ForeignKey(IP, on_delete=models.CASCADE, verbose_name='IP', default='', blank=True, null=True)
    scan = models.ForeignKey(Scans, verbose_name='扫描任务', on_delete=models.CASCADE)
    port = models.CharField(max_length=50, verbose_name='端口号', null=True, blank=True)
    ip_port = models.CharField(max_length=100, verbose_name='IP2PORT', null=True, blank=True, unique=True)
    status = models.CharField(max_length=255, default='open', verbose_name='端口状态')
    service = models.CharField(max_length=255, verbose_name='端口服务')
    created = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    modified = models.DateTimeField(auto_now=True, verbose_name='修改时间')
    tools = models.CharField(max_length=50, verbose_name='工具来源', null=True, blank=False, default='naabu')
    # add by _lin9e in 2021-1-13

    # def ip_port_field(self):
    #     return "{}:{}".format(self.ip, self.port)

    def __str__(self):
        return self.port

    def subdomain_field(self):
        if self.ip:
            return self.ip.subdomain
        else:
            return ''

    class Meta:
        verbose_name = '端口'
        verbose_name_plural = verbose_name


class WebApp(models.Model):
    url = models.CharField(max_length=500, db_index=True, verbose_name='url地址')
    scan = models.ForeignKey(Scans, verbose_name='扫描任务', on_delete=models.CASCADE)
    banner = models.CharField(max_length=255, null=True, blank=True, verbose_name='banner信息')
    status_code = models.CharField(max_length=50, null=True, blank=True, verbose_name='状态码')
    title = models.TextField(blank=True, null=True, verbose_name='标题')
    headers = models.TextField(blank=True, null=True, verbose_name='headers')
    content_length = models.IntegerField(default=0, blank=True, null=True, verbose_name='内容长度')
    screenshot_path = models.CharField(max_length=1000, null=True, blank=True, verbose_name='截屏')
    webserver = models.CharField(max_length=1500, null=True, blank=True, verbose_name='指纹', default='')
    created = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    modified = models.DateTimeField(auto_now=True, verbose_name='修改时间')

    def __str__(self):
        return self.url

    class Meta:
        verbose_name = 'web应用'
        verbose_name_plural = verbose_name


class FileLeak(models.Model):
    # url = models.ForeignKey(WebApp, verbose_name='web应用', on_delete=models.CASCADE)
    url = models.TextField(verbose_name='leak_url', null=True, blank=True)
    scan = models.ForeignKey(Scans, verbose_name='扫描任务', on_delete=models.CASCADE)
    path = models.CharField(max_length=1000, verbose_name='泄露路径', null=True, blank=True)
    content_length = models.CharField(max_length=50, verbose_name='内容长度', default='', null=True, blank=True)
    status_code = models.CharField(max_length=50, verbose_name='状态码', default='0', null=True, blank=True)
    title = models.CharField(max_length=500, verbose_name='标题', default='', null=True, blank=True)
    tools = models.CharField(max_length=100, verbose_name='工具来源', null=True, blank=False, default='fileleak')
    created = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    cms = models.CharField(max_length=500, verbose_name='CMS', null=True, blank=True)

    def __str__(self):
        return self.url

    class Meta:
        verbose_name = '文件泄露'
        verbose_name_plural = verbose_name

class Nuclei(models.Model):
    scan = models.ForeignKey(Scans, verbose_name='扫描任务', on_delete=models.CASCADE)
    # url = models.ForeignKey(WebApp, verbose_name='web应用', on_delete=models.CASCADE)
    url = models.TextField(verbose_name='url', null=True, blank=True)
    templateID = models.CharField(max_length=500, verbose_name='漏洞名')
    severity = models.CharField(max_length=100, verbose_name='级别')
    matched = models.CharField(max_length=1000, verbose_name='漏洞链接')
    detail = models.TextField(verbose_name='详情')
    mark = models.BooleanField(null=False, verbose_name='标记', default=False)
    created = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    def __Str__(self):
        return self.matched

    class Meta:
        verbose_name = 'nuclei'

class CrawlerURL(models.Model):
    scan = models.ForeignKey(Scans, verbose_name='扫描任务', on_delete=models.CASCADE, blank=True, null=True)
    url = models.TextField(verbose_name='url', null=True, blank=True)
    method = models.CharField(max_length=50, verbose_name='method', null=True, blank=True)
    header = models.TextField(verbose_name='header', null=True, blank=True)
    b64_body = models.TextField(verbose_name='b64_body', null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    def __str__(self):
        return self.url

    class Meta:
        verbose_name = 'URL爬虫'

class Rad2xray(models.Model):
    scan = models.ForeignKey(Scans, verbose_name='扫描任务', on_delete=models.CASCADE, blank=True, null=True)
    # url = models.ForeignKey(WebApp, verbose_name='web应用', on_delete=models.CASCADE)
    target = models.CharField(max_length=1000, verbose_name='target', null=True, blank=True)
    plugin = models.CharField(max_length=100, verbose_name='plugin', null=True, blank=True)
    addr = models.CharField(max_length=1000, verbose_name='漏洞链接', null=True, blank=True)
    payload = models.CharField(max_length=1000, verbose_name='payload', null=True, blank=True)
    snapshot = models.TextField(verbose_name='数据包', null=True, blank=True)
    detail = models.TextField(verbose_name='详情', null=True, blank=True)
    mark = models.BooleanField(null=False, verbose_name='标记', default=False)
    created = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    def __Str__(self):
        return self.addr

    class Meta:
        verbose_name = 'nuclei'

class BlockAssets(models.Model):
    assets = models.CharField(max_length=50, verbose_name='资产')
    description = models.CharField(max_length=200, verbose_name='备注', null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    modified = models.DateTimeField(auto_now=True, verbose_name='修改时间')

    def __str__(self):
        return self.assets

    class Meta:
        verbose_name = '黑名单资产'
        verbose_name_plural = verbose_name
