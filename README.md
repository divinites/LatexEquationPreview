# LatexEquationPreview

## Introduction

This plug-in make use of the new feature of Sublime Text, Phantom, to preview latex equations.

**ATTENTION**

This plug-in need `imagemagick` and `texlive/mactex` installed. otherwise it does not work.

## Usage

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

## Configuration

```json
{
    "equation_foreground_color": "yellow",
    "equation_background_color": "",
    "equation_size": "45%",
    "picture_width": "",
    "convert_binary": "",
    "pdflatex_binary": "",
    "debug": 1
}

```
- equation_foreground_color is the

