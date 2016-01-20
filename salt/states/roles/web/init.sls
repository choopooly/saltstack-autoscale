include:
  - nginx

/etc/nginx/conf.d/webapp.conf:
  file:
    - managed
    - template: jinja
    - source: salt://roles/web/nginx.jinja2
    - user: root
    - group: www-data
    - mode: 440
    - require:
      - pkg: nginx
      - file: /usr/share/webapp/index.html
    - watch_in:
      - service: nginx

/usr/share/webapp/index.html:
  file:
    - managed
    - template: jinja
    - source: salt://roles/web/index.jinja2
    - user: www-data
    - group: www-data
    - mode: 644
    - makedirs: True
    - watch_in:
      - service: nginx


