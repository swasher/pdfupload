Installation
--------------------------

Установка производится с помощью менеджера конфигурций Ansible.

Директория provision содержит все необходимое для автоматического провижиона с помощью Ansible.
Файл provision/provision.yml содержит подробные инструкции, как создать staging/production систему
или окружение для разработки.

Внимание:
При запуске ansible локальные файлы не используются, все файлы берутся с гита! Поэтому перед
запуском provision нужно не забыть сделать push!

The trick:
Так как Ansible не работает под виндовс, провижн запускается ВНУТРИ поднятого vagrant-бокса.

TODO зделать отдельно - развертывание из среды разработки и развертывание только с гитхаба

Steps to reproduce new server:

- create fresh ubuntu machine on ESXi (testing on 15.04). During install select `OpenSSH Server`.
- write down custom ssh port to /etc/ssh/sshd-config
- on router assign appropriate static IP for new machine
- Reboot
- Copy ssh key from 'ansible' machine to target machine: ssh-copy-id [user]@[server-ip] -p [server-port]
- Note: Provision assumes, that pdfupload machine is dedicated server, so python package will install system-wide.
        This is due high load on file system during pdf processing.


Steps to recreate local development environment

- BUG 1: невозможно создать файл в шаред фолдер
- BUG 2: невозможно интерактивный ввод-вывод


- install pycharm, git for windows, virtualbox, vagrant with ubuntu/vivid64
- download box with Ubuntu 15.04: `vagrant box add ubuntu/vivid64`
- clone project from github: `git clone https://github.com/swasher/pdfupload.git`
- using PowerShell, start vagrant box from project dir: `vagrant up`

- due bug in vagrant/ansible, there is error happens when asking sudo password during vagrant provision.
- --- Folk: [one](https://github.com/geerlingguy/JJG-Ansible-Windows/issues/3) [two](https://github.com/mitchellh/vagrant/issues/2924) [and at last](https://github.com/mitchellh/vagrant/issues/3396) with: "Guest-based provisioning cannot support interactive prompts (in Vagrant 1.x at least)"
- --- so first we connect to box via ssh, and then start provision INSIDE. 
- enter vagrant box: `vagrant ssh`
- start provision: `cd pdfupload/provision && fab provision_local`

- generate keys: `ssh-keygen -t rsa`
- TODO fill ~/.shh/config as described in fabfile

Development tools tunung:

- git
--- ensure `C:\Program Files (x86)\Git\etc\gitconfig` have `autocrlf = false` (git doesn't process files)
- pycharm
--- settings -> editor -> file encodings -> project and default encoding -> utf-8
--- settings -> editor -> code style -> line separator -> unix and osx

- add string to your hosts file or adjustment your router: [machine-ip] [machine-fqdn], where fqdn from group_vars
- vault magic word hint: b-0

TODOes and temporary solution:
- owner of uwsgi process set to normal user, not www-data, due www-data can't write to tty1, even it is in tty group

Deploy
--------------------

TODO

Install by hand
--------------------

Установка выполняется с использование ansible. Ниже описано, как установить вручную.

Установка требует следующих шагов:

- Установка
- Настройка конфигов
- Обработчик incrontab
- Доступ по samba
- uWSGI, emperor и nginx

##### Забираем репозиторий

    $ git clone https://github.com/swasher/pdfupload.git
    
и создаем директорию для логов
    
    $ mkdir pdfupload/logs

##### Устанавливаем зависимости
    
    $ sudo apt-get install redis-server
    $ pip install -r requirements.txt
    $ deactivate

Ставим incrontab, и разрешаем пользователю управлять им:    

    $ sudo apt-get install incron
    $ sudo echo <username> >> /etc/incron.allow
    
В корень проекта необходимо положить библиотеку для отправки sms. Используется smsc.ua, файл API по адресу http://smsc.ua/api/python/
нужно положить в workflow/smsc_api.py

Для отрисовки графиков нужно поставить nvd3. Можно через bowler, но я ставил руками:

    pip install sudo pip install django-nvd3
    --> Successfully installed django-nvd3 python-nvd3 python-slugify Unidecode

settings.py
    
    INSTALLED_APPS = (
        'django_nvd3',
        )

Далее c http://nvd3.org/ скачиваем архив и копируем:

    src -> static_root/nvd3/src
    lib/d3.v2.min.js -> static_root/d3/d3.min.js

Тут нужно переименовать, django-nvd3 видимо использовал первую версию.

##### Запись в tty

Чтобы скрипт мог выводить служебную информацию в терминал, нужно, чтобы пользователь, от имени которого запускается
скрипт, имел право записи в /dev/tty1. В дебиан/убунту tty1 имеет владельца root:tty, нужно добавить юзера в группу tty:
    
    $ sudo adduser $USER dialout  
    
После этого, пользователь должен перелогинится. Кроме того, пользователь должен быть обязательно прилогинен к терминалу tty1 (например, в консоли vSphere).

Настройка конфигов
--------------------

В `settings.py` проверяем настройки базы, менеджера очередей rq, а также наличие SECRET_KEY

    from settings_secret import *

    INSTALLED_APPS = (
        ...
        'django_rq',
    )

    ...

    RQ_QUEUES = {
         'default': {
         'HOST': 'localhost',
         'PORT': 6379,
         'DB': 0,
         },
    }


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

##### Supervisor DEPRECATED; use uwsgi emperor instead

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
-----------------------

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
    - Non-Signa: по границам найденных объектов; утилитой pdfcrop.pl
    
Важные TODO
-----------------------

По неизвестной причине не удалось научить юзера www-data писать в tty1, хотя обычный юзер пишет туда замечательно после
внесения его в группу tty. Поэтому uwsgi запускается от обычного непривилегированного пользователя, а не от www-data.

TROUBLESHOOTING
-----------------------

Куда смотреть, если что-то не работает:

- запустить джанго в командной строке и посмотреть браузером: `python manage.py runserver 0.0.0.0:8080`
- отчет о работе в реальном времени пишется в локальную консоль сервера /dev/tty1. Проверить, в какую консоль сейчас видим можно командой `who -m`
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