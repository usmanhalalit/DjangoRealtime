try:
    import json

    from django.contrib import admin
    from django.utils.html import format_html

    from djangorealtime.models import Event

    @admin.register(Event)
    class EventAdmin(admin.ModelAdmin):
        list_display = ['id', 'type', 'scope', 'status', 'user_id', 'created_at', 'updated_at']
        list_filter = ['type', 'scope', 'status', 'created_at']
        list_per_page = 10
        search_fields = ['id', 'type', 'user_id']
        readonly_fields = ['created_at', 'updated_at', 'detail_pretty', 'data_store_pretty']
        date_hierarchy = 'created_at'
        ordering = ['-created_at']
        actions = ['replay_events']

        @admin.action(description='Replay selected events')
        def replay_events(self, request, queryset):
            for event in queryset:
                event.replay()
            self.message_user(request, f'{queryset.count()} event(s) replayed successfully.')

        def detail_pretty(self, obj):
            return format_html('<pre>{}</pre>', json.dumps(obj.detail, indent=2))
        detail_pretty.short_description = 'Detail (Pretty)'

        def data_store_pretty(self, obj):
            return format_html('<pre>{}</pre>', json.dumps(obj.data_store, indent=2))
        data_store_pretty.short_description = 'Data Store (Pretty)'

except ImportError:
    # django.contrib.admin is not installed, skip admin registration
    pass
