# ACS-INTERFACE DOCUMENTATION

## Steps to set up a new homework:

1. Create a new section with your homework id (e.g. `pc-00`) in `setup.ini`
from `vmck/assignment`'s repo on the `master` branch. The section will contain a
single config variabile `name` that will be displayed on the dropdown bar from
where stundents will choose what homework they will upload.

E.g. section:
```
[pc-00]
; Name shown in dropdown bar
name = Programarea Calculatoarelor - Tema 0
```

2. Now that `acs-interface` is aware of your homework assignment you must create a
branch on that same repo, named like the section you created on the `master` branch
(e.g. you created a section named `pc-00` you will create a branch named `pc-00`).
In that repo you will have two files: `checker.sh` -- the checker for the homework,
must have execution permission and must output the score as the last line with the format
`{score}/{max_score}`-- and `config.ini` -- the specificatios for the vm
that will be used to check the student's submission.

E.g. config file:
```
[VMCK]
image_path = imgbuild-acs-pc.qcow2.tar.gz # image that the vm will use
memory = 512 # the memory in MB
cpus = 1 # number of cores, 1 core has 1000 MHZ
```

E.g. checker output:
```
Some irrelevant text that
the stundent cares about, but not the
vmck.
100/100
```
