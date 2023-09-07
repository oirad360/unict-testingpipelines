TESTNAME?=my_test
TESTPLAN_NAME?=repeatedOneRequest
PDFPATH?=$(TESTNAME)/results_$(TESTNAME)
APPENDPDF?=true
PROPERTIES?=additional.properties
INFO?=""

start-cluster:
	@echo "Starting the Registry service cluster..."
	@docker-compose -f docker-compose-root.yml -f prometheus/docker-compose-prometheus.yml $(foreach file,$(wildcard docker-compose-island-*.yml),-f $(file)) up

stop-cluster:
	@echo "Stopping the Registry service cluster..."
	@docker-compose -f docker-compose-root.yml -f prometheus/docker-compose-prometheus.yml $(foreach file,$(wildcard docker-compose-island-*.yml),-f $(file)) down

JMETER_CONTAINER_NAME?=jmeter
JMETER_NETWORK?=unict-testingpipelines_default # it must be the same network of the containers under test
build-jmeter:
	@echo "Bulding Jmeter image..."
	@docker build -t $(JMETER_CONTAINER_NAME):latest jmeter

start-jmeter: build-jmeter
	@echo "Starting Jmeter..."
	@docker run --rm\
		--name $(JMETER_CONTAINER_NAME) \
		-v $$(pwd)/testplans:/testplans \
		-v $$(pwd)/test-results:/test-results \
		-v $$(pwd)/test-results/${TESTNAME}:/test-results/${TESTNAME} \
		$(if $(JMETER_NETWORK), --network $(JMETER_NETWORK)) \
		$(JMETER_CONTAINER_NAME) \
		sh -c "cp ../../testplans/${PROPERTIES} ../../test-results/${TESTNAME}/properties_${TESTNAME}.txt && jmeter -n -t /testplans/${TESTPLAN_NAME}.jmx -q /testplans/${PROPERTIES} -l /test-results/${TESTNAME}/results_${TESTNAME}.csv -e -f -o  /test-results/${TESTNAME}/dashboard/"


GET_STATS_CONTAINER_NAME?=get_stats
GET_STATS_NETWORK?=unict-testingpipelines_default # it must be the same network of prometheus
build-get_stats:
	@echo "Bulding get_stats image..."
	@docker build -t $(GET_STATS_CONTAINER_NAME):latest get_stats

start-get_stats: build-get_stats
	@echo "Starting get_stats..."..
	@docker run --rm \
		--name $(GET_STATS_CONTAINER_NAME) \
		-v $$(pwd)/test-results/:/test-results \
		-v $$(pwd)/get_stats/containers_list.txt:/containers_list.txt:ro \
		--env-file $$(pwd)/get_stats/env_file.txt \
		$(if $(GET_STATS_NETWORK), --network $(GET_STATS_NETWORK)) \
		$(GET_STATS_CONTAINER_NAME) \
		python3 get_stats.py /test-results/${TESTNAME} /test-results/${PDFPATH}.pdf ${APPENDPDF} "${INFO}"

start-all:
	@echo "Starting the Registry service and jMeter..."
	@testplanName=$(TESTPLAN_NAME) properties=$(PROPERTIES) testName=$(TESTNAME) pdfPath=$(PDFPATH) appendPdf=${APPENDPDF} info="${INFO}" docker-compose -f docker-compose-root.yml -f prometheus/docker-compose-prometheus.yml -f jmeter/docker-compose-jmeter.yml -f get_stats/docker-compose-get_stats.yml $(foreach file,$(wildcard docker-compose-island-*.yml),-f $(file)) up

stop-all:
	@echo "Stopping the Project and Tester..."
	@docker-compose -f docker-compose-root.yml -f prometheus/docker-compose-prometheus.yml -f jmeter/docker-compose-jmeter.yml -f get_stats/docker-compose-get_stats.yml $(foreach file,$(wildcard docker-compose-island-*.yml),-f $(file)) down

start-single:
	@echo "Starting the single Registry service node..."
	@docker-compose -f docker-compose-root.yml up

stop-single:
	@echo "Starting the single Registry service node..."
	@docker-compose -f docker-compose-root.yml down

