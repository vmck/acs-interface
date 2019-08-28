job "interface" {
  datacenters = ["dc1"]
  type = "service"

  group "interface" {
    task "interface" {
      constraint {
        attribute = "${meta.volumes}"
        operator  = "is_set"
      }
      driver = "docker"
      config {
        image = "vmck/acs-interface:interface"
        dns_servers = ["${attr.unique.network.ip-address}"]
        volumes = [
          "${meta.volumes}/interface:/opt/interface/data",
        ]
        port_map {
          http = 8100
        }
      }
      template {
        data = <<-EOF
          DEBUG = true
          SECRET_KEY = "TODO:ChangeME!!!"
          HOSTNAME = "*"
          MINIO_ADDRESS = "10.42.1.1:9000"
          MINIO_ACCESS_KEY = "1234"
          MINIO_SECRET_KEY = "123456789"
          MINIO_BUCKET = "test"
          EOF
          destination = "local/interface.env"
          env = true
      }
      template {
        data = <<-EOF
          {{- range service "vmck" -}}
            VMCK_API_URL = "http://{{.Address}}:{{.Port}}/v0/"
          {{- end }}
          EOF
          destination = "local/vmck-api.env"
          env = true
      }
      resources {
        memory = 300
        cpu = 200
        network {
          port "http" {
            static = 10002
          }
        }
      }
      service {
        name = "interface"
        port = "http"
        check {
          name = "interface alive on http"
          initial_status = "critical"
          type = "http"
          path = "/alive"
          interval = "5s"
          timeout = "5s"
        }
      }
    }
  }
}
