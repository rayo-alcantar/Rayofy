# Importación de bibliotecas
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
from spotipy.cache_handler import CacheFileHandler
import wx
import os
import json
import webbrowser

# Cargar CLIENT_ID y CLIENT_SECRET desde un archivo JSON
CLIENT_ID = None
CLIENT_SECRET = None

try:
    if os.path.exists('credentials.json'):
        with open('credentials.json', 'r') as f:
            credentials = json.load(f)
            CLIENT_ID = credentials.get('CLIENT_ID')
            CLIENT_SECRET = credentials.get('CLIENT_SECRET')
            
            if not CLIENT_ID or not CLIENT_SECRET:
                print("CLIENT_ID o CLIENT_SECRET no se encuentran en el archivo JSON.")
    else:
        print("El archivo credentials.json no se encuentra.")
except json.JSONDecodeError:
    print("Error al decodificar el archivo JSON. Asegúrate de que el archivo tenga el formato correcto.")
except Exception as e:
    print(f"Ocurrió un error inesperado al cargar las credenciales: {e}")
# Definición de constantes
REDIRECT_URI = "http://127.0.0.1:8080/"
SCOPE = "playlist-modify-public playlist-modify-private playlist-read-private playlist-read-collaborative"
SESSION_FILE = "user_session.json"

class SpotifyAuthenticator:
    def __init__(self):
        if not CLIENT_ID or not CLIENT_SECRET:
            raise ValueError("CLIENT_ID and CLIENT_SECRET must be provided in credentials.json")
        self.cache_handler = CacheFileHandler(cache_path=SESSION_FILE)
        self.sp_oauth = SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, 
                                     redirect_uri=REDIRECT_URI, scope=SCOPE,
                                     cache_handler=self.cache_handler)
        self.sp = None
        self.token_info = None
        self.load_user_session()

    def authenticate_api(self):
        if self.token_info:
            self.sp = spotipy.Spotify(auth_manager=self.sp_oauth)
        else:
            print("No se pudo autenticar la API. Asegúrate de tener un token válido.")

    def check_user_session_file(self):
        return os.path.exists(SESSION_FILE)

    def load_user_session(self):
        if self.check_user_session_file():
            self.token_info = self.cache_handler.get_cached_token()
            
            if self.token_info:
                # Verificar si los alcances (scopes) requeridos están presentes en el token guardado
                saved_scope = self.token_info.get('scope', '')
                required_scopes = set(SCOPE.split())
                saved_scopes = set(saved_scope.split())
                if not required_scopes.issubset(saved_scopes):
                    print("Los permisos guardados no coinciden con los requeridos. Re-autenticando...")
                    self.token_info = None
                    if os.path.exists(SESSION_FILE):
                        try:
                            os.remove(SESSION_FILE)
                        except Exception:
                            pass
                    self.get_user_permission()
                    return

                if self.sp_oauth.is_token_expired(self.token_info):
                    self.token_info = self.sp_oauth.refresh_access_token(self.token_info['refresh_token'])
                self.authenticate_api()
            else:
                self.get_user_permission()
        else:
            self.get_user_permission()

    def save_user_session(self):
        if self.token_info:
            self.cache_handler.save_token_to_cache(self.token_info)

    def get_user_permission(self):
        auth_url = self.sp_oauth.get_authorize_url()
        webbrowser.open(auth_url)
        try:
            redirect_response = input("Pega la URL completa a la que fuiste redirigido: ")
            code = self.sp_oauth.parse_response_code(redirect_response)
            self.token_info = self.sp_oauth.get_access_token(code)
            self.authenticate_api()
        except Exception as e:
            print(f"Error en la autorización: {e}")
            wx.MessageBox('Error en la autorización. Intente nuevamente.', 'Error', wx.OK | wx.ICON_ERROR)
