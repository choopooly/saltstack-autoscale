include:
  - prod.common

roles: lb

haproxy:
  enabled: True
  config_file_path: /etc/haproxy/haproxy.cfg
  global:
    maxconn: 4096
  instances:
    webapp:
      mode: http
      port: 80
      backends:
        nodes:
          mode: http
          balance: roundrobin
          additional:
            - option forwardfor
