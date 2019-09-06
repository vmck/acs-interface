# ACS-INTERFACE DOCUMENTATION
### True for up to commit: f5d8b0c84838e34dd156974d9407831d363b8900

##Steps to set up a new homework:

1. Create a `.ini` file with the name `{classname}_{homework_number}.ini`
(E.g. `pc_0.ini` for the first homework) in the directory `{root}/assignment/`.
The file will have the following format:
```
[VMCK]
image_path = imgbuild-acs-pc.qcow2.tar.gz # image that the vm will use
memory = 512 # the memory in MB
cpus = 1 # number of cores, 1 core has 1000 MHZ
```

2. Add the checker script with the same format name `{classname}_{homework_number}.sh`
in the same direcotry as above. Must have execution permission and must output the score
as the last line with the format `{score}/{max_score}`. You can assume that the script will
run at the root of the student's submission.

3. NOT IMPLEMENTED YET.
When clicking send in the `upload.html` page, a request variabile must be set to the correct
assignment id of the format `{classname}_{homework_number}`.
