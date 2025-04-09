from django.contrib import admin
from .models import Person, FamilyGroup
# Register your models here.
class PersonAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'father', 'mother', 'spouse', 'get_family_groups')  # Show these fields in the list
    list_filter = ('family_groups', )  # Right sidebar filters
    search_fields = ('first_name', )  # Top right search box

    def get_family_groups(self, obj):
        return ", ".join([group.name for group in obj.family_groups.all()])
    
    get_family_groups.short_description = "Family Groups"

class FamilyGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'staff_user')  # Show these fields in the list

admin.site.register(Person, PersonAdmin)
admin.site.register(FamilyGroup, FamilyGroupAdmin)