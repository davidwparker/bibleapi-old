from django.contrib import admin
from verses.models import Verse

class VerseAdmin(admin.ModelAdmin):
  list_display = ('version','book','chapter','verse',)
  search_fields = ('version','book','chapter',)

admin.site.register(Verse, VerseAdmin)
