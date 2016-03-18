# -*- mode: ruby -*-
# vi: set ft=ruby :


Vagrant.configure(2) do |config|

  config.vm.box = "ubuntu/wily64"

  config.vm.provider :virtualbox do |v|
    v.name = "pdfdevelop"
    v.memory = 1024
    v.cpus = 1
    v.gui = false

    # enable internet access
    #v.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]

    # enable ioapic http://serverfault.com/a/91867
    v.customize ["modifyvm", :id, "--ioapic", "on"]
  end


  # how login as different user http://stackoverflow.com/a/22648525
  # config.ssh.username = "swasher"

  # Set the name of the VM. See: http://stackoverflow.com/a/17864388/100134
  #  config.vm.define :pdfdevelop do |pdfdevelop|
  #  end

  #  config.vm.hostname = "pdfdevelop"

  config.vm.synced_folder ".", "/home/vagrant/pdfupload", id: "vagrant-root",
    owner: "vagrant",
    group: "vagrant",
    mount_options: ["dmode=775,fmode=664"]

  config.vm.synced_folder "D:\\!!print", "/home/vagrant/!!print",
    owner: "vagrant",
    group: "vagrant",
    mount_options: ["dmode=775,fmode=664"]


  # Share port for nginx
  #config.vm.network "forwarded_port", guest: 80, host: 8888
  #config.vm.network "public_network"
  #config.vm.network "private_network", type: "dhcp"
  config.vm.network :private_network, ip: "172.28.128.20"

  # for supress "stdin: is not a tty error"
  config.ssh.shell = "bash -c 'BASH_ENV=/etc/profile exec bash'"

  #   config.vm.provision "shell", inline: "sudo apt-get update -qq && sudo apt-get install python-dev libpython2.7-dev libyaml-dev mc -y -q"
  #   config.vm.provision "shell", inline: "curl -s https://bootstrap.pypa.io/get-pip.py | sudo python -"
  #   config.vm.provision "shell", inline: "sudo pip install ansible fabric"
  #   config.vm.provision "shell", privileged: false, inline: "cd pdfupload/provision && fab development provision"

  config.vm.provision "shell", inline: <<-SHELL
    export DEBIAN_FRONTEND=noninteractive
    sudo apt-get update -qq && sudo apt-get install python-dev libpython2.7-dev libyaml-dev mc -y -q
    curl -s https://bootstrap.pypa.io/get-pip.py | sudo python -
    sudo pip install ansible==1.9.4 fabric
  SHELL


    ###########
    #
    # OLD way

  config.vm.provision "shell", privileged: false,  inline: <<-SHELL
    cd pdfupload/provision && fab development provision
  SHELL


    ###########
    #
    # NEW way to launch provision - via ansible local
    # But due bug this is do not work until Vagrant 1.8.2 is come out

#   config.vm.provision "ansible_local" do |ansible|
#     ansible.playbook        = "provision/provision.yml"
#     ansible.inventory_path  = "provision/inventories/all"
#     ansible.skip_tags       = "vagrant_skip"
#     ansible.limit           = "development"
#   end


end
