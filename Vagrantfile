# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  if Vagrant.has_plugin?("vagrant-env")
    config.env.enable
  end

  config.vm.box = "base"
  config.nfs.functional = false
  config.smb.functional = false

  config.vm.synced_folder "..", "/opt/acs-interface", type: "rsync"

  config.vm.provision 'hello', type: 'shell', path: "ci/set-up.sh"

  config.vm.provider :vmck do |vmck|
    vmck.image_path = 'imgbuild-cluster.qcow2.tar.gz'
    vmck.vmck_url = ENV['VMCK_URL']
    vmck.memory = 1024
    vmck.cpus = 1
    vmck.name = ENV['VMCK_NAME']
  end

end
