# Unict-TestingPipelines

The **Unict-TestingPipelines** project creates a cluster of registry services.
The cluster is composed of many instances of registry nodes.

## Getting started

### Start

To get started with Unict-TestingPipelines, run the following command:

```bash
make start-cluster
```

this command automatically detects and start all registry services and Prometheus + cAdvisor monitoring.

If you want to start all the registry services, Prometheus + cAdvisor monitoring, JMeter and get_stats services run this command:

```bash
make start-all TESTNAME=_ TESTPLAN_NAME=_ PROPERTIES=_ PDFPATH=_ APPENDPDF=_ INFO=_
```

NOTE: if you use `make start-all`, you must change the line `COPY get_stats.py .` in `COPY get_stats/get_stats.py .` in  the file `get_stats/Dockerfile`, line 5. Otherwise, if you start the services separately using `make start-cluster`,`make start-jmeter`,`make start-get_stats`, you must not change the line.

Where:
- `TESTNAME`: is the name of the test that will be executed when run this command
- `TESTPLAN_NAME`: specify the testplan for JMeter (default value is: `repeatedOneRequest`)
- `PROPERTIES`: specify the properties for JMeter variables (default value is: `additional.properties`)
- `PDFPATH`: it's the name of the pdf where tests will saved (at test-results folder), can be a name 
    (that is the pdf name) or a path if needed to save it in a specific folder (don't need to specify the 
    file extension at the end of the string).
- `APPENDPDF`: in case the `PDFPATH` already exists, if `APPENDPDF`==true, the new pdf will be concatenated with the old one, otherwise it will be replaced.
- `INFO`: short text used to give more informations to pdf (for example the resources of the containers)

**NOTE**: `NODE` and `KEY` are used only by `repeatedOneRequest` testplan. If you are using (for example) `differentRequests` testplan, you don't need to specify `NODE` and `KEY` but you need to use `additional.properties` to specify more nodes and more keys.

If you want to start only one node (root-node), run the following command:

```bash
make start-single
```

### Stop

To stop the registry services, run the following command:

```bash
make stop-cluster
```

this command automatically detects and stop all registry services.

With the following command all the registry services and the Jmeter service will stopped:

```bash
make stop-all
```

If you want to stop only one node (root-node), run the following command:

```bash
make stop-single
```

## Configuration

The scope of this project is to create and run a performance testing pipeline.
To help the users to create a new `island` to attach to the `root-node` or creating a new `module` to attach to any `island` you can read the following instructions.

### Configuration with .env

To specify the image version and the log level of every node created, here an example:
```bash
IMG_VERSION=0.2.10
LOG_LEVEL=warn
```

### Create Root

```bash
make new.root NAME=_ DISABLE_CACHE=_
```

Where:
- `NAME`: name of the root service
- `DISABLE_CACHE`: option that disable the cache of all nodes (default value is `no`, means that the cache is enabled)

### Create Island

```bash
make new.island NAME=_ PARENT=_ DISABLE_CACHE=_
```

Where:

- `NAME`: is the name of the `island`
- `PARENT`: is the name of the node where the `island` is attached (in our case the root node).
- `DISABLE_CACHE`: option that disable the cache of all nodes (default value is `no`, means that the cache is enabled)

### Create Module

```bash
make new.module NAME=_ PARENT=_ DISABLE_CACHE=_
```

Where:

- `NAME`: is the name of the `module`
- `PARENT`: is the name of the node where the `module` is attached (usually is one of the `island`).
- `DISABLE_CACHE`: option that disable the cache of all nodes (default value is `no`, means that the cache is enabled)

### Create Tree

```bash
make new.tree ROOT=_ ISLANDS=_ MODULES=_ DISABLE_CACHE=_
```

Where:
- `ROOT`: name of the root node, for example `A`
- `ISLANDS`: list of islands names, example for two islands: "B1 B2 B3"
- `MODULES`: list of modules names (modules of one island are separated by ','), example: "C1-1,C1-2 C2-1 C3-1,C3-2,C3-3"
- `DISABLE_CACHE`: option that disable the cache of all nodes (default value is `no`, means that the cache is enabled)

### Create and Start all the Services

```bash
make build-and-test TESTNAME=_ ROOT=_ ISLANDS=_ MODULES=_ DISABLE_CACHE=_ TESTPLAN_NAME=_ PROPERTIES=_ PDFPATH=_ APPENDPDF=_ INFO=_
```

Where:
- `TESTNAME`: is the name of the test that will be executed when run this command
- `ROOT`: name of the root node
- `ISLANDS`: list of islands names, example for two islands: "B1 B2"
- `MODULES`: list of modules names (modules of one island are separated by ','), example: "C1-1,C1-2 C2-1"
- `DISABLE_CACHE`: option that disable the cache of all nodes (default value is 'no', means that the cache is enabled)
- `TESTPLAN_NAME`: specify the testplan for JMeter (default value is: `repeatedOneRequest`)
- `PROPERTIES`: specify the properties for JMeter variables (default value is: `additional.properties`)
- `PDFPATH`: it's the name of the pdf where tests will saved (at test-results folder), can be a name 
    (that is the pdf name) or a path if needed to save it in a specific folder (don't need to specify the 
    file extension at the end of the string).
- `APPENDPDF`: in case the `PDFPATH` already exists, if `APPENDPDF`==true, the new pdf will be concatenated with the old one, otherwise it will be replaced.
- `INFO`: short text used to give more informations to pdf (for example the resources of the containers)


**NOTE**: `NODE` and `KEY` are used only by `repeatedOneRequest` testplan. If you are using (for example) `differentRequests` testplan, you don't need to specify `NODE` and `KEY` but you need to use `additional.properties` to specify more nodes and more keys.

### Stop and Delete all the Services started

```bash
make stop-and-clean
```

With this command all the container will be stopped, all the files created for the tree will be deleted

#### Details 👈

The previous commands will create the following files:

- `meta/registry-config-<name>.json`
- `docker-compose-island-<name>.yml` (if you run the command `make new.island ...`)
- if you run the command `make new.module ...` it will update the `docker-compose-island-<PARENT>.yml` file, adding the new container section in the file.

**NOTE**: All services is automatically detects and the users not need to specify them in the `start` and `stop` command.

### Results

If you run the commands: `make build-and-test ...` or `make start-all ...`, all the results of that test will be saved in the `test-results` folder.
Every test has a name (`TESTNAME`) and all the informations are included in a folder with that name (in the test-results folder)

### PDF

If you choose to create the pdf file, the script will search the .csv file and call Prometheus to obtain the information about the specified test.
The PDF structure is made up of a first part describing the test carried out, at the top there are some informations about the test (inserted in the script start command with the key name `INFO`) and the informations in the file .properties of JMeter.
The second part is made up of four graphs:
- The first two are information taken from the csv file and represent the requests made by JMeter, the first describes them according to the timestamp of the requests while the second graph describes the requests in order of receipt by JMeter. Requests are represented with dots, blue if successful, red otherwise.
- The last two graphs represent data requested from Prometheus (about interested containers), the first graph highlights the memory usage by the containers, the second takes into account the percentage increase in the cpu usage by the containers (in the case of multicore, the graph represents the percentage of average increase between cores).
