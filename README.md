## Azkaban dockerized recipe
The goal is to have an infra that runs Azkaban and orchestrates a basic ML flow. To demonstrate this, there must be 3 main components:
- The orchestrator that runs in an isolated environment (preferrably).
- The codebase itself which will be run through the orchestrator.
- The DAG that goes as input to the orchestrator.

## Folder structure
- `code`: Basic ML productionized code (our codebase).
- `services`: The compose file for the services that will be used (our orchestrator).
- `orchestration`: Azkaban flows and jobs (our DAG definitions).

## Usage
Have a look at the `services/docker-compose.yml` file. There are 6 services defined:
- `db`: The MySQL backend, to be used by Azkaban.
- `web`: The Azkabn web server (depends on `db` service to be healthy).
- `minio`: Replacement for S3, to be used by our ML codebase.
- `mc`: Simply creates a bucket in Minio, that will house our data.
- `jupyter`: JupyterLab service, to be used by Data Scientists for analysis.
- `pypi`: Productionized code will be packaged and uploaded to this server.

### Setting up the orchestrator
There are 2 ways to setup Akaban:
- Azkaban Solo Server: One machine hosts both web and executor services.
- One machine acts as a web server while other machines run executor services.
	- We will be using this setup in our demonstration.
	- This setup also requires a Database (MySQL preferred) to serve as backend.

#### Steps to follow:
- Log into the machines you wish to use for orchestration.
- Make sure you have packages like `git`, `python 3.8`, `docker`, `make` installed.
- Make sure these machines can talk to each other.
	- If on CentOS, use `firewall-cmd` to allow communication.
		- `firewall-cmd --zone=public --add-source=<machineip> --permanent`.
	- If on Ubuntu/Debian, use `ufw`. Google this step for your OS.
- Add entries in `/etc/hosts` file or your `nameserver` in the executor machines:
	- Assume your webserver machine has IP: `<machineip>`
	- `<machineip> azkaban-web-server azkaban-mysql-server`.
	- This is because our web-server and mysql backend will both run on the same machine whose IP is: `<machineip>`.

**Setting up the Web Server**
- Log into the machine you wish to run the web+db (and non-executor) services on.
	- Let's call this *MACHINE A*.
- Clone this repo: `https://github.com/ag/azkaban-cluster-dockerized.git`
- Modify the `.env` file if needed (different password, bucket name etc).
- Run `services="" make start` to start all services.
	- Alternatively, say you only need minio: `services="minio" make start`
- You would see that the `db` would be `unhealthy` and `web` service is in `created` state (but not yet `running`). This is because it waits for executor services to start up and when they create an entry in the database, only then `db` will become `healthy` and `web` service will become `running`.
- Meanwhile, check with `docker ps` to see if other services are running.

**Setting up the Executors**
- Log into a machine you wish to run the executor service on.
	- Let's call this *MACHINE B*.
- Clone this repo: `https://github.com/ag/azkaban-cluster-dockerized.git`.
- Build the image and run the executor.
	```bash
	cd services/executor
	docker build -t executor:latest .
	docker run --rm -d --name=executor --net=host executor:latest
	```
- Check the logs using `docker logs executor` and see if you can find the line `{"status":"success"}`. Make sure there aren't any errors.
	- If you see errors related to not being able to find the `db`, make sure to check your `/etc/hosts` and verify that you put IPs for `azkaban-<web/mysql>-server`.
- As soon as the executor service runs successfully, the `web` service on *MACHINE A* should be running. Check the logs that container as well and verify no errors.
- Repeat these steps on other machines you want to run executor services on.

**Accessing Azkaban UI**
- SSH Tunnel the port `8081` of *MACHINE A* and open `localhost:8081` on your browser. This should open the Azkaban page.
	- User: `azkaban`, Password: `azkaban`.

### Experimenting with Data
- You can place the raw data on Minio bucket via Minio web service (running on `localhost:9001`) or through a helper script in `scripts/create_dataset_in_s3.py`, using `make upload_data` target.
- Data Scientists can now run their experiments by SSH Tunneling *MACHINE A* and accessing JupyterLab. You will need to provide the notebook token to them (which you can find in the logs of the jupyter container). There can be better ways to do this, since this is just a demonstration.
- Data on Minio, can be accessed in notebooks using `boto3` python library.
- Notebooks are persisted on *MACHINE A*, since we have mounted volumes.

### Productionizing Code
- Once experimentation is done, the notebook code needs to moved to python modules and organized. There's already an *example codebase* under `code/` which uses `pyproject.toml` to define packaging instructions.
- Packaging and uploading productionized code to pypi server using `make upload_code` target, which uses `twine` to upload the `wheel` file to pypi server.
- You can check the packages residing in our pypi server using `curl -v localhost:8080/packages/`, from inside of *MACHINE A* (or SSH tunnel port `8080`).
- Ideally, your productionized code would reside in a repo, and a CI/CD (say Github actions) should build and deploy your package to pypi, upon merge to `master`.
	- For this to work, you may need to store your *MACHINE A* access keys in GitHub (or GitLab) so that the CI/CD can access your hosted pypi server.

### Running Jobs on Azkaban
- Open the Azkaban webpage from your browser, create a new project.
- Zip the `flows` directory using `zip -1 -r flows.zip orchestration/flows`.
- Upload this `flows.zip` on your local, to your created project, from the UI.
- There are ways to do this part programmatically using Azkaban CLI or the Ajax API.
- You can now trigger the jobs manually or schedule them.

## Roadmap:
- [x] Groundwork (Azkaban multi-node cluster)
- [x] Dockerfiles
- [x] Environment setup
- [x] Minio S3 setup
- [x] Finalizing an ML example for demo
- [x] Productionized ML code
- [x] Packaged ML code
- [x] End-to-End test with 1 executor
- [x] End-to-End test with multiple executors
- [x] Cleanup
- [x] Update README
