#!/bin/bash -ex
exit 0
cd "$( dirname "${BASH_SOURCE[0]}" )"

trap "vagrant destroy -f"  EXIT

vagrant up

vagrant ssh -- < ./test-pytest.sh
