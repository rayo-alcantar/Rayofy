# Rayofy

## Descripción

Rayofy es una aplicación de escritorio para gestionar tus playlists de Spotify. Puedes visualizar todas tus playlists, eliminarlas, y buscar nuevas canciones para añadir a tus playlists existentes.

## Composición

La aplicación está construida utilizando:

- Python
- wxPython para la interfaz gráfica
- Spotipy para interactuar con la API de Spotify

## Instalación de librerías

Para instalar las librerías necesarias, ejecuta los siguientes comandos:

```bash
pip install wxPython
pip install spotipy
## Obtener API de desarrollador de Spotify

1. Ve al [Dashboard de Desarrolladores de Spotify](https://developer.spotify.com/dashboard/applications).
2. Haz clic en 'Create an App'.
3. Llena la información requerida.
4. Una vez creada la app, obtendrás tu `CLIENT_ID` y `CLIENT_SECRET`.
5. Dichos datos deberás ingresarlo en un archivo .json, algo así:
```bash
{
    "CLIENT_ID": "ClientID",
    "CLIENT_SECRET": "Client_Secret"
}


## Funciones

- **Ver Playlists**: Muestra todas tus playlists de Spotify.
- **Eliminar Playlists**: Permite eliminar una playlist seleccionada.
- **Buscar Canciones**: Busca canciones en Spotify para añadir a una playlist seleccionada.
- **Copiar Enlace de Playlist**: Copia el enlace de la playlist seleccionada al portapapeles.

## Contacto

- Twitter: [x.com/@rayoalcantar](https://x.com/@rayoalcantar)
- Correo: rayoalcantar@gmail.com
