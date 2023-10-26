# Importaciones para la interfaz gráfica
import sys
import wx

sys.path.append('.')
try:
    from SpotifyAuthenticator import SpotifyAuthenticator
    from PlaylistManager import PlaylistManager
    from SearchFrame import SearchFrame
except ImportError as e:
    print("error en la importación")

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
        
        # Crear un objeto wx.Menu
        file_menu = wx.Menu()
        
        # Añadir un elemento de menú para "Crear Playlist"
        create_playlist_item = file_menu.Append(wx.ID_ANY, 'Crear Playlist', 'Crear una nueva Playlist')
        self.Bind(wx.EVT_MENU, self.on_create_playlist, create_playlist_item)
        
        # Añadir el menú a la barra de menús
        menu_bar.Append(file_menu, '&Acciones')
        
        # Establecer la barra de menús para la ventana
        self.SetMenuBar(menu_bar)
        # Crear el árbol de playlists
        self.tree = wx.TreeCtrl(panel, style=wx.TR_DEFAULT_STYLE | wx.TR_FULL_ROW_HIGHLIGHT)
        root = self.tree.AddRoot('Playlists')
        
        # Poblar el árbol con playlists
        self.playlist_manager.fetch_playlists()
        for i, playlist in enumerate(self.playlist_manager.playlists):
            
            playlist_item = self.tree.AppendItem(root, playlist['name'])
            self.tree.AppendItem(playlist_item, "Cargando...")
        # Vincular el evento de expansión del árbol
        self.tree.Bind(wx.EVT_TREE_ITEM_EXPANDING, self.on_tree_item_expanding)
        self.tree.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.on_tree_item_right_click)

        
        # Botones   
        delete_button = wx.Button(panel, label='Eliminar Playlist')
        search_button = wx.Button(panel, label='Buscar')  
        close_button = wx.Button(panel, label='Cerrar')
        copy_link_button = wx.Button(panel, label='Copiar enlace al portapapeles')
        self.tree.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.on_tree_item_right_click)

        # Vincular eventos a botones
        delete_button.Bind(wx.EVT_BUTTON, self.delete_playlist)
        search_button.Bind(wx.EVT_BUTTON, self.on_search_button_click)
        close_button.Bind(wx.EVT_BUTTON, self.close_app)
        copy_link_button.Bind(wx.EVT_BUTTON, self.copy_playlist_link)  # Evento vinculado

        # Añadir elementos al sizer
        vbox.Add(self.tree, proportion=1, flag=wx.EXPAND)
        vbox.Add(delete_button, proportion=0, flag=wx.ALIGN_CENTER)
        vbox.Add(search_button, proportion=0, flag=wx.ALIGN_CENTER)
        vbox.Add(copy_link_button, proportion=0, flag=wx.ALIGN_CENTER)
        vbox.Add(close_button, proportion=0, flag=wx.ALIGN_CENTER)

        panel.SetSizer(vbox)
    def on_create_playlist(self, event):
        # Crear un nuevo cuadro de diálogo
        dlg = wx.TextEntryDialog(self, 'Ingrese el nombre de la nueva playlist:', 'Crear Playlist')
        
        # Mostrar el cuadro de diálogo y esperar la respuesta del usuario
        if dlg.ShowModal() == wx.ID_OK:
            playlist_name = dlg.GetValue().strip()  # Obtener el valor del cuadro de texto y eliminar espacios en blanco
            
            # Validación básica
            if not playlist_name:
                wx.MessageBox('El nombre de la playlist no puede estar vacío.', 'Error', wx.OK | wx.ICON_ERROR)
                return
            if len(playlist_name) > 99:  # Suponiendo que 100 caracteres es el máximo permitido
                wx.MessageBox('El nombre de la playlist es demasiado largo.', 'Error', wx.OK | wx.ICON_ERROR)
                return
            
            # Llamar al método para crear una nueva playlist desde la clase PlaylistManager
            try:
                self.playlist_manager.create_new_playlist(playlist_name)
                wx.MessageBox(f'Playlist {playlist_name} creada exitosamente.', 'Éxito', wx.OK | wx.ICON_INFORMATION)
                # Actualizar la lista de playlists
                self.playlist_manager.fetch_playlists()
                
                # Borrar y volver a construir el árbol
                self.tree.DeleteChildren(self.tree.GetRootItem())
                for i, playlist in enumerate(self.playlist_manager.playlists):
                    playlist_item = self.tree.AppendItem(self.tree.GetRootItem(), playlist['name'])
                    self.tree.AppendItem(playlist_item, "Cargando...")
            except Exception as e:
                wx.MessageBox(f'Error al crear la playlist: {e}', 'Error', wx.OK | wx.ICON_ERROR)
        
        # Destruir el cuadro de diálogo para liberar recursos
        dlg.Destroy()
    
    def on_search_button_click(self, event):
        # Crea una nueva instancia de SearchFrame y la muestra
        search_frame = SearchFrame(self.playlist_manager)
        search_frame.Show()
    
    def copy_playlist_link(self, event):
        item = self.tree.GetSelection()
        if item:
            if self.tree.GetItemParent(item) == self.tree.GetRootItem():
                playlist_name = self.tree.GetItemText(item)
                playlist_id = None
                for playlist in self.playlist_manager.playlists:
                    if playlist['name'] == playlist_name:
                        playlist_id = playlist['id']
                        break
                if playlist_id:
                    self.playlist_manager.copy_playlist_link(playlist_id)

    def on_tree_item_expanding(self, event):
        #print("funciona?")
        
        item = event.GetItem()
        parent = self.tree.GetItemParent(item)
        if parent == self.tree.GetRootItem():
            playlist_name = self.tree.GetItemText(item)
            playlist_id = None
            #print("Appending tracks to tree...")
            for playlist in self.playlist_manager.playlists:
                if playlist['name'] == playlist_name:
                    playlist_id = playlist['id']
                    break
            if playlist_id:
                # Borrar los elementos existentes del subárbol
                self.tree.DeleteChildren(item)
    
                # Obtener las canciones de la playlist
                tracks = self.playlist_manager.fetch_tracks_from_playlist(playlist_id)
                
                # Añadir las canciones al subárbol
                for track in tracks:
                    self.tree.AppendItem(item, track)
    def delete_playlist(self, event):
        item = self.tree.GetSelection()
        if item:
            # Comprobar si el elemento seleccionado es una raíz o un hijo
            if self.tree.GetItemParent(item) == self.tree.GetRootItem():
                playlist_name = self.tree.GetItemText(item)
                playlist_id = None
                # Obtener el ID de la playlist a partir del nombre
                for playlist in self.playlist_manager.playlists:
                    if playlist['name'] == playlist_name:
                        playlist_id = playlist['id']
                        break
                
                # Confirmación antes de eliminar
                dlg = wx.MessageDialog(self, '¿Estás seguro de que quieres eliminar esta playlist?', 'Eliminar Playlist', wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
                
                if dlg.ShowModal() == wx.ID_YES:
                    # Eliminar la playlist en Spotify
                    try:
                        self.playlist_manager.sp.current_user_unfollow_playlist(playlist_id)
                        
                        # Eliminar el elemento del árbol
                        self.tree.Delete(item)
                    except Exception as e:
                        wx.MessageBox(f'Error al eliminar la playlist en Spotify: {e}', 'Error', wx.OK | wx.ICON_ERROR)
                
                dlg.Destroy()
            else:
                wx.MessageBox('Por favor, selecciona una playlist contraída para eliminar.', 'Atención', wx.OK | wx.ICON_INFORMATION)
    def on_tree_item_right_click(self, event):
        #print("Sí, hace click")
        item = event.GetItem()
        parent = self.tree.GetItemParent(item)
        
        if parent != self.tree.GetRootItem():  # Este es un nodo de una canción
            self.show_song_options(item)
    def show_song_options(self, item):
        song_name = self.tree.GetItemText(item)
        parent_item = self.tree.GetItemParent(item)
        playlist_name = self.tree.GetItemText(parent_item)
        
        dlg = wx.MessageDialog(
            self,
            f'¿Qué quieres hacer con la canción {song_name}?',
            'Opciones de la canción',
            wx.YES_NO | wx.CANCEL | wx.YES_DEFAULT | wx.ICON_QUESTION
        )
        
        dlg.SetYesNoLabels('Eliminar de playlist', 'Copiar enlace')
        
        result = dlg.ShowModal()
        
        if result == wx.ID_YES:
            self.playlist_manager.delete_song_from_playlist(playlist_name, song_name)
        elif result == wx.ID_NO:
            self.playlist_manager.copy_song_link(playlist_name, song_name)
        elif result == wx.ID_CANCEL:
            # Cancelar
            pass
        
        dlg.Destroy()
    def close_app(self, event):
        self.Close()

# Código para iniciar la aplicación
if __name__ == "__main__":
    app = wx.App(False)
    auth = SpotifyAuthenticator()
    auth.authenticate_api()
    auth.load_user_session()
    playlist_manager = PlaylistManager(auth.sp)
    frame = Rayofy(auth, playlist_manager)
    frame.Show()
    app.MainLoop()
