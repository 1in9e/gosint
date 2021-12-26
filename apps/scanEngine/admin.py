from django.contrib import admin
from .models import EngineType


# Register your models here.
@admin.register(EngineType)
class EngineTypeAdmin(admin.ModelAdmin):
    fields = ('engine_name', 'subdomain_discovery', 'certip_scan', 'port_scan', 'port_api',
              'fetch_url', 'dir_file_search', 'vuln_nuclei', 'vuln_xray', 'port_scan_type', 'dir_file_type')

    list_display = ['engine_name', 'subdomain_discovery', 'certip_scan', 'port_scan', 'port_api',
                    'fetch_url', 'dir_file_search', 'vuln_nuclei', 'vuln_xray', 'port_scan_type', 'dir_file_type']

