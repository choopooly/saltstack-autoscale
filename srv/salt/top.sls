base:
  '*':
    - common
  'lb-*':
    - roles.lb
  'web-*':
    - roles.web
  'graph-*':
    - roles.trends
