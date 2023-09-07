TESTNAME?=my_test
PDFPATH?=$(TESTNAME)/results_$(TESTNAME)
APPENDPDF?=true
GET_STATS_CONTAINER_NAME?=get_stats
GET_STATS_NETWORK?=unict-testingpipelines_default # it must be the same network of prometheus
INFO?=""
build-get_stats:
	@echo "Bulding get_stats image..."
	@docker build -t $(GET_STATS_CONTAINER_NAME):latest .

start-get_stats: build-get_stats
	@echo "Starting get_stats..."..
	@cd .. ; \
	docker run --rm \
		--name $(GET_STATS_CONTAINER_NAME) \
		-v $$(pwd)/test-results/:/test-results \
		-v $$(pwd)/get_stats/containers_list.txt:/containers_list.txt:ro \
		--env-file $$(pwd)/get_stats/env_file.txt \
		$(if $(GET_STATS_NETWORK), --network $(GET_STATS_NETWORK)) \
		$(GET_STATS_CONTAINER_NAME) \
		python3 get_stats.py /test-results/${TESTNAME} /test-results/${PDFPATH}.pdf ${APPENDPDF} "${INFO}"