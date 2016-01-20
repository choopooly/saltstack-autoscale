/usr/local:
  file:
    - directory
    - name: /usr/local/bin
    - makedirs: True
    - user: root
    - group: root
    - mode: 755

/usr/local/src:
  file:
    - directory
    - user: root
    - group: root
    - mode: 755
    - require:
      - file: /usr/local

/usr/local/share:
  file:
    - directory
    - user: root
    - group: root
    - mode: 755
    - require:
      - file: /usr/local

