SHELL=/bin/bash
environment=dev
compose_up=docker compose --env-file ${environment}.env up -d --build
compose_down=docker compose --env-file ${environment}.env rm -fsv

stop_web:
	${compose_down} web
stop_db:
	${compose_down} db
stop_backend:
	${compose_down} db minio
stop_jupyter:
	${compose_down} jupyter
start_db:
	${compose_up} db 
start_backend:
	${compose_up} db minio mc
start_web:
	${compose_up} web 
start_jupyter:
	${compose_up} jupyter
start_all:
	${compose_up} 
upload_data:
	set -o allexport; \
	source ${environment}.env; \
	set +o allexport; \
	source env/bin/activate; \
	pip install -r requirements.txt; \
	python scripts/create_dataset_in_s3.py; \
	deactivate
