"""
Cloudify plugin for running a simple bash script.

Operations:
    start: Run a script
"""
import urllib
import subprocess
import fcntl
import select
import os
import errno
from cosmo.events import send_event as send_riemann_event
from cloudify.utils import get_local_ip, get_manager_ip
from cloudify.decorators import operation
from cloudify.manager import set_node_started

get_ip = get_local_ip
send_event = send_riemann_event


@operation
def start(__cloudify_id, ctx, port=8080, **kwargs):
  logger = ctx.logger
  # See in context.py
  # https://github.com/CloudifySource/cosmo-celery-common/blob/develop/cloudify/context.py
  logger.info('ctx.node_id=%s' % ctx.node_id)
  logger.info('ctx.blueprint_id=%s' % ctx.blueprint_id)
  logger.info('ctx.deployment_id=%s' % ctx.deployment_id)
  logger.info('ctx.execution_id=%s' % ctx.execution_id)
  logger.info('ctx.properties=%s' % ctx.properties)
  # loggger.info('ctx.runtime_properties=%s' % ctx.runtime_properties)
  logger.info('get_manager_ip()=%s' % get_manager_ip())

  execute('env', ctx)

  start_sh = download_blueprint_file('start.sh', ctx)
  bash(start_sh, ctx)

  set_node_started(ctx.node_id, get_ip())


def bash(path, ctx):
  return execute('/bin/bash %s' % path, ctx)


def execute(command, ctx):
  ctx.logger.info('Running command: %s' % command)
  env = setup_environment(ctx)
  process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             env=env)
  make_async(process.stdout)
  make_async(process.stderr)

  stdout = str()
  stderr = str()
  return_code = None

  while True:
    # Wait for data to become available
    select.select([process.stdout, process.stderr], [], [])

    # Try reading some data from each
    stdoutPiece = read_async(process.stdout)
    stderrPiece = read_async(process.stderr)

    if stdoutPiece:
      ctx.logger.info(stdoutPiece)
    if stderrPiece:
      ctx.logger.error(stderrPiece)

    stdout += stdoutPiece
    stderr += stderrPiece
    return_code = process.poll()

    if return_code is not None:
      break

  ctx.logger.info('Done running command (return_code=%d): %s' % (return_code, command))
  if (return_code == 0):
    return stdout
  else:
    raise ProcessException(command, return_code, stdout, stderr)


# Helper function to add the O_NONBLOCK flag to a file descriptor
def make_async(fd):
  fcntl.fcntl(fd, fcntl.F_SETFL, fcntl.fcntl(fd, fcntl.F_GETFL) |
              os.O_NONBLOCK)


# Helper function to read some data from a file descriptor,
# ignoring EAGAIN errors
def read_async(fd):
  try:
    return fd.read()
  except IOError, e:
    if e.errno != errno.EAGAIN:
      raise e
    else:
      return ''


def setup_environment(ctx):
  '''Add some useful environment variables to the environment'''
  env = os.environ.copy()
  env['CLOUDIFY_NODE_ID'] = ctx.node_id
  env['CLOUDIFY_BLUEPRINT_ID'] = ctx.blueprint_id
  env['CLOUDIFY_DEPLOYMENT_ID'] = ctx.deployment_id
  env['CLOUDIFY_manager_ip'] = get_manager_ip()
  env['CLOUDIFY_EXECUTION_ID'] = ctx.execution_id
  for k, v in ctx.properties:
    env['CLOUDIFY_PROPERTY_%s' % k] = v
  return env


class ProcessException(Exception):
  def __init__(self, command, exit_code, stdout, stderr):
    Exception.__init__(self, stderr)
    self.command = command
    self.exit_code = exit_code
    self.stdout = stdout
    self.stderr = stderr


def download_blueprint_file(blueprint_file, ctx):
  ip = get_manager_ip()
  port = 53229
  # blueprint_id = ctx.blueprint_id
  blueprint_id = '5fc21ca7-767f-47a1-8c22-8a91ff1dc02f'
  url = 'http://%s:%d/blueprint-%s/%s' % (ip, port, blueprint_id, blueprint_file)
  return download(url, ctx.logger)


def download(http_file_path, logger):
  '''downloads a file to the local disk and returns it's disk path'''
  try:
    filename, header = urllib.urlretrieve(http_file_path)
    logger.info("Downloaded %s to %s" % (http_file_path, filename))
    return filename
  except IOError as e:
    logger.error("Error downloading file %s. %s" % (http_file_path, e))
    return None
