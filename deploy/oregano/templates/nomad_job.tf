resource "nomad_job" "%{name}" {
  jobspec = "${file("${path.module}/%{template_path}")}"
}
