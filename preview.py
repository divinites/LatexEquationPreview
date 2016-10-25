import sublime_plugin
import tempfile
import sublime
from .helper import ViewConverter, FileConverter
from .helper import INLINE_SCOPE, BLOCK_SCOPE, INLINE_FLAG, BLOCK_FLAG
import threading


def plugin_loaded():
    global temp_dir
    temp_dir = tempfile.TemporaryDirectory(prefix='Eqn_Prev')


def plugin_unloaded():
    global temp_dir
    temp_dir.cleanup()


class preview_listener(sublime_plugin.ViewEventListener):
    pass


class ShowOutstandingPreviewCommand(sublime_plugin.WindowCommand):
    def is_enable(self):
        view = self.window.active_view()
        if view.scope_name(0).startswith('text.tex'):
            return True
        return False

    def run(self):
        show_equation = ShowEquationPhantom(self.window.active_view())
        show_equation.start()


class ShowEquationPhantom(threading.Thread):
    def __init__(self, view):
        super(ShowEquationPhantom, self).__init__(self)
        self.view = view

    def run(self):
        global temp_dir
        view_converter = ViewConverter(self.view)
        content_region, FLAG = view_converter.find_equation_range()
        if content_region:
            file_converter = FileConverter(temp_dir.name)
            tex_file = file_converter.create_temptex(self.view.substr(content_region))
            png_file = file_converter.tex_to_png(tex_file)
            png_str = file_converter.png_to_datastr(png_file)
            self.view.add_phantom("latex_equation",
                                  sublime.Region(content_region.b, content_region.b + 1) if FLAG == BLOCK_FLAG
                                  else self.view.sel()[0],
                                  png_str,
                                  sublime.LAYOUT_BLOCK if FLAG == BLOCK_FLAG else sublime.LAYOUT_BELOW,
                                  on_navigate=lambda href: self.view.erase_phantoms("latex_equation"))