stop-and-clean:
	@make stop-all;
	rm docker-compose-root.yml $(foreach file,$(wildcard docker-compose-island-*.yml), $(file));
	rm -r meta/*;

new.root:
	@echo "Creating a new root configuration..."
	@echo "Creating a config file..."
	@mkdir -p meta
	@cp template/registry-config-root.template.json meta/registry-config-$(NAME).json
	@sed -i 's/<name>/$(NAME)/g' meta/registry-config-$(NAME).json
	@echo "Creating a docker-compose file..."
	@cp template/root.template.yml docker-compose-root.yml
	@sed -i 's/<name>/$(NAME)/g' docker-compose-root.yml
	@sed -i 's/<disable_cache>/"$(DISABLE_CACHE)"/g' docker-compose-root.yml

# Generation of a new registry configuration (island and module)
new.island:
	@echo "Creating a new island configuration..."
	@echo "Creating a config file..."
	@cp template/registry-config.template.json meta/registry-config-$(NAME).json
	@sed -i 's/<name>/$(NAME)/g' meta/registry-config-$(NAME).json
	@sed -i 's/<parent>/$(PARENT)/g' meta/registry-config-$(NAME).json
	@echo "Creating a docker-compose file..."
	@cp template/island.template.yml docker-compose-island-$(NAME).yml
	@sed -i 's/<name>/$(NAME)/g' docker-compose-island-$(NAME).yml
	@sed -i 's/<parent>/$(PARENT)/g' docker-compose-island-$(NAME).yml
	@sed -i 's/<disable_cache>/"$(DISABLE_CACHE)"/g' docker-compose-island-$(NAME).yml

new.module:
	@echo "Creating a new module configuration..."
	@echo "Creating a config file..."
	@cp template/registry-config.template.json meta/registry-config-$(NAME).json
	@sed -i 's/<name>/$(NAME)/g' meta/registry-config-$(NAME).json
	@sed -i 's/<parent>/$(PARENT)/g' meta/registry-config-$(NAME).json
	@echo >> docker-compose-island-$(PARENT).yml
	@echo "Updating a docker-compose file..."
	@cp template/module.template.yml template/module.template_temp.yml
	@sed -i '/^$$/d' template/module.template_temp.yml
	@sed -i 's/^/  /' template/module.template_temp.yml
	@sed -i '/^$$/d' template/module.template_temp.yml
	@sed -i '$$ r template/module.template_temp.yml' docker-compose-island-$(PARENT).yml
	@sed -i 's/<name>/$(NAME)/g' docker-compose-island-$(PARENT).yml
	@sed -i 's/<parent>/$(PARENT)/g' docker-compose-island-$(PARENT).yml
	@sed -i 's/<disable_cache>/"$(DISABLE_CACHE)"/g' docker-compose-island-$(PARENT).yml
	@rm template/module.template_temp.yml

new.tree:
	@make new.root NAME=$(ROOT) DISABLE_CACHE="$(DISABLE_CACHE)";
	@for island in $(ISLANDS); do \
		make new.island NAME=$$island PARENT=$(ROOT) DISABLE_CACHE="$(DISABLE_CACHE)"; \
		i=$$(expr $$i + 1); \
		module_list=$$(echo $(MODULES) | cut -d' ' -f$$i); \
		echo "Module List: $$module_list"; \
		for module in $$(echo $$module_list | tr ',' ' '); do \
			if [ "$$module" = "_" ]; then \
				continue; \
			fi; \
			echo "Processing Module: $$module"; \
			make new.module NAME=$$module PARENT=$$island DISABLE_CACHE="$(DISABLE_CACHE)"; \
		done \
	done

DISABLE_CACHE ?= no

build-and-test:
	@make new.tree ROOT=$(ROOT) ISLANDS="$(ISLANDS)" MODULES="$(MODULES)" DISABLE_CACHE="$(DISABLE_CACHE)"
	@make start-all TESTPLAN_NAME=$(TESTPLAN_NAME) PROPERTIES=$(PROPERTIES) TESTNAME=$(TESTNAME) PDFPATH=$(PDFPATH) APPENDPDF=${APPENDPDF} INFO=${INFO}