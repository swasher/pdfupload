from fabric.api import local, hosts, env

def provision_staging():
    local('ansible-playbook -i inventories/staging --ask-become-pass provision.yml -vvv')

def provision_production():
    local('ansible-playbook -i inventories/production --ask-become-pass provision.yml -vv')

# this fab do not execute directly;
# instead this line execute during vagrant provision via Vagrantfile
def provision_vagrant():
    local('ansible-playbook -i inventories/vagrant --ask-become-pass provision.yml -vv --skip-tags=vagrant_skip')