from django.contrib import admin
from django.utils.html import format_html
import urllib
from base64 import urlsafe_b64encode
from django.utils.html import escape
from import_export.admin import ImportExportActionModelAdmin, ExportMixin
from .models import SubDomain, BlockAssets, IP, IPC, Port, WebApp, FileLeak, Nuclei, Rad2xray, CrawlerURL


# Register your models here.
@admin.register(SubDomain)
class SubDomainAdmin(ExportMixin, admin.ModelAdmin):
    # fields = ['scan_task', 'subdomain', 'domain_type', 'record', 'created', 'tools', 'modified']
    readonly_fields = ['scan_task', 'subdomain', 'domain_type', 'record', 'domain_ips', 'tools', 'created', 'modified']
    list_display = ['subdomain', 'domain_type', 'record', 'tools', 'scan_task', 'modified']
    list_filter = ['scan_task', 'tools', 'domain_type']
    search_fields = ('subdomain', 'record', 'domain_ips')
    # list_display_links = []
    list_per_page = 20
    # DONE: 定义action，手动去除在黑名单中的子域名
    actions = ['delete_block_assets_button']

    def delete_block_assets_button(self, request, queryset):
        blocks = BlockAssets.objects.all()
        domains = SubDomain.objects.all()
        ban_domain_dict = [_.assets for _ in blocks]
        for _ in domains:
            if any(ban in _.subdomain for ban in ban_domain_dict):
                _.delete()
        return {
            'state': True,
            'msg': '删除成功！'
        }

    delete_block_assets_button.short_description = '去除黑名单资产'
    delete_block_assets_button.icon = 'fas fa-audio-description'
    delete_block_assets_button.type = 'danger'
    delete_block_assets_button.confirm = '确定要去除黑名单资产吗？'
    delete_block_assets_button.enable = True


@admin.register(BlockAssets)
class BlockAssetsAdmin(ImportExportActionModelAdmin):
    # fields = ['assets', 'description', 'created', 'modified']
    readonly_fields = ['created', 'modified']
    list_display = ['assets', 'description', 'created', 'modified']
    list_per_page = 20
    list_filter = ['assets', 'description', 'created', 'modified']


@admin.register(IP)
class IPAdmin(ExportMixin, admin.ModelAdmin):
    # fields = ['ip', 'scan', 'subdomain', 'is_cdn', 'tools']
    readonly_fields = ['ip', 'scan', 'subdomain', 'is_cdn', 'tools', 'created']
    list_display = ['ip', 'subdomain', 'ip_info', 'scan', 'is_cdn', 'tools', 'created']
    list_per_page = 20
    list_filter = ['scan', 'is_cdn']
    # fix bug: search_fields: Dont' filter on a ForeignKey field itself! by _lin9e 21.07.21
    # to: foreignkeyfield__name {name指的是外键中字段名}
    search_fields = ('subdomain__subdomain', 'ip', 'scan__scan_name',)

    def ip_info(self, obj):
        try:
            return '<a href="{}" target="view_window">{}</a>'.format('http://demo.ip-api.com/json/'+str(obj.ip), 'info')
        except Exception as e:
            return e
    ip_info.allow_tags = True
    ip_info.short_description = 'IP信息'

@admin.register(IPC)
class IPCAdmin(ExportMixin, admin.ModelAdmin):
    readonly_fields = ['ipc', 'scan', 'ipc_count', 'created']
    list_display = ['ipc', 'ipc_fofa', 'ipc_count', 'scan', 'created']
    list_per_page = 20
    list_filter = ['scan', 'created', ]
    search_fields = ['ipc', ]

    def ipc_fofa(self, obj):
        try:
            qbase64 = "ip="+str(obj.ipc)
            fofa_url = "https://fofa.so/result?qbase64=" + urllib.parse.quote(urlsafe_b64encode(qbase64.encode('ascii')))
            return '<a href="{}" target="view_window">{}</a>'.format(fofa_url, obj.ipc)
        except Exception as e:
            return e
    ipc_fofa.allow_tags = True
    ipc_fofa.short_description = "C段情报"

@admin.register(Port)
class PortAdmin(ExportMixin, admin.ModelAdmin):
    # fields = ['ip_port', 'service', 'scan', 'tools']
    readonly_fields = ['ip_port', 'service', 'scan', 'created', 'modified']
    list_display = ['ip_port', 'subdomain_field', 'port', 'service', 'tools', 'scan', 'created']
    list_per_page = 20
    list_filter = ['scan']
    search_fields = ('ip__ip', 'port', 'service', 'ip_port')


