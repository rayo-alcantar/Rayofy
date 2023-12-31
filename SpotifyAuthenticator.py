﻿# Importación de bibliotecas
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
import wx
import os
import json
import webbrowser

# Cargar CLIENT_ID y CLIENT_SECRET desde un archivo JSON
try:
    with open('credentials.json', 'r') as f:
        credentials = json.load(f)
        CLIENT_ID = credentials.get('CLIENT_ID')
        CLIENT_SECRET = credentials.get('CLIENT_SECRET')
        
        if not CLIENT_ID or not CLIENT_SECRET:
            print("CLIENT_ID o CLIENT_SECRET no se encuentran en el archivo JSON.")
except FileNotFoundError:
    print("El archivo credentials.json no se encuentra.")
except json.JSONDecodeError:
    print("Error al decodificar el archivo JSON. Asegúrate de que el archivo tenga el formato correcto.")
except Exception as e:
    print(f"Ocurrió un error inesperado: {e}")
# Definición de constantes
REDIRECT_URI = "http://localhost/"
SCOPE = "playlist-modify-public playlist-modify-private"
SESSION_FILE = "user_session.json"

class SpotifyAuthenticator:
    def __init__(self):
        self.sp_oauth = SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, 
                                     redirect_uri=REDIRECT_URI, scope=SCOPE)
        self.sp = None
        self.token_info = None
        self.load_user_session()

    def authenticate_api(self):
        if self.token_info:
            self.sp = spotipy.Spotify(auth=self.token_info['access_token'])
        else:
            print("No se pudo autenticar la API. Asegúrate de tener un token válido.")

    def check_user_session_file(self):
        return os.path.exists(SESSION_FILE)

    def load_user_session(self):
        if self.check_user_session_file():
            with open(SESSION_FILE, 'r') as f:
                self.token_info = json.load(f)
            if self.sp_oauth.is_token_expired(self.token_info):
                self.token_info = self.sp_oauth.refresh_access_token(self.token_info['refresh_token'])
                self.save_user_session()
            self.authenticate_api()
        else:
            self.get_user_permission()

    def save_user_session(self):
        with open(SESSION_FILE, 'w') as f:
            json.dump(self.token_info, f)

    def get_user_permission(self):
        auth_url = self.sp_oauth.get_authorize_url()
        webbrowser.open(auth_url)
        try:
            redirect_response = input("Pega la URL completa a la que fuiste redirigido: ")
            code = self.sp_oauth.parse_response_code(redirect_response)
            self.token_info = self.sp_oauth.get_access_token(code)
            self.save_user_session()
            self.authenticate_api()
        except Exception as e:
            print(f"Error en la autorización: {e}")
            wx.MessageBox('Error en la autorización. Intente nuevamente.', 'Error', wx.OK | wx.ICON_ERROR)
