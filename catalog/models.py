from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

from django.contrib import admin


from django.core.validators import FileExtensionValidator

# Кастомные модельные менеджеры

class TrackManager(models.Manager):
    """Кастомный менеджер для модели Track"""
    
    def long_tracks(self):
        """Возвращает треки длительностью более 4 минут"""
        return self.filter(duration_seconds__gt=240)
    
    def with_genre(self, genre_name):
        """Возвращает треки определенного жанра"""
        return self.filter(genres__name=genre_name)

class ReleaseManager(models.Manager):
    """Кастомный менеджер для модели Release"""
    
    def digital_only(self):
        """Возвращает только цифровые релизы"""
        return self.filter(format='Digital')
    
    def recent_releases(self, years=2):
        """Возвращает релизы за последние N лет"""
        from django.utils import timezone
        current_year = timezone.now().year
        return self.filter(release_year__gte=current_year - years)

# Исполнитель (певцы, группы)
class Artist(models.Model):
    name = models.CharField(
        max_length=200, 
        verbose_name="Имя исполнителя"
    )
    biography = models.TextField(
        blank=True, 
        null=True,
        verbose_name="Биография"
    )
    image = models.ImageField(
        upload_to='artists/',
        blank=True, 
        null=True,
        verbose_name="Фото исполнителя"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    
    
    
     # ✅ ДОБАВЛЯЕМ URLField ДЛЯ ССЫЛОК
    website = models.URLField(
        blank=True,
        verbose_name="Официальный сайт",
        help_text="Например: https://artistname.com"
    )
    
    spotify_url = models.URLField(
        blank=True, 
        verbose_name="Spotify",
        help_text="Например: https://open.spotify.com/artist/..."
    )
    
    youtube_url = models.URLField(
        blank=True,
        verbose_name="YouTube канал", 
        help_text="Например: https://youtube.com/c/artistname"
    )
    
    featured = models.BooleanField(default=False, verbose_name="Рекомендуемый")
    popularity_score = models.IntegerField(default=0, verbose_name="Популярность")
    
    class Meta:
        verbose_name = "Исполнитель"
        verbose_name_plural = "Исполнители"
        ordering = ['name']

    def __str__(self):
        return self.name
    
    # ✅ ДОБАВЛЯЕМ МЕТОД ДЛЯ ПРОВЕРКИ ССЫЛОК
    def has_social_links(self):
        """Проверяет, есть ли у исполнителя социальные ссылки"""
        return any([self.website, self.spotify_url, self.youtube_url])
    has_social_links.boolean = True
    has_social_links.short_description = "Есть соц. ссылки"
    
    def get_absolute_url(self):
        """URL для детальной страницы исполнителя"""
        from django.urls import reverse #перенести наверх
        return reverse('artist-detail', kwargs={'pk': self.pk})

# Музыкальный лейбл (студия звукозаписи)
class Label(models.Model):
    name = models.CharField(
        max_length=200, 
        verbose_name="Название лейбла"
    )
    description = models.TextField(
        blank=True, 
        null=True,
        verbose_name="Описание"
    )
    founded_year = models.IntegerField(
        blank=True, 
        null=True,
        verbose_name="Год основания"
    )

    class Meta:
        verbose_name = "Лейбл"
        verbose_name_plural = "Лейблы"
        ordering = ['name']

    def __str__(self):
        return self.name

# Музыкальные жанры
class Genre(models.Model):
    name = models.CharField(
        max_length=100, 
        verbose_name="Название жанра"
    )
    description = models.TextField(
        blank=True, 
        null=True,
        verbose_name="Описание жанра"
    )

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"
        ordering = ['name']

    def __str__(self):
        return self.name

# Альбом или сингл
class Release(models.Model):
    FORMAT_CHOICES = [
        ('Digital', 'Цифровой'),
        ('CD', 'CD'),
        ('Vinyl', 'Винил'),
        ('Cassette', 'Кассета'),
    ]

    title = models.CharField(
        max_length=300, 
        verbose_name="Название релиза"
    )
    artist = models.ForeignKey(
        Artist,
        on_delete=models.CASCADE,
        related_name='releases',
        verbose_name="Исполнитель"
    )
    label = models.ForeignKey(
        Label,
        on_delete=models.SET_NULL,
        blank=True, 
        null=True,
        related_name='releases',
        verbose_name="Лейбл"
    )
    format = models.CharField(
        max_length=20,
        choices=FORMAT_CHOICES,
        default='Digital',
        verbose_name="Формат"
    )
    release_year = models.IntegerField(
        verbose_name="Год выпуска"
    )
    cover_image = models.ImageField(
        upload_to='covers/',
        blank=True, 
        null=True,
        verbose_name="Обложка релиза"
    )
    
    # ✅ ДОБАВЛЯЕМ URLField ДЛЯ СТРИМИНГА
    spotify_url = models.URLField(
        blank=True,
        verbose_name="Spotify",
        help_text="Ссылка на релиз в Spotify"
    )
    
    apple_music_url = models.URLField(
        blank=True,
        verbose_name="Apple Music",
        help_text="Ссылка на релиз в Apple Music" 
    )
    
    bandcamp_url = models.URLField(
        blank=True,
        verbose_name="Bandcamp",
        help_text="Ссылка на релиз в Bandcamp"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()  # Стандартный менеджер  
    custom = ReleaseManager()   # Кастомный менеджер
    
    featured = models.BooleanField(default=False, verbose_name="Рекомендуемый релиз")
    is_premium = models.BooleanField(default=False, verbose_name="Премиум релиз")
    
    
    class Meta:
        verbose_name = "Релиз"
        verbose_name_plural = "Релизы"
        ordering = ['-release_year', 'title']

    def __str__(self):
        return f"{self.title} - {self.artist.name}"
    
    
    def is_new(self):
        """Проверяет是新 ли релиз (до 30 дней)"""
        from django.utils import timezone
        thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
        return self.created_at >= thirty_days_ago
    is_new.boolean = True
    is_new.short_description = "Новинка"
    
    
    def get_absolute_url(self):
        """URL для детальной страницы релиза"""
        from django.urls import reverse
        return reverse('release-detail', kwargs={'pk': self.pk})
    
    def has_streaming_links(self):
        """Проверяет, есть ли ссылки на стриминговые сервисы"""
        return any([self.spotify_url, self.apple_music_url, self.bandcamp_url])
    has_streaming_links.boolean = True
    has_streaming_links.short_description = "Есть стриминг"
    

# Отдельная песня/трек
class Track(models.Model):
    title = models.CharField(
        max_length=300, 
        verbose_name="Название трека"
    )
    release = models.ForeignKey(
        Release,
        on_delete=models.CASCADE,
        related_name='tracks',
        verbose_name="Релиз"
    )
    duration_seconds = models.IntegerField(
        verbose_name="Длительность в секундах"
    )
    position = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="Позиция (A1, B2)"
    )
    genres = models.ManyToManyField(
        Genre,
        blank=True,
        related_name='tracks',
        verbose_name="Жанры"
    )
    
    
    audio_file = models.FileField(
        upload_to='tracks/audio/',
        blank=True,
        null=True,
        verbose_name="Аудиофайл",
        validators=[FileExtensionValidator(allowed_extensions=['mp3', 'wav', 'ogg', 'm4a'])]
    )
    
    # ДОБАВЛЯЕМ LYRICS FILE FIELD
    lyrics_file = models.FileField(
        upload_to='tracks/lyrics/',
        blank=True,
        null=True,
        verbose_name="Текст песни (файл)",
        validators=[FileExtensionValidator(allowed_extensions=['txt', 'pdf', 'doc', 'docx'])]
    )
    
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('published', 'Опубликован'),
        ('archived', 'В архиве'),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name="Статус трека"
    )

    objects = models.Manager()  # Стандартный менеджер
    custom = TrackManager()     # Кастомный менеджер
    
    play_count = models.IntegerField(default=0, verbose_name="Количество прослушиваний")
    featured = models.BooleanField(default=False, verbose_name="Рекомендуемый трек")

    
    class Meta:
        verbose_name = "Трек"
        verbose_name_plural = "Треки"
        ordering = ['release', 'position']

    def __str__(self):
        return f"{self.title} - {self.release.artist.name}"
    
    def added_recently(self):
        """Проверяет добавлен ли трек за последние 7 дней"""
        from django.utils import timezone
        week_ago = timezone.now() - timezone.timedelta(days=7)
        return self.created_at >= week_ago
    added_recently.boolean = True
    added_recently.short_description = "Добавлен недавно"
    
    
    def get_duration(self):
        """Форматированная длительность трека"""
        minutes = self.duration_seconds // 60
        seconds = self.duration_seconds % 60
        return f"{minutes}:{seconds:02d}"
    
    
    def get_absolute_url(self):
        """URL для детальной страницы трека"""
        from django.urls import reverse
        return reverse('track-detail', kwargs={'pk': self.pk})
    
    # ДОБАВЛЯЕМ МЕТОД ДЛЯ ОТОБРАЖЕНИЯ АУДИО
    def get_audio_url(self):
        """Возвращает URL аудиофайла"""
        if self.audio_file:
            return self.audio_file.url
        return None
    
    def has_audio(self):
        """Проверяет, есть ли аудиофайл"""
        return bool(self.audio_file)
    has_audio.boolean = True
    has_audio.short_description = "Есть аудио"
    
    def has_lyrics(self):
        """Проверяет, есть ли файл с текстом"""
        return bool(self.lyrics_file)
    has_lyrics.boolean = True
    has_lyrics.short_description = "Есть текст"
    

