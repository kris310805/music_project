from django.contrib import admin
from django.shortcuts import get_object_or_404, render
from .models import *

from django.utils.safestring import mark_safe 

from django.http import HttpResponse
from .pdf_utils import generate_artists_pdf, generate_tracks_pdf, generate_release_pdf

from django.contrib import messages
from .models import Artist, Genre, Label, Release, Track, Playlist, Scrobble

# Действие для экспорта в PDF
def export_artists_to_pdf(modeladmin, request, queryset):
    """Экспорт выбранных исполнителей в PDF"""
    pdf_buffer = generate_artists_pdf(queryset)
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="artists_report.pdf"'
    return response
export_artists_to_pdf.short_description = "Экспорт выбранных исполнителей в PDF"

def export_tracks_to_pdf(modeladmin, request, queryset):
    """Экспорт выбранных треков в PDF"""
    pdf_buffer = generate_tracks_pdf(queryset)
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="tracks_report.pdf"'
    return response
export_tracks_to_pdf.short_description = "Экспорт выбранных треков в PDF"




# ДЕЙСТВИЯ ДЛЯ АДМИНКИ

# Действия для Artist
def make_artists_featured(modeladmin, request, queryset):
    """Пометить исполнителей как избранных (добавляем в название)"""
    updated = queryset.update(name=models.F('name') + ' ★')
    messages.success(request, f'{updated} исполнителей помечены как избранные')
make_artists_featured.short_description = "Пометить как избранных"

def clear_artist_biographies(modeladmin, request, queryset):
    """Очистить биографии выбранных исполнителей"""
    updated = queryset.update(biography='')
    messages.warning(request, f'Биографии {updated} исполнителей очищены')
clear_artist_biographies.short_description = "Очистить биографии"

# Действия для Track
def publish_tracks(modeladmin, request, queryset):
    """Опубликовать выбранные треки"""
    updated = queryset.update(status='published')
    messages.success(request, f'{updated} треков опубликовано')
publish_tracks.short_description = "Опубликовать треки"

def draft_tracks(modeladmin, request, queryset):
    """Перевести треки в черновики"""
    updated = queryset.update(status='draft')
    messages.info(request, f'{updated} треков переведены в черновики')
draft_tracks.short_description = "В черновики"

def archive_tracks(modeladmin, request, queryset):
    """Архивировать треки"""
    updated = queryset.update(status='archived')
    messages.info(request, f'{updated} треков архивировано')
archive_tracks.short_description = "Архивировать треки"

# Действия для Release
def mark_as_digital(modeladmin, request, queryset):
    """Пометить релизы как цифровые"""
    updated = queryset.update(format='Digital')
    messages.success(request, f'{updated} релизов помечены как цифровые')
mark_as_digital.short_description = "Пометить как цифровые"

def duplicate_releases(modeladmin, request, queryset):
    """Дублировать выбранные релизы"""
    new_releases = []
    for release in queryset:
        # Создаем копию с новым названием
        new_release = Release.objects.create(
            title=f"{release.title} (копия)",
            artist=release.artist,
            label=release.label,
            format=release.format,
            release_year=release.release_year,
            cover_image=release.cover_image
        )
        new_releases.append(new_release)
    
    messages.success(request, f'Создано {len(new_releases)} копий релизов')
duplicate_releases.short_description = "Дублировать релизы"

# Действия для Playlist
def make_playlists_public(modeladmin, request, queryset):
    """Сделать плейлисты публичными"""
    updated = queryset.update(is_public=True)
    messages.success(request, f'{updated} плейлистов стали публичными')
make_playlists_public.short_description = "Сделать публичными"

def make_playlists_private(modeladmin, request, queryset):
    """Сделать плейлисты приватными"""
    updated = queryset.update(is_public=False)
    messages.info(request, f'{updated} плейлистов стали приватными')
make_playlists_private.short_description = "Сделать приватными"

# Сложное действие с дополнительной формой
def update_release_years(modeladmin, request, queryset):
    """Обновить годы релизов с формой"""
    if 'apply' in request.POST:
        try:
            years_to_add = int(request.POST.get('years_to_add', 0))
            updated = queryset.update(release_year=models.F('release_year') + years_to_add)
            messages.success(request, f'Год выпуска обновлен для {updated} релизов')
            return None
        except ValueError:
            messages.error(request, 'Введите корректное число лет')
    
    return render(request, 'admin/update_release_years.html', {
        'releases': queryset,
        'action_name': 'update_release_years'
    })
update_release_years.short_description = "Обновить годы выпуска"


