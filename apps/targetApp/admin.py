from django.contrib import admin
from .models import Project, Target
from .forms import AddTargetForm
import re
from import_export.admin import ExportMixin, ImportExportActionModelAdmin
from libs.common import get_domain_icp


# Register your models here.
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    fields = ['project_name', 'project_description', 'create_time', 'update_time']
    readonly_fields = ['create_time', 'update_time']
    list_display = ['project_name', 'project_description', 'create_time', 'update_time']


@admin.register(Target)
class TargetAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ['project', 'target_type', 'target_name', 'target_description', 'target_icp', 'create_time',
              'update_time']
    readonly_fields = ['last_scan_time', 'create_time', 'update_time']
    list_filter = ['project', 'target_type', ]
    search_fields = ['target_name', 'target_icp']
    list_per_page = 20

    form = AddTargetForm

    def save_model(self, request, obj, form, change):
        # 对target_name字段进行换行分割
        # 并且通过正则判断是ip还是域名然后分别进行匹配插入
        targets = obj.target_name
        for target in list(set(targets.splitlines())):
            if len(target) == 0:
                continue
            # if re.match('((?:(?:25[0-5]|2[0-4]\d|[01]?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d?\d))', target):
            if re.match('(?:[0-9]{1,3}\.){3}(?:[0-9]){1,3}(?:\/\d*)?(?:\-\d*)?', target):
                # 所有IP的情况
                obj.target_type = 'ip'
            else:
                obj.target_type = 'domain'
                domain = target if not target[0] == '.' else target[1:]
                obj.target_icp = get_domain_icp(domain)
            obj.target_name = target
            Target.objects.create(project=obj.project, target_type=obj.target_type, target_icp=obj.target_icp,
                                  target_name=target, target_description=obj.target_description)