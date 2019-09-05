job "acs-interface" {
  datacenters = ["dc1"]
  type = "service"

  group "storage" {
    task "minio" {
      constraint {
        attribute = "${meta.volumes}"
        operator  = "is_set"
      }
      driver = "docker"
      config {
        image = "minio/minio:RELEASE.2019-08-29T00-25-01Z"
        dns_servers = ["${attr.unique.network.ip-address}"]
        command = "server"
        args = ["/data"]
        volumes = [
          "${meta.volumes}/minio-storage:/data",
        ]
        port_map {
          http = 9000
        }
      }
      template {
        data = <<-EOF
          MINIO_ACCESS_KEY = "1234"
          MINIO_SECRET_KEY = "123456789"
          MINIO_BROWSER = "on"
          EOF
          destination = "local/config.env"
          env = true
      }
      resources {
        memory = 200
        cpu = 100
        network {
          port "http" {
            static = 9000
          }
        }
      }
      service {
        name = "storage"
        port = "http"
        check {
          name = "storage alive on http"
          initial_status = "critical"
          type = "tcp"
          interval = "5s"
          timeout = "5s"
        }
      }
    }
  }

  group "acs-interface" {
    task "acs-interface" {
      constraint {
        attribute = "${meta.volumes}"
        operator  = "is_set"
      }
      driver = "docker"
      config {
        image = "vmck/acs-interface:interface"
        dns_servers = ["${attr.unique.network.ip-address}"]
        volumes = [
          "${meta.volumes}/acs-interface:/opt/interface/data",
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
          {{- range service "storage-minio" -}}
            MINIO_ADDRESS = "{{.Address}}:{{.Port}}"
          {{- end }}
          EOF
          destination = "local/vmck-api.env"
          env = true
      }
      template {
        data = <<-EOF
          {{- range service "storage" -}}
            MINIO_ADDRESS = "{{.Address}}:{{.Port}}"
          {{- end }}
          EOF
          destination = "local/minio-api.env"
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
        name = "acs-interface"
        port = "http"
        check {
          name = "acs-interface alive on http"
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
