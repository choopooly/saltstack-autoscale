
{% set registry = 'choopooly' %}
{% set image = 'grafana-graphite' %}
{% set tag = 'latest' %}

include:
  - docker
  - nginx

{# container management #}

{{ registry }}/{{ image }}:{{ tag }}:
  dockerng:
    - image_present

trends:
  dockerng:
    - running
    - image: {{ registry }}/{{ image }}
    - port_bindings:
      - 8080:80/tcp
      - 81:81/tcp
      - 2003:2003/tcp
    - volumes: /opt/graphite/storage/whisper
    - binds:
      -  /var/lib/docker/carbon-storage:/var/lib/graphite/storage/whisper:rw
    - watch_action: SIGHUP
    - require:
      - file: /var/lib/docker/carbon-storage
    - watch:
      - dockerng: {{ registry }}/{{ image }}:{{ tag }}

/var/lib/docker/carbon-storage:
  file:
    - directory

{# nginx config #}

/etc/nginx/conf.d/grafana.conf:
  file:
    - managed
    - template: jinja
    - user: root
    - group: root
    - mode: 440
    - source: salt://grafana/nginx.jinja2
    - require:
      - pkg: nginx

/etc/nginx/htpasswd:
  file:
    - managed
    - template: jinja
    - user: root
    - group: root
    - mode: 644
    - source: salt://grafana/htpasswd.jinja2
    - require:
      - pkg: nginx

extend:
  nginx:
    service:
      - watch:
        - file: /etc/nginx/conf.d/grafana.conf
        - file: /etc/nginx/htpasswd

