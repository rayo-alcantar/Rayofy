import wx
import threading

class SearchFrame(wx.Frame):
    def __init__(self, playlist_manager):
        super(SearchFrame, self).__init__(None, title="Buscar canción", size=(400, 250))

        self.playlist_manager = playlist_manager

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Cuadro de texto para buscar una canción
        self.search_text = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
        self.search_text.Bind(wx.EVT_TEXT_ENTER, self.on_search_button_click)
        self.search_text.SetHint("Buscar canción por nombre o artista...")
        vbox.Add(self.search_text, flag=wx.EXPAND | wx.ALL, border=10)

        # Botón "Buscar"
        self.search_button = wx.Button(panel, label="&Buscar")
        self.search_button.SetToolTip("Buscar canción (Alt+B)")
        self.search_button.Bind(wx.EVT_BUTTON, self.on_search_button_click)
        vbox.Add(self.search_button, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)
        self.search_button.SetDefault()

        panel.SetSizer(vbox)
        self.Bind(wx.EVT_CHAR_HOOK, self.on_char_hook)

    def on_char_hook(self, event):
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.Close()
        else:
            event.Skip()

    def on_search_button_click(self, event):
        search_query = self.search_text.GetValue().strip()
        if not search_query:
            wx.MessageBox('Por favor, introduce un término de búsqueda.', 'Información', wx.OK | wx.ICON_INFORMATION)
            return

        self.search_button.Disable()
        self.search_button.SetLabel("Buscando...")

        def _search_worker():
            try:
                results = self.playlist_manager.sp.search(q=search_query, limit=20, type='track')
                tracks = results.get('tracks', {}).get('items', [])
                wx.CallAfter(self._handle_search_results, tracks)
            except Exception as e:
                wx.CallAfter(self._handle_search_error, str(e))

        threading.Thread(target=_search_worker, daemon=True).start()

    def _handle_search_error(self, err_msg):
        self.search_button.Enable()
        self.search_button.SetLabel("&Buscar")
        wx.MessageBox(f'Error en la búsqueda: {err_msg}', 'Error', wx.OK | wx.ICON_ERROR)

    def _handle_search_results(self, tracks):
        self.search_button.Enable()
        self.search_button.SetLabel("&Buscar")

        if not tracks:
            wx.MessageBox('No se encontraron resultados.', 'Información', wx.OK | wx.ICON_INFORMATION)
            return

        track_labels = []
        for t in tracks:
            artists = t.get('artists', [])
            artist_name = artists[0]['name'] if artists else 'Desconocido'
            track_labels.append(f"{t.get('name', 'Sin título')} - {artist_name}")

        choice_dlg = wx.SingleChoiceDialog(self, 'Elige una canción:', 'Resultados de búsqueda', track_labels)
        if choice_dlg.ShowModal() != wx.ID_OK:
            choice_dlg.Destroy()
            return

        selected_idx = choice_dlg.GetSelection()
        selected_track = tracks[selected_idx]
        choice_dlg.Destroy()

        if not self.playlist_manager.playlists:
            self.playlist_manager.fetch_playlists()

        playlist_names = [p['name'] for p in self.playlist_manager.playlists]
        if not playlist_names:
            wx.MessageBox('No se encontraron playlists disponibles.', 'Información', wx.OK | wx.ICON_INFORMATION)
            return

        playlist_dlg = wx.SingleChoiceDialog(self, 'Elige una playlist:', 'Añadir a playlist', playlist_names)
        if playlist_dlg.ShowModal() != wx.ID_OK:
            playlist_dlg.Destroy()
            return

        selected_playlist = self.playlist_manager.playlists[playlist_dlg.GetSelection()]
        playlist_dlg.Destroy()

        try:
            self.playlist_manager.sp.playlist_add_items(selected_playlist['id'], [selected_track['uri']])
            
            # Incrementar el contador local de la playlist en memoria
            if 'tracks' in selected_playlist and isinstance(selected_playlist['tracks'], dict):
                selected_playlist['tracks']['total'] = selected_playlist['tracks'].get('total', 0) + 1

            wx.MessageBox(f'"{selected_track.get("name")}" añadida a "{selected_playlist.get("name")}"', 'Éxito', wx.OK | wx.ICON_INFORMATION)

            # Refrescar ventanas principales
            for w in wx.GetTopLevelWindows():
                if hasattr(w, 'refresh_playlists'):
                    w.refresh_playlists()
        except Exception as e:
            wx.MessageBox(f'Error al añadir canción: {e}', 'Error', wx.OK | wx.ICON_ERROR)
