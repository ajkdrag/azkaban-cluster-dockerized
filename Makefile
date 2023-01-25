SHELL=/bin/bash

dir_services=services
dir_code=code
dir_orchestration=orchestration
compose_up=docker compose -f ${dir_services}/docker-compose.yml --env-file .env up -d --build
compose_down=docker compose --project-directory ${dir_services} --env-file .env rm -fsv
services?=jupyter

start:
	${compose_up} ${services}
stop:
	${compose_down} ${services}
stop_azk:
	${compose_down} db web
start_azk:
	${compose_up} db web
upload_data:
	set -o allexport; \
	source .env; \
	set +o allexport; \
	python3 -m venv env; \
	source env/bin/activate; \
	python3 -m pip install -qr requirements.txt; \
	python3 scripts/create_dataset_in_s3.py; \
	deactivate; \
	rm -rf env
upload_code:
	echo "To package code and upload to pypi"
