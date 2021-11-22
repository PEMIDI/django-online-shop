from django.contrib import admin

from partner.models import Partner, PartnerStock


class PartnerStockInline(admin.TabularInline):
    model = PartnerStock
    extra = 1


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    inlines = (PartnerStockInline,)
    list_display = ('name',)