@admin.register(WebApp)
class WebAppAdmin(ExportMixin, admin.ModelAdmin):
    # fields = ['url', 'scan', 'banner', 'status_code', 'title', 'content_length', 'webserver',]
    readonly_fields = ['url', 'scan', 'banner', 'status_code', 'title', 'content_length', 'created', 'modified']
    list_display = ['show_url', 'title', 'status_code', 'content_length', 'webserver', 'scan', 'created', 'modified']
    list_per_page = 20
    list_filter = ['scan', 'status_code']
    search_fields = ('url', 'title', 'webserver')

    def show_url(self, obj):
        return '<a href="{}" target="view_window">{}</a>'.format(obj.url, obj.url)
    show_url.allow_tags = True
    show_url.short_description = "URL"

@admin.register(FileLeak)
class FileLeakAdmin(ExportMixin, admin.ModelAdmin):
    # fields = ['url_field', 'title', 'scan', 'content_length', 'status_code', 'tools', 'created']
    readonly_fields = ['url', 'title', 'cms', 'scan', 'content_length', 'status_code', 'tools', 'created']
    list_display = ['show_url_field', 'title', 'cms', 'content_length', 'status_code', 'tools', 'scan', 'created']
    list_per_page = 20
    list_filter = ['scan__scan_name', 'tools', ]
    search_fields = ('url', 'path', 'title', 'cms')

    def show_url_field(self, obj):
        url = str(obj.url)
        return '<a href="{}" target="view_window">{}</a>'.format(url, url)
    show_url_field.allow_tags = True
    show_url_field.short_description = '链接地址'

@admin.register(Nuclei)
class NucleiAdmin(ExportMixin, admin.ModelAdmin):
    # fields = ['scan', 'url', 'templateID', 'severity', 'matched', 'detail', 'mark', 'created']
    readonly_fields = ['scan', 'url', 'templateID', 'severity', 'matched', 'detail', 'created']
    # TODO. detail字段显示为点击出现效果
    list_display = ['show_matched_field', 'templateID', 'severity', 'scan', 'mark', 'created']
    list_per_page = 20
    list_filter = ['scan__scan_name', 'severity', 'mark', ]
    list_editable = ('mark',)
    search_fields = ('url', 'templateID', 'matched')

    def show_matched_field(self, obj):
        return '<a href="{}" target="view_window">{}</a>'.format(str(obj.matched), str(obj.matched))
    show_matched_field.allow_tags = True
    show_matched_field.short_description = '漏洞链接'

@admin.register(CrawlerURL)
class CrawlerURLAdmin(ExportMixin, admin.ModelAdmin):
    readonly_fields = ['scan', 'url', 'method', 'header', 'b64_body', 'created']
    # TODO. detail字段显示为点击出现效果
    list_display = ['show_matched_field', 'method', 'b64_body', 'scan', 'created']
    list_per_page = 20
    list_filter = ['scan__scan_name', 'method', ]
    search_fields = ('url', 'header', 'b64_body')

    def show_matched_field(self, obj):
        return '<a href="{}" target="view_window">{}</a>'.format(str(obj.url), str(obj.url))
    show_matched_field.allow_tags = True
    show_matched_field.short_description = 'URL'

    # def show_post_body(self, obj):
    #     return ''.format(b64decode(obj.b64_body) if len(obj.b64_body) > 2 else obj.b64_body)
    # show_post_body.short_description = 'POST参数'

@admin.register(Rad2xray)
class Rad2xrayAdmin(ExportMixin, admin.ModelAdmin):
    # fields = ['scan', 'target', 'plugin', 'addr', 'payload', 'snapshot', 'detail', 'mark', 'created']
    readonly_fields = ['scan', 'target', 'plugin', 'addr', 'safe_payload', 'snapshot', 'detail', 'created']
    # TODO. detail字段显示为点击出现效果
    list_display = ['show_matched_field', 'plugin', 'safe_payload', 'scan', 'mark', 'created']
    list_per_page = 20
    list_filter = ['scan__scan_name', 'plugin', 'mark', ]
    list_editable = ('mark',)
    search_fields = ('addr', 'plugin', 'detail')

    def show_matched_field(self, obj):
        return '<a href="{}" target="view_window">{}</a>'.format(str(obj.addr), str(obj.addr))
    show_matched_field.allow_tags = True
    show_matched_field.short_description = '漏洞链接'

    def safe_payload(self, obj):
        # 修复xss问题 by _lin9e in 2021.9.16
        return escape(obj.payload)
    safe_payload.short_description = 'Payload'
    safe_payload.allow_tags = True
