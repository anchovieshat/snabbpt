from markdown import Markdown
import sys
import codecs
import os
import errno

def ensure_output_exists(dir):
    if not os.path.isdir(dir):
        try:
            print("mkdir", dir)
            os.makedirs(dir)
        except OSError as e:
            raise SnabbptException("Unable to create output directory") from e


class SnabbptException(Exception):
    pass

class HTMLTemplate:
    def __init__(self, html):
        self.html = html

    def from_file(filename):
        with codecs.open(filename, mode="r", encoding="utf-8") as file:
            return HTMLTemplate(file.read())

    def render(self, file, outfile):
        with codecs.open(outfile, mode="w", encoding="utf-8", errors="xmlcharrefreplace") as out:
            out.write(self.html.replace("{{PAGE-TITLE}}", file.title).replace("{{PAGE-CONTENT}}", file.html))

class File:
    def __init__(self, filename):
        self.filename = filename

        with codecs.open(self.filename, mode="r", encoding="utf-8") as input_file:
            text = input_file.read()

        self.md = Markdown(extensions=["markdown.extensions.meta"])
        self.html = self.md.convert(text)
        self.title = self.md.Meta["title"][-1]
        self.template = self.md.Meta["template"][-1]
        self.output_path = "{0}/{1}.html".format(os.path.dirname(self.filename), self.title)

    def __str__(self):
        return self.filename

class Renderer:
    def __init__(self, outDir):
        self.templates = {}
        self.outDir = outDir

        ensure_output_exists(outDir)

    def renderDir(self, path):
        if not os.path.isdir(path):
            raise SnabbptException("{0} is not a directory".format(path))
        for file in self.get_files(path):
            self.renderFile(os.path.join(path, file))

    def get_files(self, path):
        files = []
        for file in os.listdir(path):
            if file.startswith('.'):
                continue
            if os.path.isdir(file) and file != self.outDir:
                files.extend(list(map(lambda x: os.path.normpath(os.path.join(path, file, x)), self.get_files(os.path.join(path, file)))))
            elif file.endswith(".md"):
                files.append(file)
        return files

    def renderFile(self, filename):
        file = File(filename)
        if file.template not in self.templates:
            ext = file.template.split('.')[-1].upper()
            if ext not in fileTypes:
                raise SnabbptException("Invalid template type: {0}".format(ext))
            self.templates[file.template] = fileTypes[ext].from_file(file.template)

        input_file = file.filename
        output_file = os.path.join(self.outDir, file.output_path)
        try:
            if os.stat(input_file).st_mtime < os.stat(output_file).st_mtime:
                print(file, "is up to date")
                return
        except:
            pass

        ensure_output_exists(os.path.dirname(output_file))

        print("{0} -> {1}".format(input_file, output_file))
        self.templates[file.template].render(file, output_file)

fileTypes = {
        "HTML":  HTMLTemplate,
        }

if __name__ == "__main__":
    try:
        Renderer(str(sys.argv[2])).renderDir(str(sys.argv[1]))
    except SnabbptException as e:
        if e.__cause__:
            print("{0} ({1})".format(e, e.__cause__))
        else:
            print(e)
