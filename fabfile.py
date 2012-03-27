import os
from fabric.api import local, env, put
from fabric.operations import _shell_escape, output

HOME = os.getenv('HOME')

#env.hosts = ['ubuntu@ec2-67-202-25-15.compute-1.amazonaws.com']
#env.key_filename = [
#    '%s/AeroFS/JESS3/keys/keymaster.pem' % HOME,
#]

def run(command, shell=True, pty=True):
    """
    Helper function.
    Runs a command with SSH agent forwarding enabled.

    Note:: Fabric (and paramiko) can't forward your SSH agent.
    This helper uses your system's ssh to do so.
    """
    real_command = command
    if shell:
        cwd = env.get('cwd', '')
        if cwd:
            cwd = 'cd %s && ' % _shell_escape(cwd)
        real_command = '%s "%s"' % (env.shell,
            _shell_escape(cwd + real_command))
    if output.debug:
        print("[%s] run: %s" % (env.host_string, real_command))
    elif output.running:
        print("[%s] run: %s" % (env.host_string, command))
    local("ssh -Ai %s %s '%s'" % (env.key_filename[0], env.host_string, real_command))


def devserver(port=8000, bind='0.0.0.0'):
    local('python placecorg.py %s %s' % (bind, port))

