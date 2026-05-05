# Importaciones para la interfaz gráfica
import sys
import wx
import os
import webbrowser
import pyperclip

sys.path.append('.')
from SpotifyAuthenticator import SpotifyAuthenticator
from PlaylistManager import PlaylistManager
from SearchFrame import SearchFrame

class Rayofy(wx.Frame):
    def __init__(self, spotify_authenticator, playlist_manager):
        super(Rayofy, self).__init__(None, title='Rayofy', size=(800, 600))

        self.spotify_authenticator = spotify_authenticator
        self.playlist_manager = playlist_manager

        # Iniciar la interfaz gráfica
        self.init_ui()

    def init_ui(self):
        # Crear un panel y un sizer vertical
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        # Crear un objeto wx.MenuBar
        menu_bar = wx.MenuBar()
        # Menú de ayuda para abrir el manual técnico
        help_menu = wx.Menu()
        open_manual_item = help_menu.Append(wx.ID_ANY, 'Manual técnico', 'Abrir manual técnico')
        self.Bind(wx.EVT_MENU, self.on_open_manual, open_manual_item)
        menu_bar.Append(help_menu, '&Ayuda')
        
        # Crear un objeto wx.Menu
        file_menu = wx.Menu()
        
        # Añadir un elemento de menú para "Crear Playlist"
        create_playlist_item = file_menu.Append(wx.ID_ANY, '&Crear Playlist\tCtrl+N', 'Crear una nueva Playlist')
        self.Bind(wx.EVT_MENU, self.on_create_playlist, create_playlist_item)
        
        # Añadir el menú a la barra de menús
        menu_bar.Append(file_menu, '&Acciones')
        
        # Establecer la barra de menús para la ventana
        self.SetMenuBar(menu_bar)
        
        # Crear el árbol de playlists
        self.tree = wx.TreeCtrl(panel, style=wx.TR_DEFAULT_STYLE | wx.TR_FULL_ROW_HIGHLIGHT)
        self.tree.SetToolTip("Navega con flechas. Pulsa la tecla de aplicaciones para más opciones.")
        self.tree.AddRoot('Playlists')
        
        self.refresh_playlists()
        
        # Vincular el evento de expansión del árbol
        self.tree.Bind(wx.EVT_TREE_ITEM_EXPANDING, self.on_tree_item_expanding)
        self.tree.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.on_tree_item_activated)
        # Vincular evento de teclado para menú contextual
        self.tree.Bind(wx.EVT_KEY_DOWN, self.on_tree_key_down)
        # F5 para refrescar playlists
        self.Bind(wx.EVT_KEY_DOWN, self.on_main_key_down)

        # Botón "Buscar"
        search_button = wx.Button(panel, label="&Buscar")
        search_button.Bind(wx.EVT_BUTTON, self.on_search_button_click)
        vbox.Add(self.tree, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)
        vbox.Add(search_button, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)

        panel.SetSizer(vbox)
        # Atajo de teclado Ctrl+N para crear playlist
        accel_tbl = wx.AcceleratorTable([(wx.ACCEL_CTRL, ord('N'), create_playlist_item.GetId())])
        self.SetAcceleratorTable(accel_tbl)

    def refresh_playlists(self):
        root = self.tree.GetRootItem()
        self.tree.DeleteChildren(root)
        self.playlist_manager.fetch_playlists()
        for playlist in self.playlist_manager.playlists:
            count = self.playlist_manager.get_track_count(playlist['id'])
            label = f"{playlist['name']} ({count})"
            playlist_item = self.tree.AppendItem(root, label)
            self.tree.SetItemData(playlist_item, playlist)
            self.tree.AppendItem(playlist_item, "Cargando...")

    def on_tree_item_expanding(self, event):
        item = event.GetItem()
        parent = self.tree.GetItemParent(item)
        if parent == self.tree.GetRootItem():
            playlist = self.tree.GetItemData(item)
            if playlist:
                self.tree.DeleteChildren(item)
                tracks = self.playlist_manager.fetch_tracks_from_playlist(playlist['id'])
                for track in tracks:
                    track_item = self.tree.AppendItem(item, track['display'])
                    self.tree.SetItemData(track_item, track)

    def on_create_playlist(self, event):
        dlg = wx.TextEntryDialog(self, 'Ingrese el nombre de la nueva playlist:', 'Crear Playlist')
        if dlg.ShowModal() == wx.ID_OK:
            playlist_name = dlg.GetValue().strip()
            if not playlist_name:
                wx.MessageBox('El nombre de la playlist no puede estar vacío.', 'Error', wx.OK | wx.ICON_ERROR)
                return
            try:
                if self.playlist_manager.create_new_playlist(playlist_name):
                    wx.MessageBox(f'Playlist {playlist_name} creada exitosamente.', 'Éxito', wx.OK | wx.ICON_INFORMATION)
                    self.refresh_playlists()
                else:
                    wx.MessageBox(f'Error al crear la playlist: {self.playlist_manager.status_message}', 'Error', wx.OK | wx.ICON_ERROR)
            except Exception as e:
                wx.MessageBox(f'Error al crear la playlist: {e}', 'Error', wx.OK | wx.ICON_ERROR)
        dlg.Destroy()

    def on_search_button_click(self, event):
        search_frame = SearchFrame(self.playlist_manager)
        search_frame.Show()

    def on_tree_item_activated(self, event):
        item = event.GetItem()
        parent = self.tree.GetItemParent(item)
        if parent == self.tree.GetRootItem():
            self.show_playlist_options(item)
        elif parent and parent != self.tree.GetRootItem():
            self.show_song_options(item)

    def on_tree_key_down(self, event):
        key = event.GetKeyCode()
        if key == wx.WXK_WINDOWS_MENU or key == 395: # Apps key
            item = self.tree.GetSelection()
            if item:
                parent = self.tree.GetItemParent(item)
                if parent == self.tree.GetRootItem():
                    self.show_playlist_options(item)
                elif parent:
                    self.show_song_options(item)
        else:
            event.Skip()

    def on_main_key_down(self, event):
        key = event.GetKeyCode()
        if key == wx.WXK_F5:
            self.refresh_playlists()
        else:
            event.Skip()

    def show_song_options(self, item):
        track = self.tree.GetItemData(item)
        parent_item = self.tree.GetItemParent(item)
        playlist = self.tree.GetItemData(parent_item)
        if not track or not playlist: return

        menu = wx.Menu()
        eliminar = menu.Append(wx.ID_ANY, 'Eliminar de playlist')
        copiar = menu.Append(wx.ID_ANY, 'Copiar enlace')
        
        def on_eliminar(evt):
            try:
                self.playlist_manager.sp.playlist_remove_all_occurrences_of_items(playlist['id'], [f"spotify:track:{track['id']}"])
                self.refresh_playlists()
            except Exception as e:
                wx.MessageBox(f'Error al eliminar canción: {e}', 'Error', wx.OK | wx.ICON_ERROR)
        
        def on_copiar(evt):
            url = f"https://open.spotify.com/track/{track['id']}"
            pyperclip.copy(url)
            wx.MessageBox('Enlace copiado al portapapeles.', 'Éxito', wx.OK | wx.ICON_INFORMATION)

        self.Bind(wx.EVT_MENU, on_eliminar, eliminar)
        self.Bind(wx.EVT_MENU, on_copiar, copiar)
        self.PopupMenu(menu)
        menu.Destroy()

    def show_playlist_options(self, item):
        playlist = self.tree.GetItemData(item)
        if not playlist: return

        menu = wx.Menu()
        editar = menu.Append(wx.ID_ANY, 'Editar nombre')
        eliminar = menu.Append(wx.ID_ANY, 'Eliminar playlist')
        copiar = menu.Append(wx.ID_ANY, 'Copiar enlace')
        
        def on_editar(evt):
            dlg = wx.TextEntryDialog(self, 'Nuevo nombre de la playlist:', 'Editar nombre', playlist['name'])
            if dlg.ShowModal() == wx.ID_OK:
                nuevo_nombre = dlg.GetValue().strip()
                if self.playlist_manager.rename_playlist(playlist['id'], nuevo_nombre):
                    self.refresh_playlists()
            dlg.Destroy()
        
        def on_eliminar(evt):
            dlg = wx.MessageDialog(self, f'¿Seguro que quieres eliminar la playlist "{playlist["name"]}"?', 'Confirmar eliminación', wx.YES_NO | wx.ICON_WARNING)
            if dlg.ShowModal() == wx.ID_YES:
                if self.playlist_manager.delete_playlist(playlist['id']):
                    self.refresh_playlists()
            dlg.Destroy()
        
        def on_copiar(evt):
            self.playlist_manager.copy_playlist_link(playlist['id'])
            wx.MessageBox('Enlace copiado al portapapeles.', 'Éxito', wx.OK | wx.ICON_INFORMATION)

        self.Bind(wx.EVT_MENU, on_editar, editar)
        self.Bind(wx.EVT_MENU, on_eliminar, eliminar)
        self.Bind(wx.EVT_MENU, on_copiar, copiar)
        self.PopupMenu(menu)
        menu.Destroy()

    def on_open_manual(self, event):
        manual_path = os.path.abspath('manual_tecnico.html')
        webbrowser.open(f'file://{manual_path}')

# Código para iniciar la aplicación
if __name__ == "__main__":
    app = wx.App(False)
    try:
        auth = SpotifyAuthenticator()
        playlist_manager = PlaylistManager(auth.sp)
        frame = Rayofy(auth, playlist_manager)
        frame.Show()
        app.MainLoop()
    except Exception as e:
        wx.MessageBox(f'Error al iniciar la aplicación: {e}', 'Error fatal', wx.OK | wx.ICON_ERROR)
