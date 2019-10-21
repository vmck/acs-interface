# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  if Vagrant.has_plugin?("vagrant-env")
    config.env.enable
  end

  config.vm.box = "base"
  config.nfs.functional = false
  config.smb.functional = false

  config.vm.provision "shell", path: "ci/provision-cluster.sh", privileged: false
  config.vm.provision "shell", path: "ci/provision-vmck.sh", privileged: false
  config.vm.provision "shell", path: "ci/provision-acs-interface.sh", privileged: false

  config.vm.provider :vmck do |vmck|
    vmck.image_path = 'imgbuild-cluster.qcow2.tar.gz'
    vmck.vmck_url = ENV['VMCK_URL']
    vmck.memory = 2048
    vmck.cpus = 2
    vmck.name = ENV['VMCK_NAME']
  end

end
