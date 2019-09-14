# ACS-INTERFACE DOCUMENTATION

## Steps to set up a new homework:

1. Set up a repo on github or gitlab. There, on any branch you want, must exist:
    * `checker.sh` -- the checker for the homework, must have execution permission and must
    output the score as the last line with the format `{score}/{max_score}`
    * `config.ini` -- the specificatios for the vm that will be used to check the student's
    submission.

E.g. config file:
```
[VMCK]
image_path = imgbuild-acs-pc.qcow2.tar.gz # image that the vm will use
memory = 512 # the memory in MB
cpus = 1 # number of cores, 1 core has 3000 MHZ by default. Check vmck settings
```

E.g. checker output:
```
Some irrelevant text that
the stundent cares about, but not vmck.
Some 'congrats' or 'bad day' message
100/100
```

2. Go to your acs-interface admin link (e.g. localhost:8100/admin). Log in with your
normal vmck account and under the `interface` title go to the `assignments` link.
There click on `add assignment` on the upper-right side.

E.g.
```
Course: Programarea calculatoarelor  # select from drop down
Code: 00  # consider it as an id or counter (00 first homework, 01 second etc.)
          # choose your convention (alphanumerical characters allowed)
Name: Tetribit  # the name will show up on the homepage
                # it's the name the students will when they choose their assignment
Max score: 100
Deadline:
        Date: xx/yy/zzzz
        Time: aa:bb
Repo url: https://github.com/vmck/assignment/
Repo branch: pc-00  # the branch where you have the files mentioned at 1
```
