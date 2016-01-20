highstate_run:
  local.state.highstate:
    - tgt: {{ data['name'] }}

{% if data['name'].startswith("web-") %}
update_lbs:
  local.state.highstate:
    - tgt: lb-*
{% endif %}
