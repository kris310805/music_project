from django.shortcuts import render, get_object_or_404, redirect
from .models import Artist, Favorite, Playlist, Release, Track, Genre, Label
from django.db.models import Q

from django.contrib import messages

from django.urls import reverse

from django.db.models import Count, Avg, Sum

from django.contrib.auth.models import User

#from .models import TrackFeature



# Пример 1: Фильтрация релизов по году
def releases_by_year(request, year):
    """Показывает релизы определенного года"""
    releases = Release.objects.filter(release_year=year)
    
    return render(request, 'catalog/filtered_list.html', {
        'title': f'Релизы {year} года',
        'items': releases,
        'description': f'Все релизы выпущенные в {year} году'
    })

# Пример 2: Фильтрация треков по жанру
def tracks_by_genre(request, genre_name):
    """Показывает треки определенного жанра"""
    tracks = Track.objects.filter(genres__name=genre_name)
    
    return render(request, 'catalog/filtered_list.html', {
        'title': f'Треки в жанре "{genre_name}"',
        'items': tracks,
        'description': f'Все треки в жанре {genre_name}'
    })

# Пример 3: Фильтрация исполнителей по стране (если бы было поле country)
def popular_releases(request):
    """Показывает популярные релизы (последние 5 лет)"""
    from django.utils import timezone
    current_year = timezone.now().year
    recent_releases = Release.objects.filter(
        release_year__gte=current_year - 5
    )
    
    return render(request, 'catalog/filtered_list.html', {
        'title': 'Популярные релизы',
        'items': recent_releases,
        'description': 'Релизы за последние 5 лет'
    })

# Пример 4: Фильтрация по нескольким условиям
def digital_recent_releases(request):
    """Цифровые релизы за последние 2 года"""
    from django.utils import timezone
    current_year = timezone.now().year
    
    releases = Release.objects.filter(
        format='Digital',  # цифровые релизы
        release_year__gte=current_year - 2  # за последние 2 года
    )
    
    return render(request, 'catalog/filtered_list.html', {
        'title': 'Свежие цифровые релизы',
        'items': releases,
        'description': 'Цифровые релизы за последние 2 года'
    })
    
    
def index(request):
    """Главная страница с ссылками на примеры filter()"""
    total_artists = Artist.objects.count()
    total_releases = Release.objects.count()
    total_tracks = Track.objects.count()
    
    
    return render(request, 'catalog/index.html', {
        'total_artists': total_artists,
        'total_releases': total_releases, 
        'total_tracks': total_tracks,
    })
    
    
# Примеры использования __ (будут работать с любыми данными из админки)

def artists_by_label(request):
    """Исполнители по лейблу - показывает все лейблы"""
    labels = Label.objects.all()
    selected_label = request.GET.get('label')
    
    artists = None
    if selected_label:
        artists = Artist.objects.filter(releases__label__name=selected_label).distinct()
    
    return render(request, 'catalog/artists_by_label.html', {
        'labels': labels,
        'selected_label': selected_label,
        'artists': artists
    })

def tracks_by_artist(request):
    """Треки по исполнителю - показывает всех исполнителей"""
    artists = Artist.objects.all()
    selected_artist = request.GET.get('artist')
    
    tracks = None
    if selected_artist:
        tracks = Track.objects.filter(release__artist__name=selected_artist)
    
    return render(request, 'catalog/tracks_by_artist.html', {
        'artists': artists,
        'selected_artist': selected_artist,
        'tracks': tracks
    })

def search_tracks(request):
    """Поиск треков - по названию трека или исполнителя"""
    query = request.GET.get('q', '')
    tracks = None
    tracks_exist = False  #   exists() проверку
    
    if query:
        tracks = Track.objects.filter(
            Q(title__icontains=query) | 
            Q(release__artist__name__icontains=query)
        )
        tracks_exist = tracks.exists()  #  exists() - быстрая проверка наличия результато
    
    return render(request, 'catalog/search_tracks.html', {
        'query': query,
        'tracks': tracks,
        'tracks_exist': tracks_exist,  # ✅ Передаем результат exists() в шаблон
    })

def recent_digital_tracks(request):
    """Свежие цифровые треки (последние 2 года)"""
    from django.utils import timezone
    current_year = timezone.now().year
    
    tracks = Track.objects.filter(
        release__format='Digital',
        release__release_year__gte=current_year - 2
    )
    
    return render(request, 'catalog/recent_digital_tracks.html', {
        'tracks': tracks,
        'current_year': current_year
    })