# Настройка для Исполнителей
@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    # Что показывать в списке
    list_display = ['name', 'display_image', 'get_release_count', 'created_at']
    
    # По каким полям можно фильтровать
    list_filter = ['created_at']
    
    # По каким полям можно искать
    search_fields = ['name']
    
    # Какие поля нельзя редактировать
    readonly_fields = ['display_image','created_at']
    
    # Какие поля ссылаются на страницу редактирования
    list_display_links = ['name']
    
    actions = [export_artists_to_pdf, make_artists_featured, clear_artist_biographies]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'biography', 'image')
        }),
        ('Ссылки на социальные сети', {
            'fields': ('website', 'spotify_url', 'youtube_url'),
            'classes': ('collapse',)  # Сворачиваемый блок
        }),
        ('Даты', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    # ДОБАВЬТЕ ЭТОТ МЕТОД:
    @admin.display(description='Фото')
    def display_image(self, obj):
        if obj.image:  # проверяем, есть ли изображение
            return mark_safe(f'<img src="{obj.image.url}" width="50" height="50" style="object-fit: cover;" />')
        return "Нет фото"
    
    
    
    # Собственный метод для отображения количества релизов
    @admin.display(description='Количество релизов')
    def get_release_count(self, obj):
        return obj.releases.count()

# Настройка для Лейблов
@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    list_display = ['name', 'founded_year']
    list_display_links = ['name']
    search_fields = ['name']
    list_filter = ['founded_year']

# Настройка для Жанров
@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_track_count']
    search_fields = ['name']
    
    @admin.display(description='Количество треков')
    def get_track_count(self, obj):
        return obj.tracks.count()

# Встроенное отображение треков внутри релиза
class TrackInline(admin.TabularInline):
    model = Track
    extra = 1  # Количество пустых строк для добавления
    readonly_fields = ['created_at']
    raw_id_fields = ['release']  # Для больших таблиц

# Настройка для Релизов
@admin.register(Release)
class ReleaseAdmin(admin.ModelAdmin):
    list_display = ['title', 'artist', 'has_streaming_links', 'display_cover', 'release_year', 'format', 'is_new', 'get_track_count']
    list_display_links = ['title']
    list_filter = ['format', 'release_year', 'artist']
    search_fields = ['title', 'artist__name']
    
    # Используем raw_id_fields для больших таблиц
    raw_id_fields = ['artist', 'label']
    
    readonly_fields = [ 'display_cover','created_at']
    inlines = [TrackInline]  # Показываем треки внутри релиза
    
    # Иерархия по датам
    date_hierarchy = 'created_at'
    
    actions = [mark_as_digital, duplicate_releases]
    
    def export_release_pdf(self, request, release_id):
        """Экспорт конкретного релиза в PDF"""
        from .models import Release
        release = Release.objects.get(id=release_id)
        pdf_buffer = generate_release_pdf(release)
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="release_{release.id}.pdf"'
        return response
    
    def get_urls(self):
        """Добавляем кастомный URL для экспорта релиза"""
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('<path:object_id>/export-pdf/', 
                 self.admin_site.admin_view(self.export_release_pdf),
                 name='catalog_release_export_pdf'),
        ]
        return custom_urls + urls
    
    # Добавляем кнопку в детальную страницу релиза
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_export_button'] = True
        return super().change_view(request, object_id, form_url, extra_context=extra_context)
    
    
    
    @admin.display(description='Обложка')
    def display_cover(self, obj):
        if obj.cover_image:  # проверяем, есть ли обложка
            return mark_safe(f'<img src="{obj.cover_image.url}" width="50" height="50" style="object-fit: cover;" />')
        return "Нет обложки"
    
    
    @admin.display(description='Треков')
    def get_track_count(self, obj):
        return obj.tracks.count()
    
    @admin.display(description='ТЕСТ')
    def test_method(self, obj):
        return "РАБОТАЕТ"

