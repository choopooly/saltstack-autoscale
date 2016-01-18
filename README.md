===================
saltstack-autoscale
===================

This is a fully deployable and auto-scalable stack, based on SaltStack, hosted on AWS.
The repository contains everything required to bootstrap & deploy minion.

The stack itself is composed of a load-blancer service (haproxy) and a web service (nginx). 
It also comes with its own trending system (based on graphite) which give the metrics/thresholds necessary to scale up/down webservices.

