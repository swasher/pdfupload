from fabric.api import local, hosts, env, run
from fabric.context_managers import cd

# ####### DPRECATED
# def provision_staging():
#     local('ansible-playbook -i inventories/staging --ask-become-pass provision.yml')
#
# def provision_production():
#     local('ansible-playbook -i inventories/production --ask-become-pass -vv provision.yml')
#
# def provision_local():
#     #local('ansible-playbook -i inventories/vagrant -v provision.yml ')
#     local('ansible-playbook -i inventories/vagrant -vv --skip-tags=vagrant_skip provision.yml ')
#######################

# For use this feature, you must have hosts description at ansible machine in ~/.shh/config with following format:
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

def vagrant():
    env.hosts = ['develop']


def provision():
    additional_params = '--skip-tags=vagrant_skip' if env.hosts == 'vagrant' else ''
    local('ansible-playbook -i inventories/{machine} --ask-become-pass -v {additional_params} provision.yml'.format(machine=env.hosts[0], additional_params=additional_params))


def deploy():
    with cd(env.project_path):
        run('git fetch origin')
        run('git reset --hard origin/master')
        run('touch /tmp/pdfupload.reload')