def artists_by_genre(request):
    """Исполнители по жанру - показывает все жанры"""
    genres = Genre.objects.all()
    selected_genre = request.GET.get('genre')
    
    artists = None
    if selected_genre:
        artists = Artist.objects.filter(releases__tracks__genres__name=selected_genre).distinct()
    
    return render(request, 'catalog/artists_by_genre.html', {
        'genres': genres,
        'selected_genre': selected_genre,
        'artists': artists
    })
    
    
# Пример 1: exclude() - треки БЕЗ жанров
def tracks_without_genres(request):
    """Треки без назначенных жанров"""
    tracks = Track.objects.exclude(genres__isnull=False)
    
    return render(request, 'catalog/tracks_list.html', {
        'title': 'Треки без жанров',
        'tracks': tracks,
        'description': 'Треки, у которых не назначены жанры'
    })

# Пример 2: exclude() - релизы БЕЗ лейбла
def releases_without_label(request):
    """Релизы без лейбла"""
    releases = Release.objects.exclude(label__isnull=False)
    
    return render(request, 'catalog/releases_list.html', {
        'title': 'Релизы без лейбла',
        'releases': releases,
        'description': 'Релизы, у которых не указан лейбл'
    })

# Пример 3: exclude() + filter() - треки определенного жанра, но НЕ цифровые
def non_digital_tracks_by_genre(request, genre_name):
    """Треки определенного жанра, но НЕ цифровые"""
    tracks = Track.objects.filter(
        genres__name=genre_name
    ).exclude(
        release__format='Digital'
    )
    
    return render(request, 'catalog/tracks_list.html', {
        'title': f'НЕ цифровые треки в жанре "{genre_name}"',
        'tracks': tracks,
        'description': f'Треки в жанре {genre_name}, которые НЕ в цифровом формате'
    })

# Пример 4: exclude() - исполнители БЕЗ релизов
def artists_without_releases(request):
    """Исполнители без релизов"""
    artists = Artist.objects.exclude(releases__isnull=False)
    
    return render(request, 'catalog/artists_list.html', {
        'title': 'Исполнители без релизов',
        'artists': artists,
        'description': 'Исполнители, у которых нет ни одного релиза'
    })

# Пример 5: exclude() - треки БЕЗ позиции в релизе
def tracks_without_position(request):
    """Треки без указанной позиции в релизе"""
    tracks = Track.objects.exclude(position__isnull=False).exclude(position='')
    
    return render(request, 'catalog/tracks_list.html', {
        'title': 'Треки без позиции',
        'tracks': tracks,
        'description': 'Треки, у которых не указана позиция в релизе (A1, B2 и т.д.)'
    })

# Пример 6: exclude() с несколькими условиями - релизы НЕ цифровые и НЕ последних 2 лет
def old_non_digital_releases(request):
    """Старые НЕ цифровые релизы"""
    from django.utils import timezone
    current_year = timezone.now().year
    
    releases = Release.objects.exclude(
        format='Digital'
    ).exclude(
        release_year__gte=current_year - 2
    )
    
    return render(request, 'catalog/releases_list.html', {
        'title': 'Старые не цифровые релизы',
        'releases': releases,
        'description': f'Релизы НЕ в цифровом формате и старше {current_year - 2} года'
    })
    
    
# Пример 1: order_by() - треки по длительности (от самых коротких к самым длинным)
def tracks_by_duration(request):
    """Треки отсортированные по длительности"""
    tracks = Track.objects.all().order_by('duration_seconds')
    
    return render(request, 'catalog/tracks_ordered.html', {
        'title': 'Треки по длительности',
        'tracks': tracks,
        'description': 'Треки отсортированные от самых коротких к самым длинным'
    })

# Пример 2: order_by() - релизы по году выпуска (новые сверху)
def releases_by_year(request):
    """Релизы отсортированные по году (новые сверху)"""
    releases = Release.objects.all().order_by('-release_year')
    
    return render(request, 'catalog/releases_ordered.html', {
        'title': 'Релизы по году выпуска',
        'releases': releases,
        'description': 'Релизы отсортированные по году выпуска (новые сверху)'
    })
    
    
    
# Пример 1: Использование кастомного менеджера для треков
def long_tracks(request):
    """Длинные треки (более 4 минут) используя кастомный менеджер"""
    tracks = Track.custom.long_tracks()
    
    return render(request, 'catalog/tracks_list.html', {
        'title': 'Длинные треки (4+ минут)',
        'tracks': tracks,
        'description': 'Треки длительностью более 4 минут (используется кастомный менеджер)'
    })

