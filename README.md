# LatexEquationPreview

## Introduction

This plug-in make use of the new feature of Sublime Text, Phantom, to preview latex equations.

### ATTENTION


This plug-in need `imagemagick` and `texlive/mactex` installed. otherwise it does not work.

If you do not have Tex installed, you won't need this plugin.

imagemagick can be downloaded [here](http://www.imagemagick.org/script/binary-releases.php)


### Special Attention for Windows User:

- To install `convert.exe`, please choose `legacy support` when installing imagemagick.

- `convert.exe` needs ghostscript support, please download it [here](https://github.com/ArtifexSoftware/ghostpdl-downloads/releases/download/gs920/gs920w32.exe)

## Usage

![Preview Equation](https://www.scislab.com/static/media/uploads/PrivateGraphs/latex_preview.gif)
![Auto Compilation](https://www.scislab.com/static/media/uploads/PrivateGraphs/auto_compile.gif)

Currently there are two commands available:

```json

[
    {
        "caption": "Equation Preview: View Current Equation",
        "command": "show_outstanding_preview"
    },
    {
        "caption": "Equation Preview: Clear Equation Preview",
        "command": "clean_equation_phantoms"
    },

]
```
Corresponding shortcut is <kbd>ctrl+shift+x</kbd> for show preview and <kbd>ctrl+shift+alt+x</kbd> for clean all preview.

Users can simply click on the phantom to close a single equation preview.

If auto-compile trigger in settings is set to `true`, then a preview with automatically show up when users are writing an equation.

## Configuration

```json
{
    "equation_foreground_color": "yellow",
    "equation_background_color": "",
    "equation_inline_size": "45%",
    "equation_block_size": "60%",
    "auto_compile": true,
    "convert_binary": "",
    "pdflatex_binary": "",
    "debug": 0
}

```
- equation_foreground_color is the color of preview equations.

- equation_background_color is the color of preview background.

- equation_inline/block_size is to adjust the font size of inline/block equations.

- auto_comile is an amazing feature, it will simultaneously compile the equations that users are writing and show it in the phantom.

- convert_binary is the path of `convert`, which is a part of imagemagick package.

- pdflatex_binary is the path of pdflatex executable.

- debug == 1 will show additional information in the console.
