import sublime
import tempfile
import subprocess
from subprocess import shutup
import base64
from subprocess import CalledProcessError
import os

HEAD = lambda x: """
\\nonstopmode
\\documentclass[preview]{standalone}
\\usepackage{amssymb}
\\usepackage{amsmath}
\\usepackage{geometry}
\\begin{document}
""" + str(x) + """
\\end{document}
"""

INLINE_SCOPE = "meta.environment.math.inline.dollar.latex"
BLOCK_SCOPE = "meta.environment.math.block.be.latex"

INLINE_FLAG = 0
BLOCK_FLAG = 1
PHANTOM_GROUP = 'latex_equation'


class Setting:
    def __init__(self):
        self.settings = None

    def get(self, key, value=None):
        if self.settings:
            return self.settings.get(key, value)

    def update(self, setting_object):
        self.settings = setting_object


plugin_settings = Setting()


class ViewConverter:
    def __init__(self, view):
        self.view = view
    #     self.visible_region = view.visible_region()

    # def update_visible_region(self):
    #     self.visible_region = self.view.visible_region()

    def find_equation_range(self):
        start = self.view.sel()[0].a
        end = self.view.sel()[0].b
        if self.view.match_selector(start, INLINE_SCOPE):
            selector = INLINE_SCOPE
        elif self.view.match_selector(start, BLOCK_SCOPE):
            selector = BLOCK_SCOPE
        else:
            return
        while self.view.match_selector(start, selector):
            start -= 1
            if start < 0:
                return
        while self.view.match_selector(end, selector):
            end += 1
            if end > self.view.size():
                return
        if selector == BLOCK_SCOPE:
            return sublime.Region(
                self.view.line(start).a, self.view.line(end).b), BLOCK_FLAG
        elif selector == INLINE_SCOPE:
            return sublime.Region(start + 1, end), INLINE_FLAG
        else:
            return


class FileConverter:
    def __init__(self, directory):
        self.directory = directory

    def create_temptex(self, content):
        with tempfile.NamedTemporaryFile(
                suffix=".tex", prefix="eqn", dir=self.directory,
                delete=False) as texfile:
            texfile.write(bytes(HEAD(content), 'UTF-8'))
            return texfile.name

    def tex_to_png(self, file, flag):
        if not file.endswith('.tex'):
            raise FileFormatErrorException("The input should be a tex file!")
        else:
            pdf_name = file[:-3] + "pdf"
            png_name = file[:-3] + "png"

        pdflatex = 'pdflatex'
        convert = 'convert'
        directory, _ = os.path.split(file)
        os.chdir(directory)
        compile_cmd = [pdflatex, file]
        convert_cmd = [convert, '-density', '300', pdf_name, "-resize", "75%",
                       png_name]
        trim_cmd = [convert, png_name, '-trim', png_name]
        foreground_color = plugin_settings.get('equation_foreground_color', 'red')
        # background_color = sublime.load_settings(
        #     "latex_equation_preview.sublime-settings").get(
        #         'equation_background_color', "none")
        inline_size = plugin_settings.get('equation_inline_size', '100%')
        block_size = plugin_settings.get("equation_block_size", '100%')
        foreground_color_cmd = [convert, png_name, "-alpha", "off", "-fuzz",
                                "10%", '-fill', foreground_color, '-opaque',
                                'black', "-alpha", "on", png_name]
        command_sequence = [compile_cmd, convert_cmd, trim_cmd,
                            foreground_color_cmd]
        if flag == INLINE_FLAG:
            size = inline_size
        elif flag == BLOCK_FLAG:
            size = block_size
        else:
            pass

        if size != "100%":
            resize_cmd = [convert, png_name, "-resize", size, png_name]
            command_sequence.append(resize_cmd)
        # if background_color != "none":
        #     log("background color is {}".format(background_color))
        #     background_color_cmd = [convert, png_name, '-background', background_color, png_name]
        #     command_sequence.append(background_color_cmd)

        try:
            for cmd in command_sequence:
                subprocess.check_call(cmd, stdout=shutup, stderr=shutup)
            # subprocess.call(clean_up_cmd)
        except CalledProcessError as e:
            print(e)
        return png_name

    def png_to_datastr(self, png_file):
        with open(png_file, "rb") as png:
            raw_data = png.read()
        return base64.b64encode(raw_data).decode()


def log(info):
    debug_flag = plugin_settings.get('debug', 0)
    if debug_flag != 0:
        print("LatexEquationPreview >>> " + info)


def to_phantom(view, dir_name):
    view_converter = ViewConverter(view)
    content_region, FLAG = view_converter.find_equation_range()
    log("region is {} and flag is {}".format(
        repr(content_region), repr(FLAG)))
    if content_region:
        file_converter = FileConverter(dir_name)
        log("temp_dir is {}".format(dir_name))
        tex_file = file_converter.create_temptex(view.substr(content_region))
        png_file = file_converter.tex_to_png(tex_file, FLAG)
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
        """.format(plugin_settings.get("equation_background_color"), png_str)
        group_name = PHANTOM_GROUP + str(content_region.b + 1)
        return {"region": sublime.Region(content_region.b, content_region.b + 1),
                "content": html_str,
                "layout": sublime.LAYOUT_BLOCK if FLAG == BLOCK_FLAG else sublime.LAYOUT_INLINE,
                "on_navigate": lambda href: view.erase_phantoms(group_name)}


class FileFormatErrorException(Exception):
    pass


class LatexCommandException(Exception):
    pass

