{% if data['name'].startswith("web-") %}
highstate_run:
  local.state.highstate:
    - tgt: lb-*
{% endif %}
