from django.contrib import admin
from accounts.models import Affiliate,Referral,Withdrawal

admin.site.register(Affiliate)
admin.site.register(Referral)
admin.site.register(Withdrawal)
