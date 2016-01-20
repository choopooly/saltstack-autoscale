docker package dependencies:
  pkg.installed:
    - pkgs:
      - apt-transport-https
      - iptables
      - ca-certificates
      - lxc
      - python-apt

docker package repository:
  pkgrepo.managed:
    - name: deb https://apt.dockerproject.org/repo {{ grains["os"]|lower }}-{{ grains["oscodename"] }} main
    - humanname: {{ grains["os"] }} {{ grains["oscodename"]|capitalize }} Docker Package Repository
    - keyid: f76221572c52609d
    - keyserver: keyserver.ubuntu.com
    - file: /etc/apt/sources.list.d/docker.list
    - refresh_db: True
    - require_in:
      - pkg: docker-engine
    - require:
      - pkg: docker package dependencies

docker-engine:
  pkg:
    - installed

docker-service:
  service.running:
    - name: docker
    - enable: True
    - watch:
      - pkg: docker-engine

docker-py requirements:
  pkg.installed:
    - name: python-pip
  pip.installed:
    - name: pip
    - upgrade: True

docker-py:
  pip.installed:
    - name: docker-py
    - require:
      - pkg: docker-engine
      - pip: docker-py requirements
    - reload_modules: True

