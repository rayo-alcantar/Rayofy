import wx

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
        search_button = wx.Button(panel, label="&Buscar")
        search_button.SetToolTip("Buscar canción (Alt+B)")
        search_button.Bind(wx.EVT_BUTTON, self.on_search_button_click)
        vbox.Add(search_button, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)
        search_button.SetDefault()

        panel.SetSizer(vbox)

    def on_search_button_click(self, event):
        search_query = self.search_text.GetValue().strip()
        if not search_query:
            wx.MessageBox('Por favor, introduce un término de búsqueda.', 'Información', wx.OK | wx.ICON_INFORMATION)
            return

        try:
            results = self.playlist_manager.sp.search(q=search_query, limit=20, type='track')
            tracks = results['tracks']['items']
            
            if not tracks:
                wx.MessageBox('No se encontraron resultados.', 'Información', wx.OK | wx.ICON_INFORMATION)
                return

            track_labels = [f"{t['name']} - {t['artists'][0]['name']}" for t in tracks]
            choice_dlg = wx.SingleChoiceDialog(self, 'Elige una canción:', 'Resultados de búsqueda', track_labels)
            
            if choice_dlg.ShowModal() == wx.ID_OK:
                selected_track = tracks[choice_dlg.GetSelection()]
                
                self.playlist_manager.fetch_playlists()
                playlist_names = [p['name'] for p in self.playlist_manager.playlists]
                
                playlist_dlg = wx.SingleChoiceDialog(self, 'Elige una playlist:', 'Añadir a playlist', playlist_names)
                
                if playlist_dlg.ShowModal() == wx.ID_OK:
                    selected_playlist = self.playlist_manager.playlists[playlist_dlg.GetSelection()]
                    try:
                        self.playlist_manager.sp.playlist_add_items(selected_playlist['id'], [selected_track['uri']])
                        wx.MessageBox(f'"{selected_track["name"]}" añadida a "{selected_playlist["name"]}"', 'Éxito', wx.OK | wx.ICON_INFORMATION)
                        
                        # Refresh main window if possible
                        for w in wx.GetTopLevelWindows():
                            if hasattr(w, 'refresh_playlists'):
                                w.refresh_playlists()
                    except Exception as e:
                        wx.MessageBox(f'Error al añadir canción: {e}', 'Error', wx.OK | wx.ICON_ERROR)
                
                playlist_dlg.Destroy()
            choice_dlg.Destroy()

        except Exception as e:
            wx.MessageBox(f'Error en la búsqueda: {e}', 'Error', wx.OK | wx.ICON_ERROR)
