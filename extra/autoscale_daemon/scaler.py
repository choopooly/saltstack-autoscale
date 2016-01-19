#!/usr/bin/env python

import sys
import uuid
import requests
import logging

import salt.client

root = logging.getLogger()
root.setLevel(logging.WARNING)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.WARNING)
format = "'%(asctime)s - %(name)s - %(levelname)s - %(message)s'"
formatter = logging.Formatter(format)
ch.setFormatter(formatter)
root.addHandler(ch)


def scale_up():
    """
    Send request to salt-api to scale up.
    """
    logging.debug("Scaling up.")
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
        logging.warning("Deploying node: %s-%s" % (role, node_id))
    else:
        logging.warning("Something went wrong contacting salt-master")


def scale_down(instance):
    """
    Send request to salt-api to scale down.
    """
    logging.debug("Scaling down %s." % (instance))
    # send request to salt-master
    url = "http://localhost:8000/hook/scale_down"
    data = {'name': instance}

    try:
        r = requests.post(url, data=data)
    except requests.ConnectionError, e:
        print e
        sys.exit(1)

    if r.ok:
        logging.warning("Removing node: %s" % (instance))
    else:
        logging.warning("Something went wrong contacting salt-master")


def check_autoscale():
    """
    From salt.mine get web nodes details.
    """
    caller = salt.client.Caller()
    data = caller.function('mine.get', '*', 'network.ip_addrs')
    nodes = data.keys()

    if len(nodes) == 0:
        logging.warning('No node found, scaling up the stack.')
        scale_up()
    elif len(nodes) == 1:
        logging.info('Nodes pool is at the minimum, no scaling down possible.')
        scaling_logic(nodes)
    elif len(nodes) == 4:
        logging.warning('Nodes pool already have the max members.')
    else:
        scaling_logic(nodes)


def scaling_logic(nodes):
    """
    Scaling policy, based on the nodes average requests value
    """
    scaling_up_value = 100
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
            logging.critical('Average number is not yet define')
            sys.exit(1)

        avglist.append(num)

    totalavg = sum(avglist) / len(nodesdict.keys())
    logging.debug('requests handled total average: %i' % (totalavg))

    # define if scaling is necessary
    if totalavg >= scaling_up_value:
        scale_up()
    elif totalavg <= scaling_down_value:
        if len(nodes) == 1:
            logging.info('Pool is at the minimum, no scaling down possible.')
        else:
            instance = nodes[-1]
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
    logging.debug('Node: %s, return value: %s' % (node, avg))
    return avg

if __name__ == '__main__':
    check_autoscale()