# Плейлист пользователя
class Playlist(models.Model):
    title = models.CharField(
        max_length=200, 
        verbose_name="Название плейлиста"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='playlists',
        verbose_name="Пользователь"
    )
    tracks = models.ManyToManyField(
        Track,
        #through='TrackFeature',
        #through_fields=('playlist', 'track'),
        blank=True,
        related_name='playlists',
        verbose_name="Треки"
    )
    is_public = models.BooleanField(
        default=False,
        verbose_name="Публичный"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Плейлист"
        verbose_name_plural = "Плейлисты"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.user.username})"
    
    @admin.display(description="Треков")
    def track_count(self):
        return self.tracks.count()

    @admin.display(description="Общая длительность")
    def total_duration(self):
        total_seconds = sum(track.duration_seconds for track in self.tracks.all())
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes}м {seconds}с"
# История прослушиваний
class Scrobble(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='scrobbles',
        verbose_name="Пользователь"
    )
    track = models.ForeignKey(
        Track,
        on_delete=models.CASCADE,
        related_name='scrobbles',
        verbose_name="Трек"
    )
    scrobbled_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Время прослушивания"
    )

    class Meta:
        verbose_name = "Прослушивание"
        verbose_name_plural = "Прослушивания"
        ordering = ['-scrobbled_at']

    def __str__(self):
        return f"{self.user.username} - {self.track.title}"
    
    def listened_today(self):
        """Проверяет было ли прослушивание сегодня"""
        from django.utils import timezone
        today = timezone.now().date()
        return self.scrobbled_at.date() == today
    listened_today.boolean = True
    listened_today.short_description = "Сегодня"
    
    
    
