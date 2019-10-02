{% for component in components -%}
# %{"%r"|format(component)}
%{component.render()}

{% endfor %}
