from fabric.api import local, hosts, env, run

def provision_staging():
    local('ansible-playbook -i inventories/staging --ask-become-pass -v --ask-vault-pass provision.yml')

def provision_production():
    local('ansible-playbook -i inventories/production --ask-become-pass -vv --ask-vault-pass provision.yml')

def encode_credentials():
    local('')

# this fab do not execute directly normally;
# instead this line execute during vagrant provision via Vagrantfile
# use it only on debug or for problem resolution
def provision_vagrant():
    local('ansible-playbook -i inventories/vagrant --ask-become-pass -vv  --ask-vault-pass provision.yml ')
    #local('ansible-playbook -i inventories/vagrant --ask-become-pass -vv --skip-tags=vagrant_skip --ask-vault-pass provision.yml ')


# For use this feature, you must have hosts description in ~/.shh/config with following format:
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
    #git fetch origin
    #git reset --hard origin/master