"""Inject results.json into template.html.
  index.html     standalone page for GitHub Pages
  artifact.html  the same page without the document wrapper, for publishing as a claude.ai artifact"""
import json
page = open("template.html").read().replace("/*DATA*/null", json.dumps(json.load(open("results.json")), separators=(",", ":")))
open("artifact.html", "w").write(page)
open("index.html", "w").write('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n' + page.replace("<style>", "</head>\n<body>\n<style>", 1) + "\n</body>\n</html>\n")
