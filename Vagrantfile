# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  if Vagrant.has_plugin?("vagrant-env")
    config.env.enable
  end

  config.vm.box = "base"
  config.nfs.functional = false
  config.smb.functional = false

  config.vm.provision "shell", path: "ci/provision-system.sh", binary: true, privileged: false
  config.vm.provision "shell", path: "ci/provision-cluster.sh", binary: true, privileged: false
  config.vm.provision "shell", path: "ci/provision-vmck.sh", binary: true, privileged: false
  config.vm.provision "shell", path: "ci/provision-acs-interface.sh", binary: true, privileged: false

  config.vm.provider :vmck do |vmck|
    vmck.image_path = 'imgbuild-cluster.qcow2.tar.gz'
    vmck.vmck_url = ENV['VMCK_URL']
    vmck.memory = 2048
    vmck.cpus = 2
    vmck.name = ENV['VMCK_NAME']
  end

  config.vm.provider "virtualbox" do |vb, override|
    override.vm.box = "hashicorp/bionic64"
    config.vm.network :forwarded_port, guest: 4646, guest_ip: "10.66.60.1", host: 4646, host_ip: "127.0.0.1"
    config.vm.network :forwarded_port, guest: 8500, guest_ip: "10.66.60.1", host: 8500, host_ip: "127.0.0.1"
    config.vm.network :forwarded_port, guest: 8200, guest_ip: "10.66.60.1", host: 8200, host_ip: "127.0.0.1"
    config.vm.network :forwarded_port, guest: 10000, guest_ip: "10.66.60.1", host: 10000, host_ip: "127.0.0.1"
    config.vm.network :forwarded_port, guest: 8000, guest_ip: "10.66.60.1", host: 8000, host_ip: "127.0.0.1"
    config.vm.network :forwarded_port, guest: 9000, guest_ip: "10.66.60.1", host: 9000, host_ip: "127.0.0.1"
    vb.memory = "2048"
  end

end
