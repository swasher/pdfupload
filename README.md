Deploy
--------------------------

Установка требует следующих шагов:

- забираем репозиторий
- устанавливаем зависимости
- настройка конфигов
- создаем обработчик incrontab
- доступ по samba
- настраиваем uwsgi, supervisor и nginx

Желательно использование virtualenv, в данном тексте для упрощения используется system-wide.

Забираем репозиторий
---------------------

    ::console
    $ git clone https://github.com/swasher/pdfupload.git
    
Создаем директорию-хотфолдер. Она должна находится в корне проекта и иметь название `input`. Изменяется в `settings.py`.

    ::console
    $ cd ~/pdfupload
    $ mkdir input

Устанавливаем зависимости
--------------------------
    
    ::console
    $ sudo apt-get install reddis-server
    $ sudo pip install -r requirements.txt
    
    $ sudo apt-get install incron
    $ sudo echo <username> >> /etc/incron.allow

Настройка конфигов
--------------------

В `settings.py` проверяем настройки базы, менеджера очередей rq, а также наличие SECRET_KEY

    ::python
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

    ::python
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

Во вьюхе мы запускаем обработчик файла - функцию testing, переданного через параметр:

    @job
    def processing(pdfName):
        # do something with pdfname

Чтобы запустить обработчик очереди в консоли, используется команда

    $ python manage.py rqworker default

Для атоматического запуска в uwsgi.ini добавляется строка

    attach-daemon = python /home/swasher/pdfupload/manage.py rqworker default

Или с помощью супервизора http://python-rq.org/patterns/supervisor/

Так же можно поставить pip install rq-dashboard, и наблюдать за происходящим в консоли
($rqinfo), или в браузере на порту 9181 ($rq-dashboard)

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