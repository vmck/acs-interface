# <oregano.nomad.Provider object at 0x10a399a50>
provider "nomad" {
  address = "http://10.42.2.1:4646"
  version = "~> 1.4"
}

# <oregano.nomad.Job object at 0x10a38ced0>
resource "nomad_job" "acs-interface" {
  jobspec = "${file("${path.module}/../interface.nomad")}"
}

