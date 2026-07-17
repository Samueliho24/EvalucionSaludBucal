from jinja2 import Environment, FileSystemLoader
from os.path import dirname, abspath, join

dir = dirname(abspath(__file__))
jinja = Environment(loader=FileSystemLoader(dir))

def directed_loop(a, b, reverse):
	return range(a, b + 1) if not reverse else reversed(range(a, b + 1))

html = jinja.get_template("form.jinja.html").render(directed_loop=directed_loop)
with open(join(dir, "assets", "form.html"), "w", encoding="utf-8") as f:
	f.write(html)
