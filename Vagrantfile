# -*- mode: ruby -*-
# vi: set ft=ruby :

internal_ip = "172.28.128.20"
project_name = "pdfupload"

Vagrant.configure(2) do |config|

  # config.vm.box = "bento/ubuntu-16.10"
  config.vm.box = "boxcutter/ubuntu1610"
  config.vm.network "private_network", ip: internal_ip
  config.vm.hostname = project_name + 'dev'

  config.vm.provider :virtualbox do |v|
    v.name = project_name
    v.memory = 1024
    v.cpus = 1
    v.gui = false

    # enable internet access
    # v.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]

    # enable ioapic http://serverfault.com/a/91867
    # v.customize ["modifyvm", :id, "--ioapic", "on"]
  end

  # for supress "stdin: is not a tty error"
  config.ssh.shell = "bash -c 'BASH_ENV=/etc/profile exec bash'"

  config.vm.synced_folder ".", "/home/vagrant/pdfupload", id: "vagrant-root",
    owner: "vagrant",
    group: "vagrant",
    mount_options: ["dmode=775,fmode=664"]
    #type: "smb"

  config.vm.synced_folder "D:\\!!print", "/home/vagrant/!!print",
    owner: "vagrant",
    group: "vagrant",
    mount_options: ["dmode=775,fmode=664"]

  config.vm.provision "shell", inline: <<-SHELL
    export DEBIAN_FRONTEND=noninteractive
  SHELL
    #sudo apt-get update -qq
    #apt-get autoremove -y
    #sudo apt-get install python-dev libpython2.7-dev libyaml-dev mc -y -q
    #curl -s https://bootstrap.pypa.io/get-pip.py | sudo python -
    #sudo pip install fabric
    #sudo pip install ansible

  config.vm.provision "shell", privileged: false, inline: <<-SHELL
    mkdir --parents /home/vagrant/log
    touch /home/vagrant/log/ansible.log
  SHELL

  # Run Ansible inside the Vagrant VM
  config.vm.provision :ansible_local do |ansible|
    ansible.playbook       = "provision.yml"
    ansible.verbose        = "vv"
    ansible.install        = true
    ansible.install_mode   = 'pip'
    ansible.limit          = 'development'
    ansible.provisioning_path = "/home/vagrant/" + project_name + "/provision"
    ansible.inventory_path = "/home/vagrant/" + project_name + "/provision/inventories"
  end

end

# steps to add github key:
# - copy securely stored private github key to ~/.ssg/github
# - chmod 600 ~/.ssg/github
# - enable ssh-agent: eval "$(ssh-agent -s)"
# - add key to agent: ssh-add ~/.ssh/github
# - now you can git push origin master without password