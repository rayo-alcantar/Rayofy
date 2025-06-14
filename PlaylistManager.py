# Importar biblioteca para el portapapeles
import pyperclip

class PlaylistManager:
    def __init__(self, spotify_instance):
        self.sp = spotify_instance
        self.playlists = []
        self.status_message = ""

    def update_status(self, message):
        """ Actualiza el estado de la operación """
        self.status_message = message

    def fetch_playlists(self):
        """ Obtiene todas las playlists del usuario """
        try:
            results = self.sp.current_user_playlists()
            if results:
                self.playlists = results.get('items', [])
                self.extend_playlists(results)
            else:
                self.update_status("No se pudieron obtener las playlists.")
        except Exception as e:
            self.update_status(f"Error al obtener playlists: {e}")

    def extend_playlists(self, results):
        """ Extiende la lista de playlists si hay más páginas """
        while results['next']:
            results = self.sp.next(results)
            self.playlists.extend(results.get('items', []))

    def get_playlist(self, index):
        """ Obtiene una playlist específica por su índice en la lista """
        try:
            return self.playlists[index]
        except IndexError:
            self.update_status("Índice de playlist fuera de rango.")
            return None

    def rename_playlist(self, playlist_id, new_name):
        """ Renombra una playlist """
        try:
            self.sp.playlist_change_details(playlist_id, name=new_name)
            self.update_status("Playlist renombrada con éxito.")
        except Exception as e:
            self.update_status(f"Error al renombrar playlist: {e}")

    def delete_playlist(self, playlist_id):
        """ Elimina una playlist """
        try:
            self.sp.playlist_unfollow(playlist_id)
        except Exception as e:
            self.update_status(f"Error al eliminar playlist: {e}")
    
    def fetch_tracks_from_playlist(self, playlist_id):
        tracks = []
        results = self.sp.playlist_tracks(playlist_id)
        for item in results['items']:
            track = item['track']
            # Guardar nombre y artista principal
            artist = track['artists'][0]['name'] if track['artists'] else 'Desconocido'
            tracks.append(f"{track['name']} - {artist}")
        return tracks

    def get_track_count(self, playlist_id):
        try:
            results = self.sp.playlist_tracks(playlist_id)
            return results['total']
        except Exception:
            return 0
    
    def copy_playlist_link(self, playlist_id):
        """ Copia el enlace de la playlist al portapapeles """
        try:
            playlist_url = f"https://open.spotify.com/playlist/{playlist_id}"
            pyperclip.copy(playlist_url)
            self.update_status("Enlace de playlist copiado al portapapeles.")
        except Exception as e:
            self.update_status(f"Error al copiar enlace al portapapeles: {e}")
    def delete_song_from_playlist(self, playlist_name, song_name):
        # Buscar la playlist por su nombre para obtener su ID
        playlist_id = None
        for playlist in self.playlists:
            if playlist['name'] == playlist_name:
                playlist_id = playlist['id']
                break
    
        if not playlist_id:
            self.update_status(f"Playlist {playlist_name} no encontrada.")
            return
        
        # Buscar la canción por su nombre para obtener su ID
        song_id = None
        results = self.sp.playlist_tracks(playlist_id)
        for item in results['items']:
            if item['track']['name'] == song_name:
                song_id = item['track']['id']
                break
        
        if not song_id:
            self.update_status(f"Canción {song_name} no encontrada en la playlist.")
            return
        
        # Eliminar la canción de la playlist
        try:
            self.sp.playlist_remove_all_occurrences_of_items(playlist_id, [song_id])
            self.update_status(f"La canción {song_name} ha sido eliminada de la playlist {playlist_name}.")
        except Exception as e:
            self.update_status(f"Error al eliminar la canción de la playlist: {e}")
    
    def copy_song_link(self, playlist_name, song_name):
        # Buscar la playlist por su nombre para obtener su ID
        playlist_id = None
        for playlist in self.playlists:
            if playlist['name'] == playlist_name:
                playlist_id = playlist['id']
                break
    
        if not playlist_id:
            self.update_status(f"Playlist {playlist_name} no encontrada.")
            return
        
        # Buscar la canción por su nombre para obtener su ID
        song_id = None
        results = self.sp.playlist_tracks(playlist_id)
        for item in results['items']:
            if item['track']['name'] == song_name:
                song_id = item['track']['id']
                break
        
        if not song_id:
            self.update_status(f"Canción {song_name} no encontrada en la playlist.")
            return
        
        # Copiar el enlace de la canción al portapapeles
        try:
            song_url = f"https://open.spotify.com/track/{song_id}"
            pyperclip.copy(song_url)
            self.update_status(f"El enlace de la canción {song_name} ha sido copiado al portapapeles.")
        except Exception as e:
            self.update_status(f"Error al copiar el enlace de la canción al portapapeles: {e}")
    def create_new_playlist(self, playlist_name):
        """ Crea una nueva playlist """
        if not playlist_name:
            self.update_status("El nombre de la playlist no puede estar vacío.")
            return False
    
        if len(playlist_name) > 100:  # Suponiendo que 100 caracteres es el máximo permitido por Spotify
            self.update_status("El nombre de la playlist es demasiado largo.")
            return False
    
        # Validación para evitar nombres duplicados
        existing_names = [playlist['name'] for playlist in self.playlists]
        if playlist_name in existing_names:
            self.update_status("Ya existe una playlist con ese nombre.")
            return False
    
        try:
            user = self.sp.current_user()
            self.sp.user_playlist_create(user['id'], playlist_name)
            self.update_status(f"Playlist {playlist_name} creada con éxito.")
            return True
        except Exception as e:
            self.update_status(f"Error al crear la playlist: {e}")
            return False