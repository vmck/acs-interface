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
          {{- with secret "kv/minio" -}}
            MINIO_ACCESS_KEY = "{{ .Data.access_key }}"
            MINIO_SECRET_KEY = "{{ .Data.secret_key }}"
          {{- end -}}
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

  group "database" {
    task "postgres" {
      constraint {
        attribute = "${meta.volumes}"
        operator  = "is_set"
      }

      driver = "docker"
      config {
        image = "postgres:12.0-alpine"
        dns_servers = ["${attr.unique.network.ip-address}"]
        volumes = [
          ${meta.volumes}/database/postgres/data:/var/lib/postgresql/data",
        ]
        port_map {
          pg = 5432
        }
      }
      template {
        data = <<-EOF
          POSTGRES_DB = "interface"
          {{- with secret "kv/postgres" }}
            POSTGRES_USER = {{ .Data.username }}
            POSTGRES_PASSWORD = {{ .Data.password }}
          {{- end }}
          EOF
        destination = "local/postgres.env"
        env = true
      }
      resources {
        memory = 350
        network {
          mbits = 1
          port "pg" {}
        }
      }
      service {
        name = "database-postgres-interface"
        port = "pg"
        check {
          name = "tcp"
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
        image = "vmck/acs-interface"
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
          ACS_INTERFACE_ADDRESS = "http://{{ env "NOMAD_ADDR_http" }}"
          ACS_USER_WHITELIST = '{{ key "acs_interface/whitelist" }}'
          EOF
        destination = "local/interface.env"
        env = true
      }
      template {
        data = <<-EOF
          {{- range service "vmck" -}}
            VMCK_API_URL = "http://{{ .Address }}:{{ .Port }}/v0/"
          {{- end }}
          EOF
        env = true
        destination = "local/vmck-api.env"
      }
      template {
        data = <<-EOF
          {{- range service "storage" -}}
            MINIO_ADDRESS = "{{ .Address }}:{{ .Port }}"
          {{- end }}
          EOF
        destination = "local/minio-api.env"
        env = true
      }
      template {
        data = <<-EOF
          {{- with secret "kv/minio" -}}
            MINIO_ACCESS_KEY = "{{ .Data.access_key }}"
            MINIO_SECRET_KEY = "{{ .Data.secret_key }}"
            MINIO_BUCKET = "test"
          {{- end -}}
          EOF
        destination = "local/minio.env"
        env = true
      }
      template {
        data = <<-EOF
          {{- with secret "kv/postgres" }}
            POSTGRES_USER = {{ .Data.username }}
            POSTGRES_PASSWORD = {{ .Data.password }}
          {{- end }}
          EOF
        destination = "local/postgres.env"
        env = true
      }
      template {
        data = <<-EOF
          {{- range service "database-postgres-interface" -}}
            POSTGRES_ADDRESS = "{{ .Address }}"
            POSTGRES_PORT = "{{ .Port }}"
          {{- end }}
          EOF
        destination = "local/postgres-api.env"
        env = true
      }
      template {
        data = <<-EOF
          {{- with secret "kv/ldap" -}}
            LDAP_SERVER_URL = "{{ .Data.server_address }}"
            LDAP_SERVER_URI = "ldaps://{{ .Data.server_address }}:{{ .Data.server_port }}"
            LDAP_BIND_DN = "{{ .Data.bind_dn }}"
            LDAP_BIND_PASSWORD = "{{ .Data.bind_password }}"
            LDAP_USER_TREE = "{{ .Data.user_tree }}"
            LDAP_USER_FILTER = "{{ .Data.user_filter }}"
          {{- end -}}
          EOF
          destination = "local/ldap.env"
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
        tags = [
          "traefik.enable=true",
          "traefik.frontend.rule=Host:vmchecker.liquiddemo.org",
        ]
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
