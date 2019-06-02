VAGRANTFILE_API_VERSION = "2"

unless Vagrant.has_plugin?("vagrant-hostsupdater")
  raise "This project requires the `vagrant-hostsupdater` plugin (https://git.io/vNhwP)!"
end

unless Vagrant.has_plugin?("vagrant-vbguest")
  raise "This project requires the `vagrant-vbguest` plugin (https://git.io/viqkc)!"
end

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "ubuntu/xenial64"
  config.vm.network :private_network, ip: "192.168.100.200"
  config.vm.hostname = "example.local"
end
