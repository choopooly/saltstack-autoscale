{% set postdata = data.get('post', {}) %}

spin_down_web_machines:
  runner.cloud.destroy:
    - instances:
      - {{ postdata.name }}
