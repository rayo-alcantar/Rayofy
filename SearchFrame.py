import wx

class SearchFrame(wx.Frame):
    def __init__(self, playlist_manager):
        super(SearchFrame, self).__init__(None, title="Buscar canción", size=(400, 200))

        self.playlist_manager = playlist_manager

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Cuadro de texto para buscar una canción
        self.search_text = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
        self.search_text.Bind(wx.EVT_TEXT_ENTER, self.on_search_button_click)
        self.search_text.SetHint("Buscar canción por nombre o artista...")
        vbox.Add(self.search_text, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        # Botón "Buscar"
        search_button = wx.Button(panel, label="&Buscar")
        search_button.SetToolTip("Buscar canción (Alt+B)")
        search_button.Bind(wx.EVT_BUTTON, self.on_search_button_click)
        vbox.Add(search_button, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)
        search_button.SetDefault()

        panel.SetSizer(vbox)
    def on_search_button_click(self, event):
        import wx  # Asegura que wx está en el scope local para los errores
        search_query = self.search_text.GetValue().strip()
        if not search_query:
            wx.MessageBox('Por favor, introduce un término de búsqueda.', 'Información', wx.OK | wx.ICON_INFORMATION)
            return
        try:
            results = self.playlist_manager.sp.search(q=search_query, limit=30, type='track')
            tracks = results['tracks']['items']
            if not tracks:
                wx.MessageBox('No se encontraron resultados.', 'Información', wx.OK | wx.ICON_INFORMATION)
                self.Close()
                return
            seguir = True
            while seguir:
                track_names = [f"{track['name']} - {track['artists'][0]['name']}" for track in tracks]
                dialog = wx.SingleChoiceDialog(self, 'Elige una canción para añadir a una playlist:', 'Resultados de búsqueda', track_names)
                if dialog.ShowModal() == wx.ID_OK:
                    selected_track = tracks[dialog.GetSelection()]
                    self.playlist_manager.fetch_playlists()
                    playlist_names = [playlist['name'] for playlist in self.playlist_manager.playlists]
                    playlist_dialog = wx.SingleChoiceDialog(self, 'Elige una playlist para añadir la canción:', 'Elige una playlist', playlist_names)
                    if playlist_dialog.ShowModal() == wx.ID_OK:
                        selected_playlist = self.playlist_manager.playlists[playlist_dialog.GetSelection()]
                        self.playlist_manager.sp.playlist_add_items(selected_playlist['id'], [selected_track['uri']])
                    playlist_dialog.Destroy()
                dialog.Destroy()
                continue_dialog = wx.MessageDialog(self, '¿Quieres añadir más canciones?', 'Continuar', wx.YES_NO)
                respuesta = continue_dialog.ShowModal()
                continue_dialog.Destroy()
                if respuesta == wx.ID_YES:
                    self.search_text.SetValue("")
                    self.search_text.SetFocus()
                    return
                else:
                    self.GetParent().Close() if self.GetParent() else self.Close()
                    for w in wx.GetTopLevelWindows():
                        if hasattr(w, 'refresh_playlists'):
                            w.refresh_playlists()
                    return
        except Exception as e:
            import wx  # Asegura wx en el scope del except
            wx.MessageBox(f'Error al buscar o añadir canción: {e}', 'Error', wx.OK | wx.ICON_ERROR)