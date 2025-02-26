from django.contrib import admin
from accounts.models import Affiliate,Referral,Withdrawal,Alert

admin.site.register(Affiliate)
admin.site.register(Referral)
admin.site.register(Withdrawal)


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__username', 'message')
    list_editable = ('is_read',)  # Permite marcar alertas como lidos diretamente na lista