# Настройка для Треков
@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ['title', 'get_artist_name', 'release', 'status', 'has_audio', 'has_lyrics', 'added_recently', 'get_duration', 'created_at']
    list_display_links = ['title']
    list_filter = ['release__artist', 'genres', 'release__release_year', 'status']
    search_fields = ['title', 'release__title', 'release__artist__name']
    
    # Для больших таблиц используем raw_id_fields
    raw_id_fields = ['release']
    
    readonly_fields = ['created_at', 'display_audio_info', 'display_lyrics_info']
    
    # Для выбора жанров используем горизонтальный фильтр
    filter_horizontal = ['genres']
    
    actions = [export_tracks_to_pdf, publish_tracks, draft_tracks, archive_tracks]
    
    
    
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'release', 'duration_seconds', 'position', 'genres', 'status')
        }),
        ('Файлы', {
            'fields': ('audio_file', 'lyrics_file', 'display_audio_info', 'display_lyrics_info'),
            'classes': ('collapse',)  # Сворачиваемый блок
        }),
        ('Даты', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    @admin.display(description='Аудио информация')
    def display_audio_info(self, obj):
        if obj.audio_file:
            return mark_safe(f"""
                <strong>Файл:</strong> {obj.audio_file.name}<br>
                <strong>Размер:</strong> {obj.audio_file.size / 1024 / 1024:.2f} MB<br>
                <audio controls style="width: 300px; margin-top: 5px;">
                    <source src="{obj.audio_file.url}" type="audio/mpeg">
                    Ваш браузер не поддерживает аудио элементы.
                </audio>
            """)
        return "Аудиофайл не загружен"
    
    @admin.display(description='Текст песни')
    def display_lyrics_info(self, obj):
        if obj.lyrics_file:
            return mark_safe(f"""
                <strong>Файл:</strong> {obj.lyrics_file.name}<br>
                <strong>Размер:</strong> {obj.lyrics_file.size / 1024 / 1024:.2f} MB<br>
                <a href="{obj.lyrics_file.url}" target="_blank" class="button">Скачать текст</a>
            """)
        return "Файл с текстом не загружен"
    
    
    
    @admin.display(description='Исполнитель')
    def get_artist_name(self, obj):
        return obj.release.artist.name
    
    @admin.display(description='Длительность')
    def get_duration(self, obj):
        minutes = obj.duration_seconds // 60
        seconds = obj.duration_seconds % 60
        return f"{minutes}:{seconds:02d}"

# Настройка для Плейлистов
@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'get_track_count', 'is_public', 'created_at']
    list_display_links = ['title']
    list_filter = ['is_public', 'created_at', 'user']
    search_fields = ['title', 'user__username']
    
    raw_id_fields = ['user']  # Для пользователей
    
    readonly_fields = ['created_at']
    
    
    
    date_hierarchy = 'created_at'
    
    actions = [make_playlists_public, make_playlists_private]
    
    @admin.display(description='Треков')
    def get_track_count(self, obj):
        return obj.tracks.count()

# Настройка для Прослушиваний
@admin.register(Scrobble)
class ScrobbleAdmin(admin.ModelAdmin):
    list_display = ['user', 'track', 'listened_today', 'get_artist_name', 'scrobbled_at']
    list_display_links = ['track']
    list_filter = ['scrobbled_at', 'user']
    search_fields = ['track__title', 'user__username', 'track__release__artist__name']
    
    # Для больших таблиц
    raw_id_fields = ['user', 'track']
    
    date_hierarchy = 'scrobbled_at'
    
    @admin.display(description='Исполнитель')
    def get_artist_name(self, obj):
        return obj.track.release.artist.name
    
    
    
# Админка для through модели
#@admin.register(TrackFeature)
#class TrackFeatureAdmin(admin.ModelAdmin):
#    list_display = ['playlist', 'track', 'position', 'added_by', 'added_at']
#    list_display_links = ['track']
#    list_filter = ['playlist', 'added_by', 'added_at']
#    search_fields = ['track__title', 'playlist__title', 'added_by__username']
#    raw_id_fields = ['playlist', 'track', 'added_by']
#    readonly_fields = ['added_at']
#    date_hierarchy = 'added_at'


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'artist', 'document_type', 'get_file_extension', 'uploaded_at']
    list_filter = ['document_type', 'uploaded_at', 'artist']
    search_fields = ['title', 'artist__name']
    raw_id_fields = ['artist']
    readonly_fields = ['uploaded_at', 'display_file_info']
    
    @admin.display(description='Тип файла')
    def get_file_extension(self, obj):
        return obj.get_file_extension()
    
    @admin.display(description='Информация о файле')
    def display_file_info(self, obj):
        if obj.file:
            file_url = obj.file.url
            file_extension = obj.get_file_extension().lower()
            
            if file_extension in ['jpg', 'png', 'jpeg']:
                preview = f'<img src="{file_url}" width="200" style="margin: 10px 0;"><br>'
            elif file_extension == 'pdf':
                preview = f'<a href="{file_url}" target="_blank" class="button">Открыть PDF</a><br>'
            else:
                preview = f'<a href="{file_url}" target="_blank" class="button">Скачать файл</a><br>'
            
            return mark_safe(f"""
                {preview}
                <strong>Файл:</strong> {obj.file.name}<br>
                <strong>Размер:</strong> {obj.get_file_size()}<br>
                <strong>Тип:</strong> {file_extension.upper()}
            """)
        return "Файл не загружен"