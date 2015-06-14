from fabric.api import local, hosts, env, run

def provision_staging():
    local('ansible-playbook -i inventories/staging --ask-become-pass --ask-vault-pass provision.yml')

def provision_production():
    local('ansible-playbook -i inventories/production --ask-become-pass -vv --ask-vault-pass provision.yml')

def provision_local():
    #local('ansible-playbook -i inventories/vagrant -v provision.yml ')
    local('ansible-playbook -i inventories/vagrant -vv --skip-tags=vagrant_skip provision.yml ')

# For use this feature, you must have hosts description at ansible machine in ~/.shh/config with following format:
# Host staging
#     HostName 111.222.333.444
#     Port 22000
#     User fooey
#
# Then we can us deploy as `fab staging deploy` or `fab production deploy`

env.use_ssh_config = True

def staging():
    env.hosts = ['staging']

def production():
    env.hosts = ['production']

def deploy():
    run('uname -a')
    run('pwd')
    #run('git fetch origin')
    #run('git reset --hard origin/master')
