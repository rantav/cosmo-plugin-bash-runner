"""
Cloudify plugin for running a simple bash script.

Operations:
    start: Run a script
"""

from celery import task
from cosmo.events import send_event as send_riemann_event
from cloudify.utils import get_local_ip


get_ip = get_local_ip
send_event = send_riemann_event


@task
def start(__cloudify_id, port=8080, **kwargs):
  with open('/home/ubuntu/hello', 'w') as f:
    print >> f, 'HELLO BASH! %s' % port
  send_event(__cloudify_id, get_ip(), "hello_bash status", "state", "running")