# Промежуточная модель для связи ManyToMany с дополнительными полями
#class TrackFeature(models.Model):
#    """Дополнительная информация о треке в плейлисте"""
#    playlist = models.ForeignKey('Playlist', on_delete=models.CASCADE)
#    track = models.ForeignKey('Track', on_delete=models.CASCADE)
#    added_by = models.ForeignKey(
#       User, 
#        on_delete=models.CASCADE,
#        verbose_name="Добавил пользователь"
#    )
#    added_at = models.DateTimeField(auto_now_add=True)
#    position = models.IntegerField(
#        verbose_name="Позиция в плейлисте",
#        help_text="Порядковый номер трека в плейлисте"
#    )
#    note = models.TextField(
#        blank=True,
#        verbose_name="Заметка о треке",
#        help_text="Почему этот трек добавлен в плейлист"
#    )
#
#    class Meta:
#        verbose_name = "Трек в плейлисте"
#        verbose_name_plural = "Треки в плейлистах"
#        ordering = ['playlist', 'position']
#        unique_together = ['playlist', 'track']  # Один трек может быть только один раз в плейлисте
#
#    def __str__(self):
#        return f"{self.track.title} в {self.playlist.title} (позиция {self.position})"

# ДОБАВЛЯЕМ НОВУЮ МОДЕЛЬ ДЛЯ ДОКУМЕНТОВ
class Document(models.Model):
    """Модель для хранения документов связанных с музыкой"""
    DOCUMENT_TYPES = [
        ('contract', 'Контракт'),
        ('license', 'Лицензия'),
        ('sheet_music', 'Ноты'),
        ('chords', 'Аккорды'),
        ('other', 'Другое'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="Название документа")
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES, default='other', verbose_name="Тип документа")
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='documents', verbose_name="Исполнитель")
    
    # FILE FIELD для документа
    file = models.FileField(
        upload_to='documents/',
        verbose_name="Файл документа",
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'txt', 'jpg', 'png'])]
    )
    
    description = models.TextField(blank=True, verbose_name="Описание")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Документ"
        verbose_name_plural = "Документы"
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.title} - {self.artist.name}"
    
    def get_file_extension(self):
        """Возвращает расширение файла"""
        if self.file:
            return self.file.name.split('.')[-1].upper()
        return ""
    
    def get_file_size(self):
        """Возвращает размер файла в МБ"""
        if self.file:
            return f"{self.file.size / 1024 / 1024:.2f} MB"
        return "0 MB"
    

# НОВАЯ МОДЕЛЬ - Рейтинги и отзывы
class Review(models.Model):
    RATING_CHOICES = [
        (1, '1 - Плохо'),
        (2, '2 - Неплохо'),
        (3, '3 - Хорошо'),
        (4, '4 - Очень хорошо'),
        (5, '5 - Отлично'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    track = models.ForeignKey(Track, on_delete=models.CASCADE, verbose_name="Трек")
    rating = models.IntegerField(choices=RATING_CHOICES, verbose_name="Оценка")
    comment = models.TextField(blank=True, verbose_name="Комментарий")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        unique_together = ['user', 'track']  # Один отзыв на трек от пользователя
    
    def __str__(self):
        return f"{self.user.username} - {self.track.title} ({self.rating}/5)"

# НОВАЯ МОДЕЛЬ - Избранное
class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    track = models.ForeignKey(Track, on_delete=models.CASCADE, verbose_name="Трек")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранные треки"
        unique_together = ['user', 'track']
    
    def __str__(self):
        return f"{self.user.username} - {self.track.title}"