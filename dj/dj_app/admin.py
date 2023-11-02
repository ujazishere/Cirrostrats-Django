from django.contrib import admin
from .models  import SearchQuery
# from .models  import UniqueQueries
from django.db.models import Count

# Register your models here.

# Displays on /admin webpage, all queries made on the web on homepages along with the timestamp.
class SearchQueryAdmin(admin.ModelAdmin):
    model = SearchQuery
    verbose_name = "Searches"
    list_display =('query', 'created_at', 'count')
    action = ('show_unique_queries')

"""

class UniqueQueriesAdmin(admin.ModelAdmin):
    action = ('show_unique_queries')

    def show_unique_queries(self, request, queryset):
        unique_queries = queryset.values('query').annotate(query_count=Count('query'))
        for item in unique_queries:
            self.message_user(request, f'Query: {item["query"]}, Count: {item["query_count"]}')

    show_unique_queries.short_description = 'Show Unique Queries'
      
    

admin.site.register(SearchQuery, SearchQueryAdmin)
admin.site.register(UniqueQueries, UniqueQueriesAdmin)
"""