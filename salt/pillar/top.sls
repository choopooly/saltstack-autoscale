base:
  '*':
    - prod.common
  'lb-*':
    - prod.lb
  'web-*':
    - prod.web
  'graph*':
    - prod.trends