# Пример 2: Использование кастомного менеджера для релизов  
def digital_only_releases(request):
    """Только цифровые релизы используя кастомный менеджер"""
    releases = Release.custom.digital_only()
    
    return render(request, 'catalog/releases_list.html', {
        'title': 'Цифровые релизы',
        'releases': releases,
        'description': 'Только цифровые релизы (используется кастомный менеджер)'
    })

# Пример 3: Упрощенная версия (без timezone)
def recent_digital_tracks(request):
    """Недавние цифровые треки используя кастомные менеджеры"""
    current_year = 2024  # Просто укажи текущий год
    
    # Простой способ - используем стандартные фильтры
    tracks = Track.objects.filter(
        release__format='Digital',
        release__release_year__gte=current_year - 2
    )
    
    return render(request, 'catalog/tracks_list.html', {
        'title': 'Треки из недавних цифровых релизов',
        'tracks': tracks,
        'description': 'Треки из цифровых релизов за последние 2 года'
    })
    
    
# Детальные страницы с использованием get_absolute_url
def artist_detail(request, pk):
    """Детальная страница исполнителя"""
    artist = get_object_or_404(Artist, pk=pk)
    
    artist_releases = artist.releases.all()  # Все релизы исполнителя
    recent_releases = artist.releases.filter(release_year__gte=2020)  # Новые релизы
    
    return render(request, 'catalog/detail_page.html', {
        'title': f'Исполнитель: {artist.name}',
        'object': artist,
        'type': 'artist',
        'releases': artist_releases,  # Передаем в шаблон
        'recent_releases': recent_releases
    })

def release_detail(request, pk):
    """Детальная страница релиза"""
    release = get_object_or_404(Release, pk=pk)
    
    
    
    return render(request, 'catalog/detail_page.html', {
        'title': f'Релиз: {release.title}',
        'object': release,
        'type': 'release'
    })

def track_detail(request, pk):
    """Детальная страница трека"""
    track = get_object_or_404(Track, pk=pk)
    
    return render(request, 'catalog/detail_page.html', {
        'title': f'Трек: {track.title}',
        'object': track,
        'type': 'track'
    })

# Страница для демонстрации get_absolute_url
def demonstrate_urls(request):
    """Демонстрация get_absolute_url и reverse"""
    artists = Artist.objects.all()[:5]  # Первые 5 исполнителей
    releases = Release.objects.all()[:5]  # Первые 5 релизов
    tracks = Track.objects.all()[:5]  # Первые 5 треков
    
    # Пример использования reverse для статических URL
    catalog_url = reverse('index')
    admin_url = reverse('admin:index')
    
    return render(request, 'catalog/demonstrate_urls.html', {
        'artists': artists,
        'releases': releases,
        'tracks': tracks,
        'catalog_url': catalog_url,
        'admin_url': admin_url,
    })
    
    
# Пример 1: Аннотация - количество релизов у исполнителей
def artists_with_stats(request):
    """Исполнители с статистикой по релизам и трекам"""
    from django.db.models import Count, Avg
    
    artists = Artist.objects.annotate(
        release_count=Count('releases'),  # Количество релизов
        avg_tracks_per_release=Avg('releases__tracks')  # Среднее количество треков в релизах
    ).order_by('-release_count')
    
    return render(request, 'catalog/aggregation_list.html', {
        'title': 'Исполнители со статистикой',
        'objects': artists,
        'type': 'artist_stats',
        'description': 'Исполнители с количеством релизов и средним количеством треков в релизах'
    })

# Пример 2: Агрегация - общая статистика по трекам
def tracks_statistics(request):
    """Общая статистика по трекам"""
    from django.db.models import Count, Avg, Sum, Max, Min
    
    stats = Track.objects.aggregate(
        total_tracks=Count('id'),
        avg_duration=Avg('duration_seconds'),
        total_duration=Sum('duration_seconds'),
        longest_track=Max('duration_seconds'),
        shortest_track=Min('duration_seconds')
    )
    status_counts = {
        'draft': Track.objects.filter(status='draft').count(),      #  count()
        'published': Track.objects.filter(status='published').count(),  #  count()
        'archived': Track.objects.filter(status='archived').count(),    #  count()
    }
    # Конвертируем секунды в минуты для удобства
    if stats['avg_duration']:
        stats['avg_duration_min'] = stats['avg_duration'] / 60
    if stats['total_duration']:
        stats['total_duration_min'] = stats['total_duration'] / 60
    if stats['longest_track']:
        stats['longest_track_min'] = stats['longest_track'] / 60
    if stats['shortest_track']:
        stats['shortest_track_min'] = stats['shortest_track'] / 60
    
    return render(request, 'catalog/aggregation_stats.html', {
        'title': 'Статистика по трекам',
        'stats': stats,
        'status_counts': status_counts,
        'type': 'tracks_stats',
        'description': 'Общая статистика по всем трекам в каталоге'
    })
    
    
