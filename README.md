Requirements
--------------------------

- PyPDF2==1.24
- fabric==1.10.2
- Django==1.9.2
- django-debug-toolbar==1.4
- django-bootstrap3==6.2.2
- git+git://github.com/sehmaschine/django-grappelli #2.8.1
- django-bootstrap3-datetimepicker-2==2.4.2
- django-crispy-forms==1.6.0
- rq==0.5.6
- rq-dashboard==0.3.6
- django-rq==0.9.0
- pillow==3.1.1
- django-nvd3==0.9.7
- reportlab==3.3.0
- pdfminer==20140328

Overview
--------------------------

Обслуживание производится на четырех узлах:

- development - машина разработчика, развернутая в vagrant (master node в терминологии ansible)
- production - собственно сервер с системой
- staging - машина для тестирования деплоя
- backup - сервер для бекапа базы данных

Установка производится с помощью менеджера конфигурций Ansible. Ключи создаются вручную. Для доступа
от production до backup используется ключ без пасс-фразы.

Директория provision содержит все необходимое для автоматического развертывания с помощью Ansible.
Файл provision/provision.yml содержит подробные инструкции, как создать staging/production систему
или окружение для разработки (development).

Все операции проводятся внутри vagrant.

>Внимание:
>При запуске ansible локальные файлы не используются, все файлы берутся с гита! Поэтому перед
>запуском provision нужно не забыть сделать push!

Playbook requirements:

- ubuntu/debian based system
- systemd daemon manager


Before provision
====================================

Set Ansible variables
-------------------------------

Перед развертывание нужно произвести настройку переменных в папке group_vars. Она содержит следующие файлы:

- `all.yml` - основной файл с настройками. Приватные данные указаны как ссылки на `vault.yml`
- `vault.yml` - приватные данные, хранящиеся в VCS в зашифрованном виде
- `production`,
- `staging`,
- `development` - эти файлы содержат FQDN и remote_user для соотв. узлов.


The trick:
Так как Ansible не работает под Microsoft Windows, плейбук запускается ВНУТРИ поднятого vagrant-бокса.

> TODO Когда выйдет vagrant 1.8.2, можно будет попробовать запускать провизию через новый плагин ansible-local
> В версии 1.8.1 имеется критический баг

Есть некая условность (hardcoded) в именовании узлов - они должны называться production, staging, developing
и backup соответственно.
Именно такие константы используются в навании Ansible groups, в fabric, в настройках django-settings,
в файле [ssh]config для запуска Ansible, etc.


Create keys on master node
--------------------------------------------------------

До запуска провижена необходимо создать ключи (если они отсутствуют):

    $ ssh-keygen -t rsa -C "your_email@example.com"

Эта пара ключей будет доставлена на все узлы.

Provision
====================================

Creating development node
---------------------------------------

Clone project from github:

    $ git clone https://github.com/swasher/pdfupload.git

Start vagrant box from project dir:

    $ vagrant up

Connect to vagrant and generate ssh keys:

    $ vahrant ssh
    $ ssh-keygen -t rsa

That's all!

**Some details:**

