from django.contrib import admin
from django.utils.safestring import mark_safe
from contrib.errors.models import Error
import urllib


class ErrorAdmin(admin.ModelAdmin):
    list_display = ('path', 'kind', 'info', 'when')
    list_display_links = ('path',)
    ordering = ('-id',)
    search_fields = ('path', 'kind', 'info', 'data')
    readonly_fields = ('path', 'kind', 'info', 'data', 'when', 'html',)
    fieldsets = (
        (None, {'fields': ('kind', 'data', 'info')}),
    )

    def has_delete_permission(self, request, obj=None):
        """
        Disabling the delete permissions
        """
        return True

    def has_add_permission(self, request):
        """
        Disabling the create permissions
        """
        return False

    def change_view(self, request, object_id, extra_context={}):
        """
        The detail view of the error record.
        """
        obj = self.get_object(request, urllib.unquote(object_id))

        extra_context.update({
            'instance': obj,
            'error_body': mark_safe(obj.html),
        })

        return super(ErrorAdmin, self).change_view(request,
                                                   object_id, extra_context)

admin.site.register(Error, ErrorAdmin)
