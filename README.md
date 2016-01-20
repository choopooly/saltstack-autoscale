===================
saltstack-autoscale
===================

This is a fully deployable and auto-scalable stack, based on SaltStack, hosted on AWS.
The repository contains everything required to bootstrap & deploy the minions.

The stack itself is composed of a load-blancer service (**haproxy**) and a web service (**nginx**). 
It also comes with its own trending system (based on graphite) which give the metrics/thresholds necessary to scale up/down webservices.


# Requirements
This stack have been deployed on AWS, inside a VPC, however no other AWS components are being used.
salt-master have been deployed using ec2-cli and bootstraped with [salt-bootstrap](https://github.com/saltstack/salt-bootstrap) and custom scripts.

Except those, everything will be deployed through salt-states.

# Components

## Salt-Cloud 

[Salt-Cloud](https://github.com/saltstack/salt-bootstrap) is reponsible to deploy and bootstrap salt-minions.
It supports differents cloud-providers, so you can start by editing */etc/salt/cloud.providers/<provider>.provider.conf* and */etc/salt/cloud.providers/<provider>.profiles.conf* with your own settings.

## Salt-Reactor

[Salt-Reactor](https://docs.saltstack.com/en/latest/topics/reactor/index.html) gives the ability to trigger actions in response to an event. It watch salt's event bus for event tags that match a given pattern and then running one or more commands in response. 

For example, **salt-reactor** will catch events sent by **salt-cloud** when instances have been fully deployed and then will trigger the state required.

*/etc/salt/master.d/reactor.conf*
```
reactor:
  - 'salt/cloud/*/created':
    - /srv/reactor/startup.sls
```

## Salt-Api
[Salt-Api](https://docs.saltstack.com/en/latest/ref/netapi/all/salt.netapi.rest_cherrypy.html) provides an interface to manage salt services. It will be used to send custom events to **salt-reactor** when we need to increase or decrease the number of instances as part of our auto-scalling policy.

_example:_
```
curl -sS localhost:8000/hook/scale_up -d name='web-03'
{"success": true}
```
## Salt-Mine
[Salt-Mine](https://docs.saltstack.com/en/latest/topics/mine/) collects data from **salt-minions** and made them available to the others.
The pool of web services will be exposed through salt-mine so the services can loop into them and configure their services accordingly.

_salt-mine output example:_
```
lb-01:
    ----------
    web-6eb00b47:
        - 172.31.31.72
    web-9ec9a7b4:
        - 172.31.31.75
```

_Sample of haproxy's config template:_
```
{%- for server, addrs in salt['mine.get']('web-*', 'network.ip_addrs').items() %}
    server {{ server }} {{ addrs[0] }}:80 check
{%- endfor %}
```

## HAProxy
[HAProxy](http://www.haproxy.org) acts as a proxy and a load-balancer for the web servers behind.

## Trends Monitoring
[Diamond](https://github.com/BrightcoveOS/Diamond) is a metric collector and send intermittently its data to **Graphite**.
[Graphite](http://graphite.readthedocs.org/en/latest/index.html) provides a time-series data storage, and a render API to visualize metrics trends.
[Grafana](http://docs.grafana.org) is a webapp that provides a visualization for **Graphite** data.

## autoscaler.py
The [autoscaler.py](https://github.com/choopooly/saltstack-autoscale/blob/master/salt/states/roles/master/scaler.py) is a python script that provides autoscaling functionality.

It's based on those 3 features:
* **Reporter** give a status of the stack, by querying **graphite api** for specific metrics.
* **Decider** evaluate the state of a Reporter to make a scaling decision.
* **Scaler** perform scale-up and scale-down actions on **salt-api**.

Here is a visualization of the autoscalling policy.
![Overview](http://i.imgur.com/1FUTAfP.png)
