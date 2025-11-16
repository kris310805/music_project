# catalog/management/commands/fill_data.py
from django.core.management.base import BaseCommand
from catalog.models import Artist, Genre, Label, Release, Track
from django.contrib.auth.models import User
import random

class Command(BaseCommand):
    help = 'Fill database with sample music data'
    
    def handle(self, *args, **options):
        self.stdout.write("Starting to fill database...")
        
        # Очистка старых данных (в правильном порядке из-за ForeignKey)
        Track.objects.all().delete()
        Release.objects.all().delete()
        Artist.objects.all().delete()
        Genre.objects.all().delete()
        Label.objects.all().delete()
        
        # Создание жанров
        genres = []
        genre_names = ['Rock', 'Pop', 'Hip-Hop', 'Jazz', 'Electronic', 'Classical', 'Country', 'R&B']
        for name in genre_names:
            genre = Genre.objects.create(
                name=name, 
                description=f'Описание жанра {name}'
            )
            genres.append(genre)
            self.stdout.write(f'✓ Created genre: {name}')
        
        # Создание лейблов
        labels = []
        label_names = ['Sony Music', 'Universal Music', 'Warner Music', 'Independent']
        for name in label_names:
            label = Label.objects.create(
                name=name, 
                description=f'Лейбл {name}',
                founded_year=random.randint(1950, 2000)
            )
            labels.append(label)
            self.stdout.write(f'✓ Created label: {name}')
        
        # Создание исполнителей
        artists = []
        artist_names = [
            'Arctic Monkeys', 'Taylor Swift', 'Kendrick Lamar', 'Norah Jones',
            'Daft Punk', 'Beethoven', 'Johnny Cash', 'Beyoncé',
            'The Beatles', 'Radiohead', 'Adele', 'Drake'
        ]
        
        for name in artist_names:
            artist = Artist.objects.create(
                name=name,
                biography=f'Биография исполнителя {name}. Известный музыкант в своем жанре.',
                featured=random.choice([True, False]),
                popularity_score=random.randint(0, 100)
            )
            artists.append(artist)
            self.stdout.write(f'✓ Created artist: {name}')
        
        # Создание релизов
        releases = []
        release_titles = [
            'Midnight Memories', 'Summer Vibes', 'Urban Dreams', 'Ocean Waves',
            'Mountain Echo', 'Desert Wind', 'Forest Whisper', 'River Flow',
            'Digital Age', 'Analog Soul', 'Future Vision', 'Past Reflections'
        ]
        
        for i, title in enumerate(release_titles):
            artist = random.choice(artists)
            label = random.choice(labels)
            
            release_data = {
                'title': title,
                'artist': artist,
                'label': label,
                'format': random.choice(['Digital', 'CD', 'Vinyl']),
                'release_year': random.randint(2018, 2024),
                'featured': random.choice([True, False]),
                'is_premium': random.choice([True, False])
            }
            
            release = Release.objects.create(**release_data)
            releases.append(release)
            self.stdout.write(f'✓ Created release: {release.title} by {artist.name}')
        
        # Создание треков
        track_titles = [
            'Golden Sunrise', 'Starry Night', 'Electric Storm', 'Silent Rain',
            'Neon Lights', 'Acoustic Morning', 'Digital Love', 'Analog Dreams',
            'City Pulse', 'Country Road', 'Cosmic Journey', 'Earth Song'
        ]
        
        for i, title in enumerate(track_titles):
            release = random.choice(releases)
            
            track_data = {
                'title': title,
                'release': release,
                'duration_seconds': random.randint(180, 300),
                'position': f"{random.choice(['A', 'B'])}{random.randint(1, 6)}",
                'status': random.choice(['draft', 'published', 'published']),
                'play_count': random.randint(0, 5000),
                'featured': random.choice([True, False])
            }
            
            track = Track.objects.create(**track_data)
            
            # Добавляем случайные жанры к треку
            track_genres = random.sample(genres, random.randint(1, 2))
            track.genres.set(track_genres)
            
            self.stdout.write(f'✓ Created track: {track.title}')
        
        # Делаем некоторых исполнителей и треки популярными для главной страницы
        self.make_popular_content()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎵 Successfully filled database with:\n'
                f'   • {Artist.objects.count()} artists\n'
                f'   • {Genre.objects.count()} genres\n' 
                f'   • {Label.objects.count()} labels\n'
                f'   • {Release.objects.count()} releases\n'
                f'   • {Track.objects.count()} tracks'
            )
        )
    
    def make_popular_content(self):
        """Делаем контент популярным для виджетов главной страницы"""
        self.stdout.write("\nMaking popular content for homepage widgets...")
        
        # 4 избранных исполнителя
        featured_artists = Artist.objects.all()[:4]
        for artist in featured_artists:
            artist.featured = True
            artist.popularity_score = random.randint(80, 100)
            artist.save()
            self.stdout.write(f'⭐ Featured artist: {artist.name}')
        
        # 5 популярных треков
        popular_tracks = Track.objects.all()[:5]
        for track in popular_tracks:
            track.play_count = random.randint(1000, 10000)
            track.featured = True
            track.save()
            self.stdout.write(f'🔥 Popular track: {track.title} ({track.play_count} plays)')
        
        # 3 избранных релиза
        featured_releases = Release.objects.all()[:3]
        for release in featured_releases:
            release.featured = True
            release.save()
            self.stdout.write(f'🎵 Featured release: {release.title}')