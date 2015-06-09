# -*- mode: ruby -*-
# vi: set ft=ruby :


Vagrant.configure(2) do |config|

  config.vm.box = "ubuntu/vivid64"

  config.vm.provider :virtualbox do |v|
    v.name = "pdfdevelop"
    v.memory = 1024
    v.cpus = 1

    # enable internet access
    #v.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]

    # enable ioapic http://serverfault.com/a/91867
    v.customize ["modifyvm", :id, "--ioapic", "on"]
  end


  # how login as different user http://stackoverflow.com/a/22648525
  # config.ssh.username = "swasher"

  #  config.vm.hostname = "pdfdevelop"
  #  config.vm.network :private_network, ip: "192.168.0.90"

  # Set the name of the VM. See: http://stackoverflow.com/a/17864388/100134
  #  config.vm.define :pdfdevelop do |pdfdevelop|
  #  end


  config.vm.synced_folder ".", "/home/vagrant/pdfupload", id: "vagrant-root",
    owner: "vagrant",
    group: "vagrant",
    mount_options: ["dmode=775,fmode=664"]


  # Share port for nginx
  config.vm.network "forwarded_port", guest: 80, host: 8888
  #config.vm.network "public_network"
  config.vm.network "private_network", type: "dhcp"


  config.vm.provision "shell", inline: "sudo apt-get install python-dev python-pip mc -y"
  config.vm.provision "shell", inline: "sudo pip install ansible"
  config.vm.provision "shell", inline: "ansible-playbook -i /home/vagrant/pdfupload/provision/inventories/vagrant /home/vagrant/pdfupload/provision/provision.yml -v --ask-become-pass --skip-tags=vagrant_skip --ask-vault-pass"

end
