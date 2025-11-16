from django.urls import path
from . import views

urlpatterns = [
    
    
    # Примеры filter()
    path('releases/year/<int:year>/', views.releases_by_year, name='releases-by-year'),
    path('tracks/genre/<str:genre_name>/', views.tracks_by_genre, name='tracks-by-genre'),
    path('releases/popular/', views.popular_releases, name='popular-releases'),
    path('releases/digital/recent/', views.digital_recent_releases, name='digital-recent-releases'),
    
    # Примеры использования __
    path('artists-by-label/', views.artists_by_label, name='artists-by-label'),
    path('tracks-by-artist/', views.tracks_by_artist, name='tracks-by-artist'),
    path('search-tracks/', views.search_tracks, name='search-tracks'),
    path('recent-digital-tracks/', views.recent_digital_tracks, name='recent-digital-tracks'),
    path('artists-by-genre/', views.artists_by_genre, name='artists-by-genre'),
    
    
    # НОВЫЕ: Примеры exclude()
    path('tracks/without-genres/', views.tracks_without_genres, name='tracks-without-genres'),
    path('releases/without-label/', views.releases_without_label, name='releases-without-label'),
    path('tracks/non-digital/genre/<str:genre_name>/', views.non_digital_tracks_by_genre, name='non-digital-tracks-by-genre'),
    path('artists/without-releases/', views.artists_without_releases, name='artists-without-releases'),
    path('tracks/without-position/', views.tracks_without_position, name='tracks-without-position'),
    path('releases/old-non-digital/', views.old_non_digital_releases, name='old-non-digital-releases'),
    
    
    # НОВЫЕ: Примеры order_by() - всего 2 штуки
    path('tracks/order/duration/', views.tracks_by_duration, name='tracks-by-duration'),
    path('releases/order/year/', views.releases_by_year, name='releases-order-by-year'),
    
    
    
    # НОВЫЕ: Примеры кастомных менеджеров
    path('tracks/custom/long/', views.long_tracks, name='long-tracks'),
    path('releases/custom/digital/', views.digital_only_releases, name='digital-only-releases'),
    path('tracks/custom/recent-digital/', views.recent_digital_tracks, name='recent-digital-tracks'),
    
    
    # НОВЫЕ: Демонстрация get_absolute_url и reverse
    path('demonstrate-urls/', views.demonstrate_urls, name='demonstrate-urls'),
    path('artist/<int:pk>/', views.artist_detail, name='artist-detail'),
    path('release/<int:pk>/', views.release_detail, name='release-detail'),
    path('track/<int:pk>/', views.track_detail, name='track-detail'),
    
    
    # НОВЫЕ: Примеры агрегации и аннотации
    path('aggregation-examples/', views.aggregation_examples, name='aggregation-examples'),
    path('aggregation/artists-stats/', views.artists_with_stats, name='artists-stats'),
    path('aggregation/tracks-stats/', views.tracks_statistics, name='tracks-stats'),
    path('aggregation/genres-stats/', views.genres_with_track_count, name='genres-stats'),
    
    
    # НОВЫЕ: CRUD операции
    path('crud-examples/', views.crud_examples, name='crud-examples'),
    
    # CRUD для жанров
    path('genres/', views.genre_list, name='genre-list'),
    path('genres/create/', views.genre_create, name='genre-create'),
    path('genres/<int:pk>/', views.genre_detail, name='genre-detail'),
    path('genres/<int:pk>/edit/', views.genre_edit, name='genre-edit'),
    path('genres/<int:pk>/delete/', views.genre_delete, name='genre-delete'),
    
    
#    path('through-examples/', views.through_examples, name='through-examples'),
#    path('playlists-with-features/', views.playlists_with_features, name='playlists-with-features'),
#    path('playlist-with-features/<int:pk>/', views.playlist_detail_with_features, name='playlist-with-features'),
#    path('create-playlist/', views.create_playlist_with_tracks, name='create-playlist'),


    path('select-related/tracks/', views.tracks_with_releases, name='select-related-tracks'),
    path('select-related/releases/', views.releases_with_artists, name='select-related-releases'),
    path('select-related/playlists/', views.playlist_with_user, name='select-related-playlists'),
    path('select-related/comparison/', views.performance_comparison, name='select-related-comparison'),
    
    
    # Добавьте к существующим urlpatterns
path('prefetch-related/tracks/', views.tracks_with_genres, name='prefetch-related-tracks'),
path('prefetch-related/artists/', views.artists_with_releases, name='prefetch-related-artists'),
path('prefetch-related/releases/', views.releases_with_tracks, name='prefetch-related-releases'),
path('prefetch-related/playlists/', views.playlists_with_tracks, name='prefetch-related-playlists'),
path('prefetch-related/optimized/', views.optimized_tracks, name='prefetch-related-optimized'),
path('prefetch-related/comparison/', views.prefetch_performance_comparison, name='prefetch-related-comparison'),



# CRUD для треков
path('tracks/', views.track_list, name='track-list'),
path('tracks/create/', views.track_create, name='track-create'),
path('tracks/<int:pk>/', views.track_detail, name='track-detail'),
path('tracks/<int:pk>/edit/', views.track_edit, name='track-edit'),
path('tracks/<int:pk>/delete/', views.track_delete, name='track-delete'),

# CRUD для плейлистов  
path('playlists/create/', views.playlist_create, name='playlist-create'),
path('playlists/<int:pk>/edit/', views.playlist_edit, name='playlist-edit'),
path('playlists/<int:pk>/remove-track/<int:track_id>/', views.playlist_delete_track, name='playlist-remove-track'),


path('artists-with-links/', views.artists_with_links, name='artists-with-links'),
path('spotify-releases/', views.releases_on_spotify, name='spotify-releases'),
path('artist/<int:pk>/social/', views.artist_social_links, name='artist-social'),


# Поиск с __contains/__icontains
path('search/artists-contains/', views.search_artists_contains, name='search-artists-contains'),
path('search/artists-icontains/', views.search_artists_icontains, name='search-artists-icontains'),
path('search/releases/', views.search_releases_description, name='search-releases'),

# values() и values_list()
path('demo/values/', views.artists_values_demo, name='values-demo'),
path('demo/values-list/', views.artists_values_list_demo, name='values-list-demo'),
path('demo/tracks-optimized/', views.tracks_optimized_data, name='tracks-optimized'),
path('demo/genre-stats/', views.genre_statistics_values, name='genre-stats-values'),


# Массовые операции
path('tracks/bulk-update/', views.bulk_update_tracks, name='bulk-update-tracks'),
path('tracks/bulk-delete/', views.bulk_delete_old_tracks, name='bulk-delete-tracks'),

# Главная страница
path('', views.homepage, name='homepage'),
    
    # Поиск
path('search/', views.search, name='search'),

]
