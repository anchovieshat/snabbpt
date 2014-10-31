from markdown import Markdown
import sys
import codecs

class Template:
    def __init__(self, html):
        self.html = html
    def from_file(filename):
        with codecs.open(filename, mode="r", encoding="utf-8") as file:
            return Template(file.read())
    def render(self, file):
        with codecs.open(file.title + '.html', mode="w", encoding="utf-8", errors="xmlcharrefreplace") as out:
            out.write(self.html.replace("{{PAGE-TITLE}}", file.title).replace("{{PAGE-CONTENT}}", file.html))

class File:
    def __init__(self, filename):
        self.filename = filename

        with codecs.open(self.filename, mode="r", encoding="utf-8") as input_file:
            text = input_file.read()

        self.md = Markdown(extensions=["markdown.extensions.meta"])
        self.html = self.md.convert(text)
        self.title = self.md.Meta["title"][0]
        self.template = self.md.Meta["template"][0]

class Renderer:
    def __init__(self):
        self.templates = {}
    def renderFile(self, filename):
        file = File(filename)
        if file.template not in self.templates:
            self.templates[file.template] = Template.from_file(file.template + '.html')
        self.templates[file.template].render(file)

Renderer().renderFile(str(sys.argv[1]))