Due bug in vagrant/ansible, there is error happens when asking sudo password during vagrant provision.
Thread: [one](https://github.com/geerlingguy/JJG-Ansible-Windows/issues/3),
[two](https://github.com/mitchellh/vagrant/issues/2924),
[three](https://github.com/mitchellh/vagrant/issues/3396) with: "Guest-based provisioning cannot support interactive prompts (in Vagrant 1.x at least)".
So we connect to box via ssh first, and then start provision INSIDE the vagrant box.

Creating [staging|production] server:
---------------------------------------------------------

- create fresh ubuntu machine on ESXi (testing on 15.10). During install select `OpenSSH Server`.
- [optional] set up custom ssh port in /etc/ssh/sshd-config
- [optional] if using DHCP, setting up static IP for new server (on router)
- setup FQDN resolution for name of new server in local network (via router or hosts file). Name must be [staging|production]
- reboot machine
- on ansible master machine, write the connection data to provision/group_vars/all.yml. Please attention, that there is many variables stored
in crypted vault `vault.yml`
- on develping machine, copy ssh key to target machine: ssh-copy-id [staging|production]
- start provision: `fab staging provision`
- deploy code: `fan staging deploy`



Deploy
======================================

Deploy code
--------------------------------------

Деплой выполняется одной командой fabric:

    $ cd provision
    $ fab [staging|production] deploy
    
При этом база данных не затрагивается. Сначала выполняется деплой на тестовый сервер, тестируется, потом деплоится на
рабочий. Если во время тестирования на тестовом сервере что-то пошло не так, то перед следующей попыткой деплоя нужно
привести тестовый сервер в состояние, идентичное рабочему (production) серверу:

    $ fab restore_staging

Эта команда выполнит зеркалирование приложения с production на staging, включая так же копирование баз данных.

Deploy data
--------------------------------------

> TODO

Misc
=====================================

Хотфолдер и обработчик incrontab
----------------------------

Когда в хотфолдер падает файл, запускается обработчик incrontab, и событие ставится в очередь rq.

Создаем директорию-хотфолдер. Может находится в корне проекта и иметь название `input`. Изменяется в `settings.py`.

    $ cd pdfupload
    $ mkdir input
    
Открываем доступ в хотфолдер, примерный конфиг для samba:

    [pdfupload-django]
    comment = pdfupload-django
    path = /home/swasher/pdfupload/input
    browsable =yes
    writable = yes
    guest ok = yes
    read only = no

Создаем событие inotify через incrontab (`incrontab -e`), из-под непривелигированного пользователя, который
был добавлен в `incron.allow`:

    /home/swasher/pdfupload/input IN_CLOSE_WRITE python /home/swasher/pdfupload/putting_job_in_the_queue.py $#

Файл putting_job_in_the_queue.py создает запись в очереди. В нем должны быть настройки, чтобы интерпретатор питон
понял, что это код джанго. В последней строке вызывается вьюха джанго, и в нее передается параметр - имя файла.

    import os
    import sys
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pdfupload.settings")
    from django.conf import settings

    import django_rq
    import workflow.views

    pdfName = sys.argv[1]

    django_rq.enqueue(workflow.views.processing, filename=pdfName)


Обработчик события rq
----------------------

Используется библиотека очередей rq. Это более простой аналог Celery. После того, как файл 
попадает в хот фолдер, задание добавляется в очередь.

Затем задание обрабатывается функцией processing во `views.py`, для чего ее оборачивают в декоратор @job.

    @job
    def processing(pdfName):
        # do something with pdfname

Чтобы запустить обработчик очереди в консоли, используется команда

    $ python manage.py rqworker default

Для автоматического запуска менеджера очередей в 'uwsgi.ini' добавляется строка

    attach-daemon = python /home/swasher/pdfupload/manage.py rqworker default
    
Так же можно поставить rq-dashboard, и наблюдать за происходящим в консоли

    $ rqinfo
     
или в браузере на порту 9181, запустив 

    $ rq-dashboard

Настраиваем uwsgi, emperor и nginx
-------------------------------------

##### nginx

Связку wsgi+вебсервер можно использовать любую, я использую uWSGI+nginx. 

Примерный конфиг для nginx. Не забываем создать нужные пути, для логов например.

    server {
        server_name pdf.site.ua;
        access_log  /home/swasher/pdfupload/logs/nginx-access.log  compression;
        error_log   /home/swasher/pdfupload/logs/nginx-error.log info;
    
        location / {
            uwsgi_pass 127.0.0.1:49001;
            include uwsgi_params;
        }
    
        location /media/ {
            alias /home/swasher/pdfupload/media/;
            expires 30d;
        }
    
        location /static/ {
            alias /home/swasher/pdfupload/static_root/;
            expires 30d;
        }
    }

##### uWSGI

В корне проекта лежит файл настроек uWSGI. Так же проверяем пути. Последней строкой автоматически запускается 
менеджер очередей rq. `/home/swasher/pdfupload/uwsgi.ini`:

    [uwsgi]
    # set PYTHONHOME/virtualenv. Comment if no virtual environment
    #home=/home/swasher/production/blacklist
    chdir=/home/swasher/pdfupload
    master=True
    disable-logging=True
    vacuum=True
    pidfile=/tmp/pdfupload.pid
    max-requests=5000
    socket=127.0.0.1:49001
    processes=2
    
    # Path to python interpreter if using virt. envir., otherwise '..'
    pythonpath=..
    env=DJANGO_SETTINGS_MODULE=pdfupload.settings
    #module = django.core.handlers.wsgi:WSGIHandler()
    module = django.core.wsgi:get_wsgi_application()
    touch-reload=/tmp/pdfupload.reload
    attach-daemon = python /home/swasher/pdfupload/manage.py rqworker default

Поле 'touch-reload' указывает на файл, запись в который приводит к перезапуску клиента супервизора. В данном случае,
команда

    $ touch /tmp/pdfupload.reload
    
приведет к перезапуску uWSGI сервера.


##### Supervisor

**DEPRECATED: use uwsgi emperor instead**

В конфиг `supervisord.conf` изменения вносить не нужно. Создаем только файл конфигурации для нашего 
питон-приложения `/etc/supervisor/conf.d/pdfupload.conf`:

    [program:pdfupload]
    command=uwsgi /home/swasher/pdfupload/uwsgi.ini
    stdout_logfile=/home/swasher/pdfupload/logs/uwsgi.ini
    stderr_logfile=/home/swasher/pdfupload/logs/uwsgi_err.ini
    autostart=true
    autorestart=true
    redirect_stderr=true
    stopwaitsecs = 60
    stopsignal=INT
    user=swasher

##### Uwsgi emperor

В ubuntu можно поставить uwsgi через менеджер пакетов apt, и тогда вместе с ним ставится
и демон emperor. Но uwsgi там не самый свежий, поэтому мы будем ставим его через pip.

В Ubuntu 15.04 на смену upstart пришел systemd. Как настроить автозапуск emperor
подробно описано [тут](http://uwsgi.readthedocs.org/en/latest/Systemd.html?highlight=emperor)

Вкратце, в `/etc/uwsgi/` нужно создать файл `emperor.ini`, в котором написано, где будут лежать конфиги
вассалов, и от какого юзера запускать их.

Далее, в `/etc/systemd/system/` нужно создать конфиги `emperor.uwsgi.service` и `emperor.uwsgi.socket`.
Подробно по ссылке выше, рабочие конфиги в `provision/roles/uwsgi`

Методика анализа
====================================

В скрипте применяется анализ файла, основанный на метках signastation и имени файла. 
В отдельных местах есть возможность альтерантивной методики детектирования.

    - Параметр: Тип файла
    - Использование: входная проверка.
    - Signa: Расширение файла должно быть pdf, тип файла (утилита file) должен быть pdf
    - Non-Signa: то же
    - Else: FAIL
    
    
    - Параметр: File creator
    - Использование: входная проверка
    - Signa: File creator должен быть 'PrinectSignaStation'
    - Non-Signa: warning
    
    
    - Параметр: Печатная машина  
    - Использование: Куда слать превью; Папка для заливки; Размер клапана для кропа в бумагу; 
                     Кому слать sms;
    - Signa: специальная метка в спуске, которая явно содержит название печаной машины. 
             Должно совпадать с моделью PrintingPress.name
    - Non-Signa: FAIL
    
    
    - Параметр: Кол-во комплектов
    - Использование: Пишется в базу
    - Signa: утилитой pdfinfo
    - Non-Signa: утилитой pdfinfo
    
    
    - Параметр: Количество плит
    - Использование: Пишется в базу; Может использоваться для переименования файла. 
                     Строгий параметр для отчетности
    - Signa: Основывается на теге 'HDAG_ColorantNames', пишется в пдф Сигной, от меток не зависит. 
             При пересохранении сохраняется. Используется PyPDF2.
    - Non-Signa: возвращает ноль
    
    
    - Параметр: Кто выводит пластины
    - Использование: Используется для заливки на фтп; Для отчетности;
    - Signa: Тэг в имени файла; Должно соответствовать полю Outputter.name.
    - Non-Signa: то же
    
    
    - Параметр: Куда заливать файл; Куда заливать превью
    - Использование: Файл заливается на вывод; Компрессированное превью заливается для просмотра печатнику.
    - Signa: 
    - Non-Signa: 
    
    
    - Параметр: Размер бумаги
    - Использование: Для кропа превью
    - Signa: тестовая метка, сожержащая размеры бумаги; пропадает при пересохранении документа
    - Non-Signa: None; однако затем crop() использует размер на основе ghostscript -sDEVICE=bbox


USE CASE
----------------------

Кнопка в шапке меняют режимы работы. При включении `import mode` получаемые файлы
обрабатываются и заносятся в базу, но на фтп не отсылаются, а дата заливки берется как
дата создания файла.


TROUBLESHOOTING
-----------------------

Куда смотреть, если что-то не работает:

- запустить джанго в командной строке и посмотреть браузером: `python manage.py runserver 0.0.0.0:8080`
- можно перезапустить nginx командой `pdfupload_restart.sh`
- запускаем `rq-dashboard`, смотрим браузером в порт 9181
- руками запустить python `path/to/putting_job_in_the_queue.py <filename>.pdf`. Помогает при ошибках компиляции скрипта.


ERROR (in uwsgi log)

The translation infrastructure cannot be initialized before the
django.core.exceptions.AppRegistryNotReady: The translation infrastructure cannot be
initialized before the apps registry is ready. Check that you don't make non-lazy gettext
calls at import time.

SOLUTION

I always see the solution after reporting a bug. The fix (in uwsgi.ini):
Change
module = django.core.handlers.wsgi:WSGIHandler()
to
module = django.core.wsgi:get_wsgi_application()
in the vassal.ini



  [мануал]: http://python-rq.org/patterns/supervisor/