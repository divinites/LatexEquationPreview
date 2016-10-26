import sublime_plugin
import tempfile
import sublime
from .helper import ViewConverter, FileConverter, log, settings
from .helper import INLINE_SCOPE, BLOCK_SCOPE, INLINE_FLAG, BLOCK_FLAG
import threading


def plugin_loaded():
    global temp_dir, settings, phantom_list, phantom_key
    temp_dir = tempfile.TemporaryDirectory(prefix='Eqn_Prev')
    settings.update(sublime.load_settings("latex_equation_preview.sublime-settings"))
    phantom_key = []


def plugin_unloaded():
    global temp_dir
    temp_dir.cleanup()


class ShowOutstandingPreviewCommand(sublime_plugin.WindowCommand):
    def is_enable(self):
        view = self.window.active_view()
        if view.scope_name(0).startswith('text.tex'):
            return True
        return False

    def run(self):
        show_equation = ShowEquationPhantom(self.window.active_view())
        show_equation.start()


class CleanEquationPhantoms(sublime_plugin.WindowCommand):
    def is_enable(self):
        view = self.window.active_view()
        if view.scope_name(0).startswith('text.tex'):
            return True
        return False

    def run(self):
        global phantom_key
        view = self.window.active_view()
        for key in phantom_key:
            view.erase_phantoms(key)


class ShowEquationPhantom(threading.Thread):
    def __init__(self, view):
        super(ShowEquationPhantom, self).__init__(self)
        self.view = view
        self.phantom_set = sublime.PhantomSet(self.view, "latex_equation")

    def run(self):
        global temp_dir, settings, phantom_key
        view_converter = ViewConverter(self.view)
        content_region, FLAG = view_converter.find_equation_range()
        log("region is {} and flag is {}".format(repr(content_region), repr(FLAG)))
        if content_region:
            file_converter = FileConverter(temp_dir.name)
            log("temp_dir is {}".format(temp_dir.name))
            tex_file = file_converter.create_temptex(self.view.substr(content_region))
            png_file = file_converter.tex_to_png(tex_file)
            log("png file is {}".format(png_file))
            png_str = file_converter.png_to_datastr(png_file)
            html_str = """
            <style>
            .block {{
                background-color:{};
                position:relative;
                top: -12px;
                display: inline;
            }}
            </style>
            <span class="block">
            <a href="#"><img src="data:image/png;base64,{}" /></a>
            </span>
            """.format(settings.get("equation_background_color"), png_str)
            phantom_name = "latex_equation" + str(content_region.b)
            phantom_key.append(phantom_name)
            self.view.add_phantom(phantom_name,
                                  sublime.Region(content_region.b, content_region.b + 1),
                                  html_str,
                                  sublime.LAYOUT_BLOCK if FLAG == BLOCK_FLAG else sublime.LAYOUT_INLINE,
                                  on_navigate=lambda href: self.view.erase_phantoms(phantom_name))

