#!/usr/bin/env python

import sys
import uuid
import requests
import logging
import logging.handlers

import salt.client

# syslog handler settings
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
handler = logging.handlers.SysLogHandler(address='/dev/log')
format = '%(module)s.%(funcName)s: %(levelname)s - %(message)s'
formatter = logging.Formatter(format)
handler.setFormatter(formatter)
log.addHandler(handler)


def scale_up():
    """
    Send request to salt-api to scale up.
    """
    log.debug("Scaling up.")
    # generate uuid
    node_id = uuid.uuid4()
    role = "web-"
    full_id = role + str(node_id)

    # send request to salt-master
    url = "http://localhost:8000/hook/scale_up"
    data = {'name': full_id}

    try:
        r = requests.post(url, data=data)
    except requests.ConnectionError, e:
        print e
        sys.exit(1)

    if r.ok:
        log.warning("Deploying node: %s-%s" % (role, node_id))
    else:
        log.warning("Something went wrong contacting salt-master")


def scale_down(instance):
    """
    Send request to salt-api to scale down.
    """
    log.debug("Scaling down %s." % (instance))
    # send request to salt-master
    url = "http://localhost:8000/hook/scale_down"
    data = {'name': instance}

    try:
        r = requests.post(url, data=data)
    except requests.ConnectionError, e:
        print e
        sys.exit(1)

    if r.ok:
        log.warning("Removing node: %s" % (instance))
    else:
        log.warning("Something went wrong contacting salt-master")


def check_autoscale():
    """
    From salt.mine get web nodes details.
    """
    caller = salt.client.Caller()
    data = caller.function('mine.get', '*', 'network.ip_addrs')
    nodes = data.keys()

    if len(nodes) == 0:
        log.warning('No node found, scaling up the stack.')
        scale_up()
    elif len(nodes) == 1:
        log.info('Nodes pool is at the minimum, no scaling down possible.')
        scaling_logic(nodes)
    elif len(nodes) == 4:
        log.warning('Nodes pool already have the max members.')
    else:
        scaling_logic(nodes)


def scaling_logic(nodes):
    """
    Scaling policy, based on the nodes average requests value
    """
    scaling_up_value = 50
    scaling_down_value = 25
    nodesdict = {}
    avglist = []

    for node in nodes:
        trend = get_trends(node)
        nodesdict[node] = trend

    # sum up all nodes trends values
    for num in nodesdict.itervalues():
        try:
            num = int(num)
        except TypeError:
            log.critical('Average number is not yet define')
            sys.exit(1)

        avglist.append(num)

    totalavg = sum(avglist) / len(nodesdict.keys())
    log.debug('requests handled total average: %i' % (totalavg))

    # define if scaling is necessary
    if totalavg >= scaling_up_value:
        scale_up()
    elif totalavg <= scaling_down_value:
        if len(nodes) == 1:
            log.info('Pool is at the minimum, no scaling down possible.')
        else:
            instance = nodes[0]
            scale_down(instance)


def get_trends(node):
    """
    Get average trends for nginx req_handled metric
    """
    # call salt pillar to get graphite host
    caller = salt.client.Caller()
    pillar = caller.sminion.functions['pillar.item']('graphite_address')
    graphite = pillar.values()[0]

    # build url
    last_min = "5"
    query = '%s.os.nginx.req_handled,"%smin","avg",false' % (node, last_min)
    url = ('http://%s/graphite/render?target=summarize(%s)'
           '&from=-%sminutes'
           '&until=now'
           '&format=json'
           % (graphite, query, last_min))

    # graphite api call
    try:
        r = requests.get(url)
    except requests.ConnectionError, e:
        print e
        sys.exit(1)

    feed = r.json()
    avg = feed[0]['datapoints'][0][0]

    # return
    log.debug('Node: %s, return value: %s' % (node, avg))
    return avg

if __name__ == '__main__':
    check_autoscale()
