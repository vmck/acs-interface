# interface
UI for Vmchecker
[![Build Status](https://jenkins.liquiddemo.org/api/badges/vmck/interface/status.svg)](https://jenkins.liquiddemo.org/vmck/interface)

## Installation

You need `pipenv` and `docker` installed
```shell
sudo apt update && sudo apt install docker
pip3 install --user pipenv
```

To install dependencies:
```shell
pipenv install
```

You need a running vmck instance. You may use [vmck/vmck](https://github.com/vmck/vmck)
as a starting ground. Please refer to it on how to set it up.

## Run

### Locally

You need to set up some enviromental vars. For that you can
create the file `.env` at the root of this project  where you
add your variabiles. The following example is enough to start you:

```
#DEBUG=True
MINIO_ACCESS_KEY=1234
MINIO_SECRET_KEY=123456789
VMCK_API_URL=http://www.example.com
```
Please add it to your `.env` file
Now run:

```shell
pipenv run ./examples/minio.sh
./runinterface
```

Now the vmck/interface is available at `localhost:8100` and the minio
blob storage server at `localhost:9000`.

To stop `CTRL-C` in the terminal where you started to stop `vmck/interface`
and `docker stop storage` to stop the minio server.
