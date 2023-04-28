DIR?=.
SERVICE_NAME=query-server
NEXUSHOST=10.10.30.23:5000
VERSION=0206
REGISTRY_HOST=10.10.30.23
REGISTRY_PORT=5000

.PHONY: to-nexus
to-nexus:
	make build-image
	make push-to-registry

.PHONY: poland-image
poland-image:
	make build-image
	make compress-image
	make change-name

.PHONY: push-to-registry
push-to-registry:
	docker push ${REGISTRY_HOST}:${REGISTRY_PORT}/${SERVICE_NAME}:v${VERSION}

.PHONY: change-name
change-name:
	mv query-server.tar query-server-v${VERSION}.tar

.PHONY: build-image
build-image:
	docker build --platform linux/amd64 -t ${NEXUSHOST}/${SERVICE_NAME}:v${VERSION} .

.PHONY: compress-image
compress-image:
	docker save -o ${SERVICE_NAME}.tar ${NEXUSHOST}/${SERVICE_NAME}:v${VERSION}

setup:
	git config commit.template .gitmessage.txt
	poetry install
	poetry run pre-commit install
	chmod -R +x ./scripts

clean:
	rm -vrf ./build ./dist ./*.tgz ./*.egg-info .pytest_cache .mypy_cache
	find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete
	rm .coverage

format:
	bash ./scripts/format.sh ${DIR}

typecheck:
	bash ./scripts/typecheck.sh ${DIR}

lint:
	bash ./scripts/lint.sh ${DIR}

test:
	bash ./scripts/test.sh

pre-commit:
	poetry run pre-commit



.ONESHELL:
SHELL = /usr/bin/zsh
run:
	cd app
	uvicorn main:app --reload --host=0.0.0.0 --port=19000
