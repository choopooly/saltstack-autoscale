{% set postdata = data.get('post', {}) %}

spin_up_more_web_machines:
  runner.cloud.profile:
    - prof: nano_ec2
    - instances:
      - {{ postdata.name }}
