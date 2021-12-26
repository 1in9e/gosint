from django.db import models
from apps.targetApp.models import Target
from apps.scanEngine.models import EngineType
from simplepro.components import fields


# Create your models here.
class Scans(models.Model):
    scan_name = fields.CharField(max_length=50, verbose_name='扫描任务名称', unique=True, null=True, blank=True)
    target = fields.TransferField(Target, blank=True, help_text=u'选择扫描资产',  verbose_name='扫描资产', titles=['待选', '已选'])
    user = models.CharField(max_length=50, blank=True, null=True, verbose_name='添加者')
    scan_level = fields.SliderField(default=10, verbose_name='扫描优先级', max_value=10, min_value=1)
    celery_id = models.CharField(max_length=100, blank=True, verbose_name='celery任务', null=True)
    scan_type = fields.ForeignKey(EngineType, on_delete=models.CASCADE, verbose_name='扫描类型', null=True, blank=True)
    scan_status = models.CharField(verbose_name='扫描状态', default='0', max_length=10,
                                      choices=(('PENDING', '正在扫描'), ('FAILURE', '扫描失败'),
                                               ('RETRY', '正在重试'), ('SUCCESS', '扫描完成'),
                                               ('REVOKED', '任务撤销'), ('STARTED', '开始扫描')))
    last_scan_date = models.DateTimeField(null=True, blank=True, auto_now_add=True, verbose_name='最后扫描日期')

    def __str__(self):
        return self.scan_name

    class Meta:
        verbose_name = '扫描任务'
        verbose_name_plural = verbose_name



