from django.contrib import admin
from .models  import SearchQuery
# Register your models here.

# Displays on /admin webpage, all queries made on the web on homepages along with the timestamp.
class SearchQueryAdmin(admin.ModelAdmin):
  list_display =('query', 'created_at')

admin.site.register(SearchQuery, SearchQueryAdmin)
