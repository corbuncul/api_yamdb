from django.contrib import admin

from reviews.models import Category, Comments, Genre, Review, Title

admin.site.empty_value_display = '-пусто-'


@admin.register(Category, Genre)
class CategoryGenreAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')
    search_fields = ('name',)


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = (
        'pk', 'name', 'description', 'year', 'category', 'display_genres'
    )
    search_fields = ('name',)
    list_filter = ('year', 'category')
    list_editable = ('category',)

    @admin.display(description='Genres')
    def display_genres(self, obj):
        return ", ".join([genre.name for genre in obj.genre.all()])


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('pk', 'author', 'text', 'pub_date')
    search_fields = ('author_username', 'text')
    list_filter = ('author', 'pub_date')


@admin.register(Comments)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'author', 'review', 'text', 'pub_date')
    search_fields = ('author_username', 'review_name')
    list_filter = ('author', 'review', 'pub_date')
