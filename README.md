# Rayofy

## Descripción

Rayofy es una aplicación de escritorio accesible para gestionar tus playlists de Spotify. Permite visualizar, buscar, editar, eliminar y copiar enlaces de tus playlists, así como buscar y añadir canciones de forma eficiente.

## Características principales

- **Ver Playlists**: Visualiza todas tus playlists de Spotify en un árbol interactivo.
- **Eliminar Playlists**: Elimina playlists con confirmación y accesibilidad por teclado.
- **Editar nombre de Playlist**: Cambia el nombre de cualquier playlist fácilmente.
- **Buscar Canciones**: Busca canciones por nombre y artista, y añádelas a cualquier playlist.
- **Copiar Enlace de Playlist**: Copia el enlace de la playlist seleccionada al portapapeles.
- **Menús contextuales**: Acciones rápidas sobre playlists y canciones usando la tecla de aplicaciones.
- **Refresco rápido**: Pulsa F5 para actualizar la lista de playlists.
- **Accesibilidad**: Navegación y acciones completamente accesibles por teclado.

## Instalación de librerías

Instala las dependencias ejecutando:

```bash
pip install wxPython spotipy pyperclip
```

## Configuración de credenciales de Spotify

1. Ve al [Dashboard de Desarrolladores de Spotify](https://developer.spotify.com/dashboard/applications).
2. Haz clic en 'Create an App'.
3. Llena la información requerida.
4. Obtén tu `CLIENT_ID` y `CLIENT_SECRET`.
5. Crea un archivo `credentials.json` en la raíz del proyecto con este formato:

```json
{
    "CLIENT_ID": "tu_client_id",
    "CLIENT_SECRET": "tu_client_secret"
}
```

## Uso

- Ejecuta `Rayofy.py` para iniciar la aplicación.
- Usa el teclado para navegar y acceder a todas las funciones.
- Pulsa la tecla de aplicaciones sobre una playlist o canción para ver las opciones disponibles.
- Pulsa F5 para refrescar la lista de playlists.

## Contacto

- Twitter: [x.com/@rayoalcantar](https://x.com/@rayoalcantar)
- Correo: rayoalcantar@gmail.com
