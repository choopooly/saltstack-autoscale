haproxy.config:
 file.managed:
   - name: {{ salt['pillar.get']('haproxy:config_file_path', '/etc/haproxy/haproxy.cfg') }}
   - source: salt://haproxy/templates/config.jinja
   - template: jinja
   - user: root
   - group: root
   - mode: 644
   - watch_in:
     - service: haproxy.service
