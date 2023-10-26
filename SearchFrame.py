import wx

class SearchFrame(wx.Frame):
    def __init__(self, playlist_manager):
        super(SearchFrame, self).__init__(None, title="Buscar canción", size=(400, 200))

        self.playlist_manager = playlist_manager

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Cuadro de texto para buscar una canción
        self.search_text = wx.TextCtrl(panel)
        vbox.Add(self.search_text, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        # Botón "Buscar"
        search_button = wx.Button(panel, label="Buscar")
        search_button.Bind(wx.EVT_BUTTON, self.on_search_button_click)
        vbox.Add(search_button, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)

        panel.SetSizer(vbox)
    def on_search_button_click(self, event):
        search_query = self.search_text.GetValue().strip()
        
        if not search_query:
            wx.MessageBox('Por favor, introduce un término de búsqueda.', 'Información', wx.OK | wx.ICON_INFORMATION)
            return
    
        # Realizar la búsqueda en Spotify (solo canciones)
        try:
            results = self.playlist_manager.sp.search(q=search_query, limit=10, type='track')
            tracks = results['tracks']['items']
            
            if not tracks:
                wx.MessageBox('No se encontraron resultados.', 'Información', wx.OK | wx.ICON_INFORMATION)
                self.Close()
                return
    
            # Mostrar los resultados en un menú para que el usuario pueda elegir una canción
            track_names = [track['name'] for track in tracks]
            dialog = wx.SingleChoiceDialog(self, 'Elige una canción para añadir a una playlist:', 'Resultados de búsqueda', track_names)
    
            if dialog.ShowModal() == wx.ID_OK:
                selected_track = tracks[dialog.GetSelection()]
    
                # Mostrar otro menú para seleccionar la playlist a la que se desea añadir la canción
                self.playlist_manager.fetch_playlists()
                playlist_names = [playlist['name'] for playlist in self.playlist_manager.playlists]
                dialog = wx.SingleChoiceDialog(self, 'Elige una playlist para añadir la canción:', 'Elige una playlist', playlist_names)
    
                if dialog.ShowModal() == wx.ID_OK:
                    selected_playlist = self.playlist_manager.playlists[dialog.GetSelection()]
                    # Añadir la canción a la playlist
                    self.playlist_manager.sp.playlist_add_items(selected_playlist['id'], [selected_track['uri']])
                    
                dialog.Destroy()
            
            dialog.Destroy()
    
            # Limpiar el cuadro de texto de búsqueda
            self.search_text.SetValue("")
    
        except Exception as e:
            wx.MessageBox(f'Error al buscar o añadir canción: {e}', 'Error', wx.OK | wx.ICON_ERROR)