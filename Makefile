SHELL=/bin/bash

dir_services=services
dir_code=code
dir_orchestration=orchestration
compose_up=docker compose -f ${dir_services}/docker-compose.yml --env-file .env up -d --build
compose_down=docker compose --project-directory ${dir_services} --env-file .env rm -fsv
services?=jupyter
pypi_host?=localhost

start:
	${compose_up} ${services}
stop:
	${compose_down} ${services}
stop_azk:
	${compose_down} db web
start_azk:
	${compose_up} db web
clean_build:
	cd ${dir_code}; \
	rm -rf *.egg-info dist/ build/
upload_data:
	set -o allexport; \
	source .env; \
	set +o allexport; \
	python3 -m venv env; \
	source env/bin/activate; \
	pip install --upgrade pip; \
	pip install -qr requirements.txt; \
	python3 scripts/create_dataset_in_s3.py; \
	deactivate; \
	rm -rf env
upload_code: clean_build
	set -o allexport; \
	source .env; \
	set +o allexport; \
	python3 -m venv env; \
	source env/bin/activate; \
	pip install --upgrade pip; \
	pip install -qr requirements.txt; \
	cd ${dir_code}; \
	python3 -m build --wheel; \
	twine check dist/*.whl; \
	twine upload --repository-url http://${pypi_host}:8080 dist/*.whl; \
	deactivate; \
	rm -rf env
run_preproc:
	set -o allexport; \
	source .env; \
	set +o allexport; \
	spam_preproc -c ../mlcode/configs/train_s3.yaml -t
run_train:
	set -o allexport; \
	source .env; \
	set +o allexport; \
	spam_train -p b12bc11f-2056-4e3f-a173-aab6db0177e3  -c ../mlcode/configs/train_s3.yaml
run_inference:
	set -o allexport; \
	source .env; \
	set +o allexport; \
	spam_infer -c ../mlcode/configs/train_s3.yaml -s "URGENT! Take this 100000 cash prize RIGHT NOW!!!"