# Пример 3: Аннотация - жанры с количеством треков
def genres_with_track_count(request):
    """Жанры с количеством треков"""
    from django.db.models import Count
    
    genres = Genre.objects.annotate(
        track_count=Count('tracks')
    ).order_by('-track_count')
    
    return render(request, 'catalog/aggregation_list.html', {
        'title': 'Жанры по популярности',
        'objects': genres,
        'type': 'genre_stats',
        'description': 'Жанры отсортированные по количеству треков'
    })
    
def aggregation_examples(request):
    """Главная страница с примерами агрегации"""
    return render(request, 'catalog/aggregation_examples.html')


# CRUD для жанров - Чтение (Read)
def genre_list(request):
    """Список всех жанров"""
    genres = Genre.objects.all().order_by('name')
    return render(request, 'catalog/crud/genre_list.html', {
        'genres': genres,
        'title': 'Список жанров'
    })

def genre_detail(request, pk):
    """Детальная страница жанра"""
    genre = get_object_or_404(Genre, pk=pk)
    tracks = genre.tracks.all()[:10]  # Первые 10 треков этого жанра
    
    return render(request, 'catalog/crud/genre_detail.html', {
        'genre': genre,
        'tracks': tracks,
        'title': f'Жанр: {genre.name}'
    })

