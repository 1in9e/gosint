from django.db import models
from datetime import datetime
from simplepro.components import fields


class Project(models.Model):
    project_name = fields.CharField(max_length=50, blank=True, null=True, verbose_name='项目名称', input_type='text',
                                    placeholder='请输入项目名称')
    project_description = fields.CharField(verbose_name='项目描述', input_type='textarea', placeholder='描述',
                                           max_length=500)
    create_time = models.DateTimeField(default=datetime.now, verbose_name='创建时间')
    update_time = models.DateTimeField(null=True, verbose_name='更新时间')

    def __str__(self):
        return self.project_name

    class Meta:
        verbose_name = '项目'
        verbose_name_plural = verbose_name


class Target(models.Model):
    """
    目标域名信息或者IP信息
    """
    # fix bug error.2021.12.26 _lin9e [django原生外键没有问题]
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name='工程名', null=True)
    target_type = fields.CharField(max_length=50, default='domain', verbose_name='资产类型',
                                  choices=(('domain', '域名'), ('ip', 'ip资产')))
    target_name = models.TextField(blank=True, null=True, verbose_name='资产内容', unique=True)
    target_description = fields.CharField(max_length=500, verbose_name='描述', null=True, blank=True, default='',
                                          placeholder='可空')
    target_icp = models.CharField(max_length=300, verbose_name='域名备案', null=True, blank=True, default='')
    last_scan_time = models.DateTimeField(null=True, verbose_name='上次扫描时间')
    create_time = models.DateTimeField(verbose_name='创建时间', default=datetime.now)
    update_time = models.DateTimeField(null=True, verbose_name='更新时间')

    def __str__(self):
        return '{}:{}'.format(self.project, self.target_name)

    class Meta:
        verbose_name = '资产信息'
        verbose_name_plural = verbose_name

