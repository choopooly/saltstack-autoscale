/usr/local/bin/autoscaler.py:
  file:
    - managed
    - source: salt://roles/master/scaler.py
    - user: root
    - group: root
    - mode: 700
  cron.present:
    - user: root
    - minute: '*/{{ salt['pillar.get']('autoscale:cronjob', '5') }}'
    - watch:
      - file: /usr/local/bin/autoscaler.py
