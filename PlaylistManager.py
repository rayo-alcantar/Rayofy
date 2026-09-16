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
        while results and results.get('next'):
            results = self.sp.next(results)
            if results:
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
            return True
        except Exception as e:
            self.update_status(f"Error al renombrar playlist: {e}")
            return False

    def delete_playlist(self, playlist_id):
        """ Elimina una playlist """
        try:
            self.sp.current_user_unfollow_playlist(playlist_id)
            self.update_status("Playlist eliminada con éxito.")
            return True
        except Exception as e:
            self.update_status(f"Error al eliminar playlist: {e}")
            return False

    def fetch_tracks_from_playlist(self, playlist_id):
        tracks = []
        try:
            results = self.sp.playlist_tracks(playlist_id)
            while results:
                for item in results.get('items', []):
                    track = item.get('track')
                    if not track:
                        continue
                    artists = track.get('artists', [])
                    artist = artists[0]['name'] if artists else 'Desconocido'
                    tracks.append({
                        'name': track.get('name', 'Desconocido'),
                        'artist': artist,
                        'id': track.get('id'),
                        'display': f"{track.get('name', 'Desconocido')} - {artist}"
                    })
                if results.get('next'):
                    results = self.sp.next(results)
                else:
                    results = None
        except Exception as e:
            self.update_status(f"Error al obtener canciones: {e}")
        return tracks

    def get_track_count(self, playlist_or_id):
        """ Obtiene el total de canciones leyendo de memoria si es un diccionario o consultando la API como fallback """
        if isinstance(playlist_or_id, dict):
            tracks = playlist_or_id.get('tracks', {})
            if isinstance(tracks, dict) and 'total' in tracks:
                return tracks['total']
        try:
            results = self.sp.playlist_tracks(playlist_or_id, fields='total')
            return results.get('total', 0)
        except Exception:
            return 0
    
    def copy_playlist_link(self, playlist_id):
        """ Copia el enlace de la playlist al portapapeles """
        try:
            playlist_url = f"https://open.spotify.com/playlist/{playlist_id}"
            pyperclip.copy(playlist_url)
            self.update_status("Enlace de playlist copiado al portapapeles.")
            return True
        except Exception as e:
            self.update_status(f"Error al copiar enlace al portapapeles: {e}")
            return False

    def delete_song_from_playlist(self, playlist_name, song_name):
        playlist_id = None
        for playlist in self.playlists:
            if playlist['name'] == playlist_name:
                playlist_id = playlist['id']
                break
        if not playlist_id:
            self.update_status(f"Playlist {playlist_name} no encontrada.")
            return False
        song_id = None
        results = self.sp.playlist_tracks(playlist_id)
        while results:
            for item in results.get('items', []):
                track = item.get('track')
                if not track:
                    continue
                artists = track.get('artists', [])
                artist = artists[0]['name'] if artists else 'Desconocido'
                if f"{track.get('name')} - {artist}" == song_name:
                    song_id = track.get('id')
                    break
            if song_id or not results.get('next'):
                break
            results = self.sp.next(results)

        if not song_id:
            self.update_status(f"Canción {song_name} no encontrada en la playlist.")
            return False
        try:
            self.sp.playlist_remove_all_occurrences_of_items(playlist_id, [f"spotify:track:{song_id}"])
            self.update_status(f"La canción {song_name} ha sido eliminada de la playlist {playlist_name}.")
            return True
        except Exception as e:
            self.update_status(f"Error al eliminar la canción de la playlist: {e}")
            return False

    def copy_song_link(self, playlist_name, song_name):
        playlist_id = None
        for playlist in self.playlists:
            if playlist['name'] == playlist_name:
                playlist_id = playlist['id']
                break
        if not playlist_id:
            self.update_status(f"Playlist {playlist_name} no encontrada.")
            return False
        song_id = None
        results = self.sp.playlist_tracks(playlist_id)
        while results:
            for item in results.get('items', []):
                track = item.get('track')
                if not track:
                    continue
                artists = track.get('artists', [])
                artist = artists[0]['name'] if artists else 'Desconocido'
                if f"{track.get('name')} - {artist}" == song_name:
                    song_id = track.get('id')
                    break
            if song_id or not results.get('next'):
                break
            results = self.sp.next(results)

        if not song_id:
            self.update_status(f"Canción {song_name} no encontrada en la playlist.")
            return False
        try:
            song_url = f"https://open.spotify.com/track/{song_id}"
            pyperclip.copy(song_url)
            self.update_status(f"El enlace de la canción {song_name} ha sido copiado al portapapeles.")
            return True
        except Exception as e:
            self.update_status(f"Error al copiar el enlace de la canción al portapapeles: {e}")
            return False

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

    def remove_duplicate_tracks(self, playlist_id):
        """ Encuentra canciones duplicadas manteniendo la primera ocurrencia y eliminando el resto """
        seen_uris = set()
        duplicates_to_remove = []

        try:
            results = self.sp.playlist_tracks(playlist_id)
            current_pos = 0
            while results:
                for item in results.get('items', []):
                    track = item.get('track')
                    if track and track.get('uri'):
                        uri = track['uri']
                        if uri in seen_uris:
                            duplicates_to_remove.append({'uri': uri, 'positions': [current_pos]})
                        else:
                            seen_uris.add(uri)
                    current_pos += 1
                if results.get('next'):
                    results = self.sp.next(results)
                else:
                    break

            if not duplicates_to_remove:
                return 0, "No se encontraron canciones duplicadas en esta playlist."

            total_duplicates = len(duplicates_to_remove)

            # Ordenar por posición descendente para que borrar desde el final no altere los índices previos
            duplicates_to_remove.sort(key=lambda x: x['positions'][0], reverse=True)

            # Lotes de hasta 100 items por llamada (límite de la API de Spotify)
            batch_size = 100
            for i in range(0, len(duplicates_to_remove), batch_size):
                batch = duplicates_to_remove[i:i + batch_size]
                self.sp.playlist_remove_specific_occurrences_of_items(playlist_id, batch)

            return total_duplicates, f"Se eliminaron {total_duplicates} canciones duplicadas exitosamente."
        except Exception as e:
            return -1, f"Error al eliminar duplicados: {e}"

    def copy_track_to_playlist(self, target_playlist_id, track_id):
        """ Añade una canción existente a otra playlist """
        try:
            self.sp.playlist_add_items(target_playlist_id, [f"spotify:track:{track_id}"])
            return True, "Canción copiada exitosamente."
        except Exception as e:
            return False, f"Error al copiar canción: {e}"

    def move_track_to_playlist(self, source_playlist_id, target_playlist_id, track_id):
        """ Mueve una canción de una playlist a otra """
        try:
            self.sp.playlist_add_items(target_playlist_id, [f"spotify:track:{track_id}"])
            self.sp.playlist_remove_all_occurrences_of_items(source_playlist_id, [f"spotify:track:{track_id}"])
            return True, "Canción movida exitosamente."
        except Exception as e:
            return False, f"Error al mover canción: {e}"