# <nomad.Provider 'http://10.42.2.1:4646'>
provider "nomad" {
  address = "http://10.42.2.1:4646"
  version = "~> 1.4"
}

# <nomad.Job 'acs-interface'>
resource "nomad_job" "acs-interface" {
  jobspec = "${file("${path.module}/../interface.nomad")}"
}

