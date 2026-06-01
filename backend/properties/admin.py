from django.contrib import admin
from .models import Category, Agent, Property, PropertyImage, Wishlist, ContactMessage

class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title','owner','listing_type','property_type','price','location','status','approval_status','is_featured','created_at')
    list_filter = ('listing_type','property_type','status','approval_status','furnished','is_featured')
    search_fields = ('title','location','description')
    actions = ['approve_properties', 'reject_properties']
    inlines = [PropertyImageInline]

    @admin.action(description='Approve selected properties')
    def approve_properties(self, request, queryset):
        queryset.update(approval_status='approved')

    @admin.action(description='Reject selected properties')
    def reject_properties(self, request, queryset):
        queryset.update(approval_status='rejected')

admin.site.register(Category)
admin.site.register(Agent)
admin.site.register(Wishlist)
admin.site.register(ContactMessage)
admin.site.register(PropertyImage)
