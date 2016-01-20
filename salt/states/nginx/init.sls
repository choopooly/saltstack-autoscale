{% set bad_configs = ('default', 'virtual') %}
{% set config_paths = ('conf.d', 'sites-enabled', 'sites-available') %}


nginx:
  pkg:
    - installed
  service:
    - running
    - enable: true
    - watch:
{%- for filename in bad_configs %}
  {% for path in config_paths %}
      - file: /etc/nginx/{{ path }}/{{ filename }}
    {% endfor %}
{%- endfor %}

{% for filename in bad_configs %}
  {% for path in config_paths %}
/etc/nginx/{{ path }}/{{ filename }}:
  file:
    - absent
    - require:
      - pkg: nginx
  {% endfor %}
{% endfor %}
