Deploy
--------------------------

Установка требует следующих шагов:

- Установка
- забираем репозиторий
- устанавливаем зависимости
- настройка конфигов
- создаем обработчик incrontab
- доступ по samba
- настраиваем uwsgi, supervisor и nginx

Желательно использование virtualenv, в данном тексте для упрощения используется system-wide.

Установка
--------------------

##### virtualenv

В домашней директории создаем окружение:

    $ virtualenv uploadsite
    $ cd uploadsite
    $ source bin/active

##### Забираем репозиторий

    $ git clone https://github.com/swasher/pdfupload.git
    
Создаем директорию-хотфолдер. Она должна находится в корне проекта и иметь название `input`. Изменяется в `settings.py`.

    $ cd pdfupload
    $ mkdir input
    
Директория для логов
    
    $ mkdir logs

##### Устанавливаем зависимости
    
    $ sudo apt-get install redis-server
    $ pip install -r requirements.txt
    $ deactivate

Ставим incrontab, и разрешаем пользователю управлять им:    

    $ sudo apt-get install incron
    $ sudo echo <username> >> /etc/incron.allow

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

Создаем обработчик incrontab
----------------------------

Создаем событие inotify через incrontab (`incrontab -e`), из-под непривелигированного пользователя, который
был добавлен в `incron.allow`:

    /home/swasher/pdfupload/input IN_CLOSE_WRITE python /home/swasher/pdfupload/putting_job_in_the_queue.py $#

Файл putting_job_in_the_queue.py создает запись в очереди. В нем должны быть настройки, чтобы интерпретатор питон
понял, что это код джанго. В последней строке вызывается вьюха джанго, и в нее передается параметр.

    import os
    import sys
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pdfupload.settings")
    from django.conf import settings

    import django_rq
    import workflow.views

    pdfName = sys.argv[1]

    django_rq.enqueue(workflow.views.testing, filename=pdfName)

Доступ по Samba
---------------------------------

Открываем доступ в хотфолдер, примерный конфиг для samba:

    [pdfupload-django]
    comment = pdfupload-django
    path = /home/swasher/pdfupload/input
    browsable =yes
    writable = yes
    guest ok = yes
    read only = no
    
Когда в эту директорию падает файл, запускается обработчик incrontab, событие ставится в очередь rq и обрабатывается - 

Обработчик события
------------------

Используется библиотека очередей rq. Это более простой аналог Celery.

Во вьюхе мы запускаем обработчик файла - функцию testing, переданного через параметр:

    @job
    def processing(pdfName):
        # do something with pdfname

Чтобы запустить обработчик очереди в консоли, используется команда

    $ python manage.py rqworker default

Для автоматического запуска менеджера очередей в uwsgi.ini добавляется строка

    attach-daemon = python /home/swasher/pdfupload/manage.py rqworker default
    
Так же можно поставить rq-dashboard, и наблюдать за происходящим в консоли

    $ rqinfo
     
или в браузере на порту 9181, запустив 

    $ rq-dashboard

Настраиваем uwsgi, supervisor и nginx
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


TROUBLESHOOTING
-----------------------

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