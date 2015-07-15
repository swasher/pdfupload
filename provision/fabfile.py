# --- coding: utf-8 ---

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


# def staging():
#     env.hosts = ['staging']

# def production():
#     env.hosts = ['production']

# def development():
#     env.hosts = ['development']


def provision():
    additional_params = '--skip-tags=vagrant_skip' if env.hosts[0] == 'development' else ''

    # Do you want verbose output from ansible? Uncomment it.
    # additional_params += ' -vvv'

    local('ansible-playbook -i inventories/all --ask-become-pass {additional_params} --limit {target} '
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

        # after pip install, run collectstatic

        # then run test
        #run('python manage.py test myapp')


@hosts('staging')
def restore_staging():
    run('rsync -avz --delete production:{0} {1}'.format('/home/swasher/pdfupload', '~'))
    run('rsync -avz --delete production:{0} {1}'.format('/home/swasher/media', '~'))

    run('sudo -u postgres dropdb --if-exists pdfuploaddb')
    run("sudo -u postgres createdb --encoding='UTF-8' --owner=swasher --template=template0 pdfuploaddb")
    run('pg_dump -h production pdfuploaddb | psql pdfuploaddb')

    run('touch /tmp/pdfupload')


@hosts('production')
def restore_db():
    exit('\nV E R Y   D A N G E R O U S!!!\n==============================\nComment out this line in fabric to drop production DB and load data from backup server!\n')
    #run('sudo -u postgres dropdb --if-exists pdfuploaddb')
    #run("sudo -u postgres createdb --encoding='UTF-8' --owner=swasher --template=template0 pdfuploaddb")
    run('ssh staging cat ???DB??? | psql pdfuploaddb')