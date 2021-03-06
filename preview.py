import sublime_plugin
import tempfile
import sublime
from .helper import log, PHANTOM_GROUP
from .helper import to_phantom, plugin_settings, is_inside_equation
import os
import threading


def plugin_loaded():
    global temp_dir, phantom_keys, temp_file_name
    temp_dir = tempfile.TemporaryDirectory(prefix='Eqn_Prev')
    temp_file = tempfile.NamedTemporaryFile(suffix=".tex",
                                            prefix="auto_eqn",
                                            dir=temp_dir.name,
                                            delete=False)
    temp_file_name = temp_file.name
    temp_file.close()
    phantom_keys = ['live_update']
    plugin_settings.update(
        sublime.load_settings("latex_equation_preview.sublime-settings"))


def plugin_unloaded():
    global temp_dir, temp_file_name
    try:
        temp_dir.cleanup()
        log('temp_dir removed')
        os.remove(temp_file_name)
        log('temp_file removed')
    except:
        pass


def is_showable():
    view = sublime.active_window().active_view()
    enabled_suffix = plugin_settings.get('enabled_for')
    if view.file_name() and enabled_suffix:
        for suffix in enabled_suffix:
            if view.file_name().endswith(suffix):
                return True
    return False


class PreviewMonitor(sublime_plugin.ViewEventListener):
    def __init__(self, view):
        self.view = view
        self.timeout_scheduled = False
        self.needs_update = False
        self.phantom_set = sublime.PhantomSet(view, "live_update")

    @classmethod
    def is_applicable(cls, settings):
        # syntax = settings.get('syntax')
        return is_showable() and plugin_settings.get('auto_compile')

    def on_modified_async(self):
        if is_inside_equation(self.view):
            if self.timeout_scheduled:
                self.needs_update = True
            else:
                sublime.set_timeout(lambda: self.handle_timeout(), 500)
                try:
                    self.update_phantoms()
                except:
                    pass

    def update_phantoms(self):
        global temp_dir, temp_file_name
        phantoms = []
        log("temp_file is {}".format(temp_file_name))
        raw_phantom = to_phantom(self.view, temp_dir.name, temp_file_name)
        phantoms.append(sublime.Phantom(raw_phantom['region'],
                                        raw_phantom['content'],
                                        raw_phantom['layout'],
                                        on_navigate=lambda x: self.phantom_set.update([])))
        self.phantom_set.update(phantoms)

    def handle_timeout(self):
        self.timeout_scheduled = False
        if self.needs_update:
            self.needs_update = False
            self.update_phantoms()


class ShowOutstandingPreviewCommand(sublime_plugin.WindowCommand):
    def is_enable(self):
        return is_showable()

    def run(self):
        view = self.window.active_view()
        if is_inside_equation(view):
            show_equation = ShowEquationPhantom(self.window.active_view())
            show_equation.start()
        else:
            log("not in the scope.")


class CleanEquationPhantomsCommand(sublime_plugin.WindowCommand):
    def is_enable(self):
        return is_showable()

    def run(self):
        global phantom_keys
        view = self.window.active_view()
        for key in phantom_keys:
            view.erase_phantoms(key)


class ShowEquationPhantom(threading.Thread):
    def __init__(self, view):
        super(ShowEquationPhantom, self).__init__(self)
        self.view = view

    def run(self):
        global temp_dir, phantom_keys
        raw_phantom = to_phantom(self.view, temp_dir.name)
        phantom_name = PHANTOM_GROUP + str(raw_phantom['region'].b)
        phantom_keys.append(phantom_name)
        self.view.add_phantom(phantom_name,
                              raw_phantom['region'],
                              raw_phantom['content'],
                              raw_phantom['layout'],
                              raw_phantom['on_navigate'])