# CRUD для жанров - Создание (Create)
def genre_create(request):
    """Создание нового жанра"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        
        if name:
            genre = Genre.objects.create(
                name=name,
                description=description
            )
            messages.success(request, f'Жанр "{genre.name}" успешно создан!')
            return redirect('genre-list')
        else:
            messages.error(request, 'Название жанра обязательно!')
    
    return render(request, 'catalog/crud/genre_form.html', {
        'title': 'Создать новый жанр',
        'action': 'create'
    })

# CRUD для жанров - Редактирование (Update)
def genre_edit(request, pk):
    """Редактирование жанра"""
    genre = get_object_or_404(Genre, pk=pk)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        
        if name:
            genre.name = name
            genre.description = description
            genre.save()
            
            messages.success(request, f'Жанр "{genre.name}" успешно обновлен!')
            return redirect('genre-detail', pk=genre.pk)
        else:
            messages.error(request, 'Название жанра обязательно!')
    
    return render(request, 'catalog/crud/genre_form.html', {
        'title': f'Редактировать жанр: {genre.name}',
        'genre': genre,
        'action': 'edit'
    })

# CRUD для жанров - Удаление (Delete)
def genre_delete(request, pk):
    """Удаление жанра"""
    genre = get_object_or_404(Genre, pk=pk)
    
    if request.method == 'POST':
        genre_name = genre.name
        genre.delete()
        messages.success(request, f'Жанр "{genre_name}" успешно удален!')
        return redirect('genre-list')
    
    return render(request, 'catalog/crud/genre_confirm_delete.html', {
        'genre': genre,
        'title': f'Удалить жанр: {genre.name}'
    })

# Главная страница CRUD
def crud_examples(request):
    """Главная страница с примерами CRUD операций"""
    return render(request, 'catalog/crud/crud_examples.html')



# Примеры select_related() 

def tracks_with_releases(request):
    """Треки с предзагруженными релизами и исполнителями"""
  
    # tracks = Track.objects.all()[:10]

    tracks = Track.objects.select_related('release', 'release__artist')[:10]
    
    return render(request, 'catalog/select_related_examples.html', {
        'title': 'Треки с select_related()',
        'tracks': tracks,
        'description': 'Предзагрузка release и release__artist в одном запросе'
    })

def releases_with_artists(request):
    """Релизы с предзагруженными исполнителями"""
    releases = Release.objects.select_related('artist')[:10]
    
    return render(request, 'catalog/select_related_examples.html', {
        'title': 'Релизы с select_related()',
        'releases': releases,
        'description': 'Предзагрузка artist в одном запросе'
    })

def playlist_with_user(request):
    """Плейлисты с предзагруженными пользователями"""
    playlists = Playlist.objects.select_related('user')[:10]
    
    return render(request, 'catalog/select_related_examples.html', {
        'title': 'Плейлисты с select_related()',
        'playlists': playlists,
        'description': 'Предзагрузка user в одном запросе'
    })

# Сравнение производительности
def performance_comparison(request):
    """Сравнение с и без select_related()"""
    
    # БЕЗ оптимизации
    tracks_slow = Track.objects.all()[:5]
    
    # С оптимизацией
    tracks_fast = Track.objects.select_related('release__artist')[:5]
    
    return render(request, 'catalog/performance_comparison.html', {
        'tracks_slow': tracks_slow,
        'tracks_fast': tracks_fast,
        'title': 'Сравнение производительности'
    })
    
    
# Примеры prefetch_related() - добавьте после select_related примеров

def tracks_with_genres(request):
    """Треки с предзагруженными жанрами"""
    # БЕЗ оптимизации - делает N+1 запросов
    # tracks = Track.objects.all()[:10]
    
    # С оптимизацией - делает 2 запроса
    tracks = Track.objects.prefetch_related('genres')[:10]
    
    return render(request, 'catalog/prefetch_related_examples.html', {
        'title': 'Треки с prefetch_related()',
        'tracks': tracks,
        'description': 'Предзагрузка жанров для треков'
    })

def artists_with_releases(request):
    """Исполнители с предзагруженными релизами"""
    artists = Artist.objects.prefetch_related('releases')[:10]
    
    return render(request, 'catalog/prefetch_related_examples.html', {
        'title': 'Исполнители с prefetch_related()',
        'artists': artists,
        'description': 'Предзагрузка релизов для исполнителей'
    })

def releases_with_tracks(request):
    """Релизы с предзагруженными треками"""
    releases = Release.objects.prefetch_related('tracks')[:10]
    
    return render(request, 'catalog/prefetch_related_examples.html', {
        'title': 'Релизы с prefetch_related()',
        'releases': releases,
        'description': 'Предзагрузка треков для релизов'
    })

def playlists_with_tracks(request):
    """Плейлисты с предзагруженными треками"""
    playlists = Playlist.objects.prefetch_related('tracks')[:10]
    
    return render(request, 'catalog/prefetch_related_examples.html', {
        'title': 'Плейлисты с prefetch_related()',
        'playlists': playlists,
        'description': 'Предзагрузка треков для плейлистов'
    })

# Комбинированный пример: select_related + prefetch_related
def optimized_tracks(request):
    """Треки с полной оптимизацией"""
    tracks = Track.objects.select_related('release', 'release__artist').prefetch_related('genres')[:10]
    
    return render(request, 'catalog/prefetch_related_examples.html', {
        'title': 'Полная оптимизация треков',
        'tracks': tracks,
        'description': 'select_related + prefetch_related вместе'
    })

# Сравнение производительности
def prefetch_performance_comparison(request):
    """Сравнение с и без prefetch_related()"""
    
    # БЕЗ оптимизации
    artists_slow = Artist.objects.all()[:5]
    
    # С оптимизацией
    artists_fast = Artist.objects.prefetch_related('releases')[:5]
    
    return render(request, 'catalog/prefetch_comparison.html', {
        'artists_slow': artists_slow,
        'artists_fast': artists_fast,
        'title': 'Сравнение prefetch_related()'
    })
    
    
    
    
# CRUD для треков с redirect()

def track_list(request):
    """Список треков"""
    tracks = Track.objects.select_related('release__artist').prefetch_related('genres')[:20]
    return render(request, 'catalog/crud/track_list.html', {
        'tracks': tracks,
        'title': 'Все треки'
    })

def track_create(request):
    """Создание трека с redirect после успеха"""
    if request.method == 'POST':
        title = request.POST.get('title')
        release_id = request.POST.get('release')
        duration_seconds = request.POST.get('duration_seconds')
        
        if title and release_id and duration_seconds:
            try:
                release = Release.objects.get(id=release_id)
                track = Track.objects.create(
                    title=title,
                    release=release,
                    duration_seconds=int(duration_seconds),
                    status='published'
                )
                messages.success(request, f'Трек "{track.title}" успешно создан!')
                # РЕДИРЕКТ на детальную страницу трека
                return redirect('track-detail', pk=track.pk)
            except Release.DoesNotExist:
                messages.error(request, 'Релиз не найден!')
        else:
            messages.error(request, 'Заполните все обязательные поля!')
    
    releases = Release.objects.all()
    return render(request, 'catalog/crud/track_form.html', {
        'title': 'Создать новый трек',
        'releases': releases,
        'action': 'create'
    })

def track_edit(request, pk):
    """Редактирование трека с redirect после успеха"""
    track = get_object_or_404(Track, pk=pk)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        duration_seconds = request.POST.get('duration_seconds')
        status = request.POST.get('status')
        
        if title and duration_seconds:
            track.title = title
            track.duration_seconds = int(duration_seconds)
            track.status = status
            track.save()
            
            messages.success(request, f'Трек "{track.title}" успешно обновлен!')
            # РЕДИРЕКТ на детальную страницу трека
            return redirect('track-detail', pk=track.pk)
        else:
            messages.error(request, 'Заполните все обязательные поля!')
    
    releases = Release.objects.all()
    return render(request, 'catalog/crud/track_form.html', {
        'title': f'Редактировать трек: {track.title}',
        'track': track,
        'releases': releases,
        'action': 'edit'
    })

def track_delete(request, pk):
    """Удаление трека с redirect после успеха"""
    track = get_object_or_404(Track, pk=pk)
    
    if request.method == 'POST':
        track_title = track.title
        track.delete()
        messages.success(request, f'Трек "{track_title}" успешно удален!')
        # РЕДИРЕКТ на список треков
        return redirect('track-list')
    
    return render(request, 'catalog/crud/track_confirm_delete.html', {
        'track': track,
        'title': f'Удалить трек: {track.title}'
    })

def track_detail(request, pk):
    """Детальная страница трека с обработкой 404"""
    track = get_object_or_404(
        Track.objects.select_related('release__artist').prefetch_related('genres'), 
        pk=pk
    )
    return render(request, 'catalog/crud/track_detail.html', {
        'track': track,
        'title': f'Трек: {track.title}'
    })

# CRUD для плейлистов с redirect()

def playlist_create(request):
    """Создание плейлиста с redirect"""
    if request.method == 'POST':
        title = request.POST.get('title')
        user_id = request.POST.get('user')
        is_public = request.POST.get('is_public') == 'on'
        
        if title and user_id:
            try:
                user = User.objects.get(id=user_id)
                playlist = Playlist.objects.create(
                    title=title,
                    user=user,
                    is_public=is_public
                )
                messages.success(request, f'Плейлист "{playlist.title}" создан!')
                # РЕДИРЕКТ на страницу редактирования плейлиста (чтобы добавить треки)
                return redirect('playlist-edit', pk=playlist.pk)
            except User.DoesNotExist:
                messages.error(request, 'Пользователь не найден!')
        else:
            messages.error(request, 'Заполните название плейлиста!')
    
    users = User.objects.all()
    return render(request, 'catalog/crud/playlist_form.html', {
        'title': 'Создать плейлист',
        'users': users,
        'action': 'create'
    })

def playlist_edit(request, pk):
    """Редактирование плейлиста с добавлением треков"""
    playlist = get_object_or_404(Playlist.objects.prefetch_related('tracks'), pk=pk)
    
    if request.method == 'POST':
        # Обработка изменения названия
        if 'update_playlist' in request.POST:
            title = request.POST.get('title')
            is_public = request.POST.get('is_public') == 'on'
            
            if title:
                playlist.title = title
                playlist.is_public = is_public
                playlist.save()
                messages.success(request, 'Плейлист обновлен!')
                return redirect('playlist-edit', pk=playlist.pk)
        
        # Обработка добавления трека
        elif 'add_track' in request.POST:
            track_id = request.POST.get('track')
            if track_id:
                try:
                    track = Track.objects.get(id=track_id)
                    playlist.tracks.add(track)
                    messages.success(request, f'Трек "{track.title}" добавлен в плейлист!')
                    # РЕДИРЕКТ на эту же страницу (чтобы продолжить редактирование)
                    return redirect('playlist-edit', pk=playlist.pk)
                except Track.DoesNotExist:
                    messages.error(request, 'Трек не найден!')
    
    tracks = Track.objects.all()
    available_tracks = tracks.exclude(id__in=playlist.tracks.values_list('id', flat=True))
    
    return render(request, 'catalog/crud/playlist_edit.html', {
        'playlist': playlist,
        'available_tracks': available_tracks,
        'title': f'Редактировать: {playlist.title}'
    })

def playlist_delete_track(request, pk, track_id):
    """Удаление трека из плейлиста с redirect"""
    playlist = get_object_or_404(Playlist, pk=pk)
    track = get_object_or_404(Track, pk=track_id)
    
    if request.method == 'POST':
        playlist.tracks.remove(track)
        messages.success(request, f'Трек "{track.title}" удален из плейлиста!')
        # РЕДИРЕКТ обратно на редактирование плейлиста
        return redirect('playlist-edit', pk=playlist.pk)
    
    return render(request, 'catalog/crud/playlist_confirm_remove_track.html', {
        'playlist': playlist,
        'track': track
    })
    
    
def artists_with_links(request):
    """Исполнители с социальными ссылками"""
    artists_with_links = Artist.objects.exclude(
        website=''
    ).exclude(
        spotify_url=''
    ).exclude(
        youtube_url=''
    )
    
    return render(request, 'catalog/artists_with_links.html', {
        'artists': artists_with_links,
        'title': 'Исполнители с социальными ссылками'
    })

def releases_on_spotify(request):
    """Релизы доступные в Spotify"""
    spotify_releases = Release.objects.exclude(spotify_url='')
    
    return render(request, 'catalog/releases_list.html', {
        'releases': spotify_releases,
        'title': 'Релизы в Spotify',
        'description': 'Релизы, доступные для прослушивания в Spotify'
    })

def artist_social_links(request, pk):
    """Страница со всеми ссылками исполнителя"""
    artist = get_object_or_404(Artist, pk=pk)
    
    # Собираем все непустые ссылки
    social_links = []
    if artist.website:
        social_links.append({'name': 'Официальный сайт', 'url': artist.website})
    if artist.spotify_url:
        social_links.append({'name': 'Spotify', 'url': artist.spotify_url})
    if artist.youtube_url:
        social_links.append({'name': 'YouTube', 'url': artist.youtube_url})
    
    return render(request, 'catalog/artist_social.html', {
        'artist': artist,
        'social_links': social_links,
        'title': f'Ссылки {artist.name}'
    })
    
def search_artists_contains(request):
    """Поиск исполнителей (регистрозависимый)"""
    query = request.GET.get('q', '')
    artists = None
    
    if query:
        artists = Artist.objects.filter(name__contains=query)  # ✅ __contains
    
    return render(request, 'catalog/search_results.html', {
        'query': query,
        'artists': artists,
        'search_type': 'artists_contains',
        'title': f'Поиск исполнителей: "{query}" (регистрозависимый)'
    })

def search_artists_icontains(request):
    """Поиск исполнителей (регистронезависимый)"""
    query = request.GET.get('q', '')
    artists = None
    
    if query:
        artists = Artist.objects.filter(name__icontains=query)  # ✅ __icontains
    
    return render(request, 'catalog/search_results.html', {
        'query': query,
        'artists': artists,
        'search_type': 'artists_icontains',
        'title': f'Поиск исполнителей: "{query}" (регистронезависимый)'
    })
def search_releases_description(request):
    """Поиск по описанию релизов"""
    query = request.GET.get('q', '')
    releases = None
    
    if query:
        releases = Release.objects.filter(
            Q(title__icontains=query) |
            Q(artist__name__icontains=query)
        )
    
    return render(request, 'catalog/search_results.html', {
        'query': query,
        'releases': releases,
        'search_type': 'releases',
        'title': f'Поиск релизов: "{query}"'
    })
    
    
def artists_values_demo(request):
    """Демонстрация values() - возвращает словари"""
    # ✅ values() - только нужные поля как словари
    artists_data = Artist.objects.values('id', 'name', 'created_at')[:10]
    
    return render(request, 'catalog/values_demo.html', {
        'data_type': 'values() - словари',
        'data': artists_data,
        'title': 'Демонстрация values()'
    })

def artists_values_list_demo(request):
    """Демонстрация values_list() - возвращает кортежи"""
    # values_list() - только нужные поля как кортежи
    artists_tuples = Artist.objects.values_list('id', 'name')[:10]
    
    # ✅ values_list(flat=True) - для одного поля
    artist_names = Artist.objects.values_list('name', flat=True)[:10]
    
    return render(request, 'catalog/values_demo.html', {
        'data_type': 'values_list() - кортежи',
        'data': artists_tuples,
        'flat_data': artist_names,
        'title': 'Демонстрация values_list()'
    })

def tracks_optimized_data(request):
    """Оптимизированная выборка данных о треках"""
    # ✅ values() с связанными полями - эффективно!
    tracks_data = Track.objects.select_related('release__artist').values(
        'id',
        'title', 
        'duration_seconds',
        'release__title',
        'release__artist__name'
    )[:15]
    
    return render(request, 'catalog/values_demo.html', {
        'data_type': 'values() с связанными полями',
        'data': tracks_data,
        'title': 'Оптимизированные данные треков'
    })

def genre_statistics_values(request):
    """Статистика по жанрам используя values() и аннотацию"""
    from django.db.models import Count
    
    # ✅ values() + annotate() для группировки
    genre_stats = Genre.objects.values('name').annotate(
        track_count=Count('tracks')
    ).order_by('-track_count')
    
    return render(request, 'catalog/values_demo.html', {
        'data_type': 'values() + annotate() для статистики',
        'data': genre_stats,
        'title': 'Статистика по жанрам'
    })
    
    
def bulk_update_tracks(request):
    """Массовое обновление треков используя update()"""
    if request.method == 'POST':
        # ✅ update() - массовое обновление статуса треков
        updated_count = Track.objects.filter(
            status='draft'
        ).update(
            status='published'
        )
        
        messages.success(request, f'✅ Опубликовано {updated_count} треков используя update()')
        return redirect('track-list')
    
    draft_tracks_count = Track.objects.filter(status='draft').count()
    
    return render(request, 'catalog/bulk_operations.html', {
        'action': 'update',
        'draft_tracks_count': draft_tracks_count,
        'title': 'Массовое обновление треков'
    })
    
    
def bulk_delete_old_tracks(request):
    """Массовое удаление старых треков используя delete()"""
    if request.method == 'POST':
        from django.utils import timezone
        from datetime import timedelta
        
        # ✅ delete() - массовое удаление старых треков
        month_ago = timezone.now() - timedelta(days=30)
        old_tracks = Track.objects.filter(
            status='archived',
            created_at__lt=month_ago
        )
        
        deleted_count = old_tracks.count()
        old_tracks.delete()  # ✅ delete() - массовое удаление
        
        messages.warning(request, f'🗑️ Удалено {deleted_count} архивных треков старше 30 дней используя delete()')
        return redirect('track-list')
    
    from django.utils import timezone
    from datetime import timedelta
    
    month_ago = timezone.now() - timedelta(days=30)
    old_tracks_count = Track.objects.filter(
        status='archived', 
        created_at__lt=month_ago
    ).count()
    
    return render(request, 'catalog/bulk_operations.html', {
        'action': 'delete',
        'old_tracks_count': old_tracks_count,
        'title': 'Массовое удаление треков'
    })
    
    
def homepage(request):
    """Главная страница музыкального каталога с виджетами"""
    
    # 1. ВИДЖЕТ: Новые релизы (последние 5)
    new_releases = Release.objects.select_related('artist').order_by('-id')[:5]
    
    # 2. ВИДЖЕТ: Избранные исполнители
    featured_artists = Artist.objects.filter(featured=True)[:4]
    
    # 3. ВИДЖЕТ: Популярные треки (по play_count)
    popular_tracks = Track.objects.select_related('release__artist').filter(
        play_count__gt=0
    ).order_by('-play_count')[:5]
    
    # 4. ВИДЖЕТ: Жанровая статистика (агрегатная функция COUNT)
    from django.db.models import Count
    genres_with_stats = Genre.objects.annotate(
        track_count=Count('tracks')
    ).order_by('-track_count')[:6]
    
    # 5. ВИДЖЕТ: Общая статистика (агрегатные функции)
    stats = {
        'total_artists': Artist.objects.count(),
        'total_tracks': Track.objects.count(),
        'total_releases': Release.objects.count(),
        'most_popular_track': Track.objects.order_by('-play_count').first(),
        'avg_track_duration': Track.objects.aggregate(
            avg_duration=Avg('duration_seconds')
        )['avg_duration']
    }
    
    context = {
        'new_releases': new_releases,
        'featured_artists': featured_artists,
        'popular_tracks': popular_tracks,
        'genres_with_stats': genres_with_stats,
        'stats': stats,
        'title': 'MusicCatalog - Ваш музыкальный гид'
    }
    
    return render(request, 'catalog/homepage.html', context)

def search(request):
    """Страница поиска по всему каталогу"""
    query = request.GET.get('q', '')
    results = {}
    
    if query:
        # Поиск по трекам
        results['tracks'] = Track.objects.filter(
            Q(title__icontains=query) | 
            Q(release__title__icontains=query)
        ).select_related('release__artist')[:10]
        
        # Поиск по исполнителям
        results['artists'] = Artist.objects.filter(
            Q(name__icontains=query) | 
            Q(biography__icontains=query)
        )[:10]
        
        # Поиск по релизам
        results['releases'] = Release.objects.filter(
            Q(title__icontains=query) |
            Q(artist__name__icontains=query)
        ).select_related('artist')[:10]
    
    context = {
        'query': query,
        'results': results,
        'has_results': any(results.values()),
        'title': f'Поиск: {query}'
    }
    
    return render(request, 'catalog/search.html', context)