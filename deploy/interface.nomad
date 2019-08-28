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
        image = "vmck/interface:interface"
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
          SECRET_KEY = "TODO:ChangeME!!!"
          {{- range service "vmck" -}}
            VMCK_API_URL = "http://{{.Address}}:{{.Port}}/v0/"
          {{- end }}
          MINIO_ADDRESS = "localhost:9000"
          MINIO_ACCESS_KEY = "1234"
          MINIO_SECRET_KEY = "123456789"
          MINIO_BUCKET = "test"
          EOF
          destination = "local/interface.env"
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
          path = ""
          interval = "5s"
          timeout = "5s"
        }
      }
    }
  }
}
