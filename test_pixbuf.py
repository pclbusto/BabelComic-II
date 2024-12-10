# import re
# linea = ""
# with open("input.txt","r") as archivo:
#     linea = archivo.readline()
#     salida = ""
#     ids_comic = set()
#     expresion = "(\d+)\s(.*)"
#     while linea:
#         linea = archivo.readline()
#         # print(linea)
#         match = re.findall(expresion, linea)
#
#         if match:
#             ids_comic.add((match[0][0], match[0][1]))
#
#     lista = list(ids_comic)
#     lista_cadena = "{}".format(lista)
#     # print(lista_cadena)
#     lista_cadena = lista_cadena.replace("[", "")
#     lista_cadena = lista_cadena.replace("]", "")
#     lista_cadena = lista_cadena.replace("), (", "),\n (")
#     # print(lista_cadena)
#     # salida = salida+"delete  FROM comicbooks_info_cover_url where id_comicbook_info in ({})".format(lista_cadena)
#     salida = "INSERT INTO comicbooks_info_cover_url(\"id_comicbook_info\", \"thumb_url\") VALUES {};".format(lista_cadena)
#     with open("salida.txt", "w") as salida_f:
#         salida_f.write(salida)
#     # print(salida)
#
#
import gtk
import webkit

class Editor(webkit.WebView):
    '''a webkit editor'''

    def __init__(self):
        webkit.WebView.__init__(self)
        self.set_editable(True)

class EditorWindow(gtk.Window):
    '''the editor window'''

    def __init__(self):
        gtk.Window.__init__(self)
        self.set_title("webkit editor")
        self.set_default_size(800, 600)

        self.entry = gtk.Entry()
        self.entry.set_text("http://webkit.org")
        self.entry.connect('activate', self._on_entry_activate)
        self.editor = Editor()
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.set_shadow_type(gtk.SHADOW_IN)

        scroll.add(self.editor)

        vbox = gtk.VBox()
        vbox.pack_start(self.entry, False)
        vbox.pack_start(scroll)

        self.add(vbox)
        vbox.show_all()

    def load(self, url):
        '''load the given url in the editor and set it to editable'''
        self.editor.open(url)

    def _on_entry_activate(self, entry):
        '''callback called when the user hits enter on the entry'''
        self.load(entry.get_text())

if __name__ == '__main__':
    window = EditorWindow()
    window.show()
    window.entry.activate()
    gtk.main()

view.open("http://w3.org/")
gtk.main()