import sublime
import tempfile
import subprocess
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
            return sublime.Region(self.view.line(start).a, self.view.line(end).b), BLOCK_FLAG
        elif selector == INLINE_SCOPE:
            return sublime.Region(start + 1, end), INLINE_FLAG
        else:
            return


class FileConverter:
    def __init__(self, directory):
        self.directory = directory

    def create_temptex(self, content):
        with tempfile.NamedTemporaryFile(suffix=".tex", prefix="eqn", dir=self.directory, delete=False) as texfile:
            texfile.write(bytes(HEAD(content), 'UTF-8'))
            return texfile.name

    def tex_to_png(self, file):
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
        convert_cmd = [convert, '-density', '300', pdf_name, "-resize", "75%", png_name]
        trim_cmd = [convert, png_name, '-trim', png_name]
        color = sublime.load_settings("latex_equation_preview.sublime-settings").get('equation_color', 'red')
        size = sublime.load_settings("latex_equation_preview.sublime-settings").get('equation_size', '100%')
        color_cmd = [convert, png_name, "-alpha", "off", "-fuzz", "10%", '-fill', color, '-opaque', 'black', "-alpha", "on", png_name]
        resize_cmd = [convert, png_name, "-resize", size, png_name]
        command_sequence = [compile_cmd, convert_cmd, trim_cmd, color_cmd]
        if size != "100%":
            command_sequence.append(resize_cmd)
        # clean_up_cmd = [latexmk, '-C']
        try:
            for cmd in command_sequence:
                subprocess.check_call(cmd)
            # subprocess.call(clean_up_cmd)
        except CalledProcessError as e:
            print(e)
        return png_name

    def png_to_datastr(self, png_file):
        with open(png_file, "rb") as png:
            raw_data = png.read()
        img_data = base64.b64encode(raw_data).decode()
        return '<img style="max-width:200px" src="data:image/png;base64,{0}" />'.format(img_data)


class FileFormatErrorException(Exception):
    pass


class LatexCommandException(Exception):
    pass
