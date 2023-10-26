class SearchFrame(wx.Frame):
    def __init__(self, parent, title):
        super(SearchFrame, self).__init__(parent, title=title, size=(400, 300))
        
        # Aquí puedes añadir más elementos a la interfaz gráfica de esta ventana
        panel = wx.Panel(self)
        label = wx.StaticText(panel, label="Introduce tu búsqueda:", pos=(20, 20))
        self.textbox = wx.TextCtrl(panel, pos=(20, 50), size=(300, 25))
        
        search_button = wx.Button(panel, label="Buscar", pos=(250, 100))
        # Aquí puedes vincular este botón a un método que realice la búsqueda, por ejemplo
        # search_button.Bind(wx.EVT_BUTTON, self.perform_search)
        
        self.Show()
