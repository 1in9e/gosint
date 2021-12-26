from django.db import models
from simplepro.components import fields

# Create your models here.
class EngineType(models.Model):
    """
    扫描引擎定义
    """
    engine_name = fields.CharField(max_length=200, verbose_name='引擎名称')
    subdomain_discovery = fields.SwitchField(null=True, verbose_name='扫描子域名', default=True)
    certip_scan = fields.SwitchField(null=True, verbose_name='cert_ip', default=False)
    port_scan = fields.SwitchField(null=True, verbose_name='扫描端口', default=True)
    port_api = fields.SwitchField(null=True, verbose_name='port_api[C段]', default=False)
    fetch_url = fields.SwitchField(null=True, verbose_name='扫描Web', default=True)
    dir_file_search = fields.SwitchField(null=False, verbose_name='目录扫描', default=False)
    vuln_nuclei = fields.SwitchField(null=False, default=False, verbose_name='nuclei扫描')
    vuln_xray = fields.SwitchField(null=False, default=False, verbose_name='xray被动扫描')
    # 端口扫描类型定义
    port_scan_choices = (
        (u'top10', u'top10'),
        (u'top100', u'top100'),
        (u'top1000', u'top1000'),
        (u'all', u'全端口')
    )
    port_scan_type = models.CharField(max_length=20, choices=port_scan_choices, verbose_name='端口扫描模式', default='top10')
    # dir_file_search 扫描路径类型定义
    dir_file_choices = (
        (u'top100', u'top100'),
        (u'top2000', u'top2000'),
        (u'top8000', u'top8000')
    )
    dir_file_type = models.CharField(max_length=20, choices=dir_file_choices, verbose_name='目录扫描模式', default='top100')

    def __str__(self):
        return self.engine_name

    class Meta:
        verbose_name = '扫描引擎'
        verbose_name_plural = verbose_name


class Wordlist(models.Model):
    name = models.CharField(max_length=200, verbose_name='字典名称')
    short_name = models.CharField(max_length=50, unique=True, verbose_name='字典简称')
    count = models.IntegerField(default=0, verbose_name='数量')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '字典'
        verbose_name_plural = verbose_name


class Configuration(models.Model):
    name = models.CharField(max_length=200, verbose_name='配置名称')
    short_name = models.CharField(max_length=50, unique=True, verbose_name='配置简称')
    content = models.TextField(verbose_name='配置内容')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '配置'
        verbose_name_plural = verbose_name


