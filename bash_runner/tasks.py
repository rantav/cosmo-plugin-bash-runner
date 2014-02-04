"""
Cloudify plugin for running a simple bash script.

Operations:
    start: Run a script
"""
import urllib
from cosmo.events import send_event as send_riemann_event
from cloudify.utils import get_local_ip, get_manager_ip
from cloudify.decorators import operation
from cloudify.manager import set_node_started

get_ip = get_local_ip
send_event = send_riemann_event

@operation
def start(__cloudify_id, ctx, port=8080, **kwargs):
  # See in context.py
  # https://github.com/CloudifySource/cosmo-celery-common/blob/develop/cloudify/context.py
  log(ctx, 'ctx.node_id=%s' % ctx.node_id)
  log(ctx, 'ctx.blueprint_id=%s' % ctx.blueprint_id)
  log(ctx, 'ctx.deployment_id=%s' % ctx.deployment_id)
  log(ctx, 'ctx.execution_id=%s' % ctx.execution_id)
  log(ctx, 'ctx.properties=%s' % ctx.execution_id)
  # log(ctx, 'ctx.runtime_properties=%s' % ctx.runtime_properties)
  log(ctx, 'get_manager_ip()=%s' % get_manager_ip())
  set_node_started(ctx.node_id, get_ip())
  # send_event(__cloudify_id, get_ip(), "bash_runner status", "state", "running")


def download(http_file_path, ctx):
  try:
    filename, header = urllib.urlretrieve(http_file_path)
    log(ctx, "Downloaded %s to %s" % (http_file_path, filename))
    return filename
  except IOError as e:
    ctx.logger.error("Error downloading file %s. %s" % (http_file_path, e))
    return None

def log(ctx, s):
  with open('/home/ubuntu/hello', 'ab+') as f:
    print >> f, s
  ctx.logger.info(s) # /var/log/celery/celecy.log
