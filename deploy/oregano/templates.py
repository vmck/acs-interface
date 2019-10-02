from pathlib import Path
import jinja2


template_dir = Path(__file__).resolve().parent / 'templates'

env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(str(template_dir)),
    variable_start_string='%{',
    variable_end_string='}',
    undefined=jinja2.StrictUndefined,
)


def render(name, context={}):
    return env.get_template(name).render(context)
