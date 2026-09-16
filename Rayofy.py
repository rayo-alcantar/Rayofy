# Importaciones para la interfaz gráfica
import sys
import wx
import os
import webbrowser
import pyperclip
import threading

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
        self.tree.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.on_tree_item_right_click)
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
        self.tree.AppendItem(root, "Cargando playlists...")
        
        def _worker():
            self.playlist_manager.fetch_playlists()
            wx.CallAfter(self._populate_playlists_tree, root)

        threading.Thread(target=_worker, daemon=True).start()

    def _populate_playlists_tree(self, root):
        if not self:
            return
        self.tree.DeleteChildren(root)
        for playlist in self.playlist_manager.playlists:
            count = self.playlist_manager.get_track_count(playlist)
            is_collab = playlist.get('collaborative', False)
            tag = " [Colaborativa]" if is_collab else ""
            label = f"{playlist['name']}{tag} ({count})"
            playlist_item = self.tree.AppendItem(root, label)
            self.tree.SetItemData(playlist_item, playlist)
            self.tree.AppendItem(playlist_item, "Cargando...")

    def on_tree_item_expanding(self, event):
        item = event.GetItem()
        parent = self.tree.GetItemParent(item)
        if parent == self.tree.GetRootItem():
            playlist = self.tree.GetItemData(item)
            if playlist:
                child, cookie = self.tree.GetFirstChild(item)
                if child.IsOk() and self.tree.GetItemText(child) == "Cargando...":
                    def _worker():
                        tracks = self.playlist_manager.fetch_tracks_from_playlist(playlist['id'])
                        wx.CallAfter(self._populate_tracks_tree, item, tracks)

                    threading.Thread(target=_worker, daemon=True).start()

    def _populate_tracks_tree(self, item, tracks):
        if not self:
            return
        self.tree.DeleteChildren(item)
        if not tracks:
            self.tree.AppendItem(item, "(Sin canciones)")
            return
        for track in tracks:
            track_item = self.tree.AppendItem(item, track['display'])
            self.tree.SetItemData(track_item, track)

    def on_create_playlist(self, event):
        dlg = wx.TextEntryDialog(self, 'Ingrese el nombre de la nueva playlist:', 'Crear Playlist')
        if dlg.ShowModal() == wx.ID_OK:
            playlist_name = dlg.GetValue().strip()
            dlg.Destroy()
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
        else:
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
            track = self.tree.GetItemData(item)
            if track:
                self.play_or_open_track(track['id'])

    def on_tree_item_right_click(self, event):
        item = event.GetItem()
        if item.IsOk():
            self.tree.SelectItem(item)
            parent = self.tree.GetItemParent(item)
            if parent == self.tree.GetRootItem():
                self.show_playlist_options(item)
            elif parent:
                self.show_song_options(item)

    def play_or_open_track(self, track_id):
        """ Reproduce vía Web API o abre en la app de escritorio de Spotify """
        try:
            self.playlist_manager.sp.start_playback(uris=[f"spotify:track:{track_id}"])
            return
        except Exception:
            pass

        try:
            os.startfile(f"spotify:track:{track_id}")
        except Exception:
            webbrowser.open(f"https://open.spotify.com/track/{track_id}")

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

    def _transfer_song(self, track, source_playlist, is_move=False):
        target_playlists = [p for p in self.playlist_manager.playlists if p['id'] != source_playlist['id']] if is_move else self.playlist_manager.playlists
        if not target_playlists:
            wx.MessageBox('No hay otras playlists disponibles.', 'Información', wx.OK | wx.ICON_INFORMATION)
            return

        names = [p['name'] for p in target_playlists]
        action_name = "Mover" if is_move else "Copiar"
        dlg = wx.SingleChoiceDialog(self, f'{action_name} "{track["display"]}" a:', f'{action_name} canción', names)
        if dlg.ShowModal() == wx.ID_OK:
            selected_target = target_playlists[dlg.GetSelection()]
            dlg.Destroy()

            def _worker():
                if is_move:
                    ok, msg = self.playlist_manager.move_track_to_playlist(source_playlist['id'], selected_target['id'], track['id'])
                else:
                    ok, msg = self.playlist_manager.copy_track_to_playlist(selected_target['id'], track['id'])

                def _done():
                    if ok:
                        wx.MessageBox(f'Canción {action_name.lower()}da a "{selected_target["name"]}" con éxito.', 'Éxito', wx.OK | wx.ICON_INFORMATION)
                        self.refresh_playlists()
                    else:
                        wx.MessageBox(msg, 'Error', wx.OK | wx.ICON_ERROR)
                wx.CallAfter(_done)

            threading.Thread(target=_worker, daemon=True).start()
        else:
            dlg.Destroy()

    def show_song_options(self, item):
        track = self.tree.GetItemData(item)
        parent_item = self.tree.GetItemParent(item)
        playlist = self.tree.GetItemData(parent_item)
        if not track or not playlist: return

        menu = wx.Menu()
        reproducir = menu.Append(wx.ID_ANY, 'Reproducir / Abrir en Spotify')
        menu.AppendSeparator()
        copiar_a = menu.Append(wx.ID_ANY, 'Copiar a otra playlist...')
        mover_a = menu.Append(wx.ID_ANY, 'Mover a otra playlist...')
        menu.AppendSeparator()
        eliminar = menu.Append(wx.ID_ANY, 'Eliminar de playlist')
        copiar = menu.Append(wx.ID_ANY, 'Copiar enlace')

        def on_reproducir(evt):
            self.play_or_open_track(track['id'])

        def on_copiar_a(evt):
            self._transfer_song(track, playlist, is_move=False)

        def on_mover_a(evt):
            self._transfer_song(track, playlist, is_move=True)
        
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

        self.Bind(wx.EVT_MENU, on_reproducir, reproducir)
        self.Bind(wx.EVT_MENU, on_copiar_a, copiar_a)
        self.Bind(wx.EVT_MENU, on_mover_a, mover_a)
        self.Bind(wx.EVT_MENU, on_eliminar, eliminar)
        self.Bind(wx.EVT_MENU, on_copiar, copiar)
        self.PopupMenu(menu)
        menu.Destroy()

    def show_playlist_options(self, item):
        playlist = self.tree.GetItemData(item)
        if not playlist: return

        menu = wx.Menu()
        editar = menu.Append(wx.ID_ANY, 'Editar nombre')
        duplicados = menu.Append(wx.ID_ANY, 'Buscar y eliminar duplicados')
        menu.AppendSeparator()
        eliminar = menu.Append(wx.ID_ANY, 'Eliminar playlist')
        copiar = menu.Append(wx.ID_ANY, 'Copiar enlace')
        
        def on_editar(evt):
            dlg = wx.TextEntryDialog(self, 'Nuevo nombre de la playlist:', 'Editar nombre', playlist['name'])
            if dlg.ShowModal() == wx.ID_OK:
                nuevo_nombre = dlg.GetValue().strip()
                dlg.Destroy()
                if self.playlist_manager.rename_playlist(playlist['id'], nuevo_nombre):
                    self.refresh_playlists()
            else:
                dlg.Destroy()

        def on_duplicados(evt):
            dlg = wx.MessageDialog(self, f'¿Deseas buscar y eliminar canciones duplicadas en "{playlist["name"]}"?', 'Limpiar duplicados', wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION)
            res = dlg.ShowModal()
            dlg.Destroy()
            if res == wx.ID_YES:
                def _worker():
                    count, msg = self.playlist_manager.remove_duplicate_tracks(playlist['id'])
                    def _done():
                        if count > 0:
                            wx.MessageBox(msg, 'Duplicados eliminados', wx.OK | wx.ICON_INFORMATION)
                            self.refresh_playlists()
                        elif count == 0:
                            wx.MessageBox('No se encontraron canciones duplicadas.', 'Información', wx.OK | wx.ICON_INFORMATION)
                        else:
                            wx.MessageBox(msg, 'Error', wx.OK | wx.ICON_ERROR)
                    wx.CallAfter(_done)

                threading.Thread(target=_worker, daemon=True).start()
        
        def on_eliminar(evt):
            dlg = wx.MessageDialog(self, f'¿Seguro que quieres eliminar la playlist "{playlist["name"]}"?', 'Confirmar eliminación', wx.YES_NO | wx.CANCEL | wx.NO_DEFAULT | wx.ICON_WARNING)
            res = dlg.ShowModal()
            dlg.Destroy()
            if res == wx.ID_YES:
                if self.playlist_manager.delete_playlist(playlist['id']):
                    self.refresh_playlists()
        
        def on_copiar(evt):
            self.playlist_manager.copy_playlist_link(playlist['id'])
            wx.MessageBox('Enlace copiado al portapapeles.', 'Éxito', wx.OK | wx.ICON_INFORMATION)

        self.Bind(wx.EVT_MENU, on_editar, editar)
        self.Bind(wx.EVT_MENU, on_duplicados, duplicados)
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
