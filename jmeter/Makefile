JMETER_CONTAINER_NAME?=jmeter
TESTNAME?=default
TESTPLAN_NAME?=repeatedOneRequest
PROPERTIES?=additional.properties
JMETER_NETWORK?=unict-testingpipelines_default # it must be the same network of the containers under test
build-image:
	@echo "Bulding Jmeter image..."
	@docker build -t $(JMETER_CONTAINER_NAME):latest .

start-jmeter: build-image
	@echo "Starting Jmeter..."
	@cd .. ; \
	docker run --rm\
		--name $(JMETER_CONTAINER_NAME) \
		-v $$(pwd)/testplans:/testplans \
		-v $$(pwd)/test-results:/test-results \
		-v $$(pwd)/test-results/${TESTNAME}:/test-results/${TESTNAME} \
		$(if $(JMETER_NETWORK), --network $(JMETER_NETWORK)) \
		$(JMETER_CONTAINER_NAME) \
		sh -c "cp ../../testplans/${PROPERTIES} ../../test-results/${TESTNAME}/properties_${TESTNAME}.txt && jmeter -n -t /testplans/${TESTPLAN_NAME}.jmx -q /testplans/${PROPERTIES} -l /test-results/${TESTNAME}/results_${TESTNAME}.csv -e -f -o  /test-results/${TESTNAME}/dashboard/"


