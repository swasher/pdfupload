from fabric.api import local, hosts, env, run
from fabric.context_managers import cd
from fabric.api import settings

# For use server names, you must have hosts description at ansible machine in ~/.shh/config with following format:
# Host staging
#     HostName 111.222.333.444
#     Port 22000
#     User fooey
#
# Then we can us deploy as `fab staging deploy` or `fab production deploy`


# USAGE
# fab [staging|production|vagrant] [provision|deploy]
#

env.use_ssh_config = True
env.project_path = '/home/swasher/pdfupload'



def staging():
    env.hosts = ['staging']

def production():
    env.hosts = ['production']

def development():
    env.hosts = ['development']


def provision():
    additional_params = '--skip-tags=vagrant_skip' if env.hosts[0] == 'development' else ''

    # Do you want verbose output from ansible? Uncomment it.
    #additional_params += ' -v'

    local('ansible-playbook -i inventories/{target} --ask-become-pass {additional_params} '
          'provision.yml'.format(target=env.hosts[0], additional_params=additional_params))


def testing():
    local('ansible-playbook -i inventories/{target} --ask-become-pass -vv testing.yml'.format(target=env.hosts[0]))


def deploy():
    with cd(env.project_path):
        run('git fetch origin')
        run('git reset --hard origin/master')
        run('sudo pip install -r requirements.txt')
        run('python manage.py migrate')
        run('touch /tmp/pdfupload.reload')

        # then run test
        #run('python manage.py test myapp')

        # also, we need reinstall requirements.txt due to new package may be used

@hosts('production')
def staging_restore():
    env.hosts = ['staging']
    #with settings(user='swasher', host_string='192.168.0.203', port='22522'):
    #env.hosts = ['production']

    run('hostname -f')
    staging()
    run('echo {}')
    print(env.port)

    with settings(hosts='staging'):
        run('hostname -f')

def parsing():
    from os.path import expanduser
    from paramiko.config import SSHConfig

    def hostinfo(host, config):
        hive = config.lookup(host)
        if 'hostname' in hive:
            host = hive['hostname']
        if 'user' in hive:
            host = '%s@%s' % (hive['user'], host)
        if 'port' in hive:
            host = '%s:%s' % (host, hive['port'])
        return host

    try:
        config_file = file(expanduser('~/.ssh/config'))
    except IOError, e:
        print(e)
    else:
        config = SSHConfig()
        config.parse(config_file)
        keys = [config.lookup(host).get('identityfile', None) for host in env.hosts]
        env.key_filename = [expanduser(key) for key in keys if key is not None]
        env.hosts = [hostinfo(host, config) for host in env.hosts]

        for role, rolehosts in env.roledefs.items():
            env.roledefs[role] = [hostinfo(host, config) for host in rolehosts]