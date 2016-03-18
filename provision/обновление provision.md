Из таска git удалена задача clone
-------------------------------------

причина: код на машину не нужно устанавливать в момент провижена, но в момент деплоя.
Пока это делается через фабрик fab [machine] deploy. Если деплой будет делаться через
ансибл, то для этого нужно создать отдельный таск. Общий принцип: провижн не трогает код,
а только создает среду выполнения.

Что было в clone.yml

---
# Determine if a project path exists and is a directory.  Note that we need to test
# both that p.stat.isdir actually exists, and also that it's set to true
- stat: path={{project_root}}
  register: p
- debug: msg="Project dir exists"
  when: p.stat.isdir is defined and p.stat.isdir


# skip clone if {{project_root}} already exist OR installing on vagrant (develper) machine
- git: repo={{project_repo}}
       dest={{project_root}}
       accept_hostkey=yes
  when: not p.stat.isdir is defined
  tags: vagrant_skip


environment
---------------------------------------

Сделать метку каждой машины в /etc/environment -> DJANGO_ENVIRONMENT=production

vagrant skip
---------------------------------------

Это хак, который изменяет поведение провижина при разворачивании среды разработки в вагранте.
От него желательно избавиться