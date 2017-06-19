# --- coding: utf-8 ---

from fabric.api import local, hosts, env, run, task
from fabric.context_managers import lcd


# For use server names, we must have hosts description at any machine in ~/.shh/config with following format:
# Host hostname
#     HostName 111.222.333.444
#     Port 22000
#     User fooey
#
# Then we can us deploy as `fab staging deploy` or `fab production deploy`

env.use_ssh_config = True
env.project_path = '/home/swasher/pdfupload'

def staging():
    env.hosts = ['staging']

def production():
    env.hosts = ['production']

def development():
    env.hosts = ['development']


def github():
    local('ssh-add ~/.ssh/github')


@hosts('production')
def backup_production_db():
    run("pg_dump 'pdfuploaddb' | ssh swasher@backup \'cat > ~/pdfupload/dump_`date +\%d.\%m.\%Y-\%H.\%M.\%S`_extraordinary\'")


def provision():
    """
    Install needed software, source code and databases on clean machine.
    Use this for initially setup provision/staging/deployment.
    Development environment must run inside Vagrant box.

    Usage:
    fab [development|staging|production] provision
    """
    #additional_params = ' -v '
    additional_params = ' '

    if env.hosts[0] == 'development':
        additional_params += " --skip-tags 'prod' "

    if env.hosts[0] == 'staging' or env.hosts[0] == 'production':
        additional_params += " --skip-tags 'dev' "

    with lcd('provision'):
        local('ansible-playbook -i inventories/all --limit {target} {additional_params} provision.yml'.
            format(target=env.hosts[0], additional_params=additional_params))


def deploy():
    """
    Deploy latest source code from github to staging or provision server.
    Quick deploy - only fetch source code.

    Usage:
    fab [staging|production] deploy
    """

    additional_params = ''
    # additional_params += '-vvv '

    with lcd('provision'):
        local('ansible-playbook -i inventories/all --limit {target} {additional_params} deploy.yml'.
            format(target=env.hosts[0], additional_params=additional_params))


def full_deploy():
    """
    Deploy latest source code from github to staging or provision server.
    Full deploy - include recreate virtual environment, bower dependencied, collect static, migrate, etc

    Usage:
    fab [staging|production] full_deploy
    """

    additional_params = ''
    # additional_params += '-vvv '

    with lcd('provision'):
        local('ansible-playbook -i inventories/all --limit {target} {additional_params} full_deploy.yml'.
            format(target=env.hosts[0], additional_params=additional_params))


@hosts('staging')
def restore_staging():
    """
    Make staging server as mirror of production (source code and db)

    Usage:
    fab restore_staging
    """

    # run('rsync -avz --delete production:{0} {1}'.format('/home/swasher/pdfupload', '~'))
    # run('rsync -avz --delete production:{0} {1}'.format('/home/swasher/static_root', '~'))
    #
    # # раскомментировать, если нужно скопировать БД и ресурсы с prod на staging
    # run('rsync -avz --delete production:{0} {1}'.format('/home/swasher/media', '~'))
    # run('sudo -u postgres dropdb --if-exists pdfuploaddb')
    # run("sudo -u postgres createdb --encoding='UTF-8' --owner=swasher --template=template0 pdfuploaddb")
    # run('pg_dump -h production pdfuploaddb | psql pdfuploaddb')
    #
    # run('touch /tmp/pdfupload')

    with lcd('provision'):
        local('ansible-playbook -i inventories/all --limit staging restore_staging.yml')


def restore_db_from_backup():
    """
    Copy from Backap Server to target.

    Usage:
    fab [development|staging|production] restore_db_from_backup
    """

    if env.hosts[0] == 'production':
        prompt("\nV E R Y   D A N G E R O U S!!!\n==============================\n" +
               "It will destroy production  DB and then restore if from backup server.\nIf you are sure, type 'yes'",
               key='answer', default='no')
        if env.answer != 'yes':
            exit('Terminate.')

    additional_params = '-v'
    #additional_params += '--skip-tags=vagrant_skip ' if env.hosts[0] == 'development' else ''
    #additional_params += '-vvv '

    with lcd('provision'):
        local('ansible-playbook -i inventories/all --limit {target} {additional_params} restore_db_from_backup.yml'.
            format(target=env.hosts[0], additional_params=additional_params))

# === end of useful task


def testing():
    additional_params = '--skip-tags=vagrant_skip' if env.hosts[0] == 'development' else ''
    with lcd('provision'):
        local('ansible-playbook -i inventories/all --limit {target} -vvv testing.yml'.format(target=env.hosts[0]))


def replicate_db(source, target):
    """
    Replicate database from source to destination
    :param source:
    :param target:
    :return:
    """
    pass

    # something like
    # pg_dump -C -h remotehost1 -U remoteuser1 db_name | psql remotehost2 -U remoteuser2 db_name

"""
def access_to_backup_server():
    if ключей нет:
        ssh-keygen
    ssh-import-id user@backupip
"""


# deprecated; now use ansible's deploy
# def deploy():
#     """
#     Deploy source code to production/staging
#
#     Usage:
#     fab [staging|production] deploy
#     """
#     with cd(env.project_path):
#         run('git fetch origin')
#         run('git reset --hard origin/master')
#         run('bower install')
#         run('sudo pip install -r requirements.txt')
#         run('python manage.py collectstatic --noinput --clear --verbosity 1')
#         run('python manage.py migrate')
#         run('touch /tmp/pdfupload.reload')
#         run('echo `date +"%H:%m %d.%m.%Y"` > stamp')
#         # then run test
#         #run('python manage.py test myapp')

# deprecated; now use ansible's restore_db_from_backup
# def restore_db():
#     """
#     Restore DB from latest backup.
#
#     Usage:
#     fab [staging|production|development] restore_db
#     """
#
#     prompt('\nV E R Y   D A N G E R O U S!!!\n==============================\n'
#            'Type `yes` for delete current DB and restore this one from backup server\n', key='answer', default='no')
#
#     if env.answer != 'yes':
#         exit('Terminate.')
#
#     sudo('dropdb --if-exists pdfuploaddb', user='postgres')
#     sudo('createdb --encoding=\'UTF-8\' --owner=swasher --template=template0 pdfuploaddb', user='postgres')
#
#     latest_backup = local('ssh backup ls -rt /home/swasher/pdfupload | tail -1', capture=True)
#
#     print 'latest backup =', latest_backup
#
#     with hide('output'):
#         run('ssh backup cat /home/swasher/pdfupload/{} | psql pdfuploaddb'.format(latest_backup))


# deprecated; now use ansible's restore_db_from_backup
# def restore_local_db():
#     """
#     Restore DB from latest backup.
#     It's very ugly copy of restore_local_db, becouse command for remote and local side are different (local and
#
#     Usage:
#     fab [staging|production|development] restore_db
#     """
#
#     prompt('\nV E R Y   D A N G E R O U S!!!\n==============================\n'
#            'Type `yes` for delete current DB and restore this one from backup server\n', key='answer', default='no')
#
#     if env.answer != 'yes':
#         exit('Terminate.')
#
#     sudo('dropdb --if-exists pdfuploaddb', user='postgres')
#     sudo('createdb --encoding=\'UTF-8\' --owner=swasher --template=template0 pdfuploaddb', user='postgres')
#
#     latest_backup = local('ssh backup ls -rt /home/swasher/pdfupload | tail -1', capture=True)
#
#     print 'latest backup =', latest_backup
#
#     with hide('output'):
#         run('ssh backup cat /home/swasher/pdfupload/{} | psql pdfuploaddb'.format(latest_backup))
