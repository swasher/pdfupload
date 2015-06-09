from fabric.api import local, hosts, env

def provision_staging():
    local('ansible-playbook -i inventories/staging --ask-become-pass -vv --ask-vault-pass provision.yml')

def provision_production():
    local('ansible-playbook -i inventories/production --ask-become-pass -vv --ask-vault-pass provision.yml')

# this fab do not execute directly;
# instead this line execute during vagrant provision via Vagrantfile
def provision_vagrant():
    local('ansible-playbook -i inventories/vagrant --ask-become-pass -vv --skip-tags=vagrant_skip --ask-vault-pass provision.yml ')