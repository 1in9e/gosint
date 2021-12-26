from django.contrib import admin
from gosint.tasks import task_worker
from celery.result import AsyncResult
from gosint.celery import app
from .models import Scans


# Register your models here.
@admin.register(Scans)
class ScanAdmin(admin.ModelAdmin):
    fields = ['scan_name', 'target', 'scan_type', 'scan_level', 'user', ]
    readonly_fields = ['scan_status', 'last_scan_date', 'user', ]
    list_display = ['scan_name', 'get_targets', 'scan_type', 'scan_status', 'user', 'last_scan_date']
    list_filter = ['scan_name', 'scan_status']

    def get_targets(self, obj):
        if len(obj.target.all()) < 10:
            res = '<br>'.join([p.target_name for p in obj.target.all()])
        else:
            res = '<br>'.join([p.target_name for p in obj.target.all()[0:10]]) + "<br>......"
        return res
    get_targets.short_description = '扫描目标'

    def save_model(self, request, obj, form, change):
        # 重写方法，发送celery扫描任务
        super(ScanAdmin, self).save_model(request, obj, form, change)
        celery_id = app.send_task('gosint.tasks.task_worker', args=([t.pk for t in form.cleaned_data['target']], obj.scan_type.pk, obj.pk,), queue='server')
        obj.celery_id = celery_id
        obj.user = str(request.user)
        obj.save()

    def get_queryset(self, request):
        """
        每次获取扫描状态
        :param request:
        :return:
        """
        # TODO：任务完成后自动刷新数据库
        # Done：fix：2021-1-6 by le31ei: 当redis重启后，celery id对应的task就没有了，获取状态会一直未PENDDING
        qs = super(ScanAdmin, self).get_queryset(request)
        if qs.count() > 0:
            for _ in qs:
                if _.celery_id == 'SUCCESS' or _.celery_id == 'FAILURE' or _.celery_id == 'REVOKED' or not _.celery_id:
                    continue                   # 扫描成功或者失败后不再进行异步查询
                task_id = _.celery_id
                status = AsyncResult(task_id).status
                if status == 'SUCCESS':
                    _.celery_id = 'SUCCESS'    # 扫描成功后将celery的id置为成功
                if status == 'FAILURE':
                    _.celery_id = 'FAILURE'
                if status == 'REVOKED':
                    _.celery_id = 'REVOKED'
                _.scan_status = status
                _.save()
        return qs

    actions = ['rescan', ]

    def rescan(self):
        pass

    rescan.short_description = '测试按钮'
