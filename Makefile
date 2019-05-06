BUCKETPATH = ga-odc-eros-archive-west/alex

L5_EXAMPLE = espa-tonybutzer@gmail.com-11272018-195452-308/LT052100501990120801T1-SC20181128022137.tar.gz
L7_EXAMPLE = espa-tonybutzer@gmail.com-11272018-195447-427/LE072100502008091201T1-SC20181128003726.tar.gz
L8_EXAMPLE = espa-tonybutzer@gmail.com-11272018-195148-621/LC082100502013120701T1-SC20181127234642.tar.gz

L5_FILE = s3://$(BUCKETPATH)/$(L5_EXAMPLE)
L7_FILE = s3://$(BUCKETPATH)/$(L7_EXAMPLE)
L8_FILE = s3://$(BUCKETPATH)/$(L8_EXAMPLE)

get-l5-example:
	aws s3 cp $(L5_FILE) data/raw

unzip-l5-example:
	cd data/raw && tar -xzvf $(word 2, $(subst /, ,$(L5_EXAMPLE)))

select-l5-files: clear-dirs
	cp data/raw/LT05*sr*.tif data/many/
	cp data/raw/LT05*.xml data/many/

get-l7-example:
	aws s3 cp $(L7_FILE) data/raw

unzip-l7-example:
	cd data/raw && tar -xzvf $(word 2, $(subst /, ,$(L7_EXAMPLE)))

select-l7-files: clear-dirs
	cp data/raw/LE07*sr*.tif data/many/
	cp data/raw/LE07*.xml data/many/

get-l8-example:
	aws s3 cp $(L8_FILE) data/raw

unzip-l8-example:
	cd data/raw && tar -xzvf $(word 2, $(subst /, ,$(L8_EXAMPLE)))

test-example:
	docker-compose run pygdal \
		./process_landsat.py

push:
	docker build --tag crcsi/landsat-processor .
	docker push crcsi/landsat-processor

add-items:
	AWS_DEFAULT_PROFILE=fsi-admin \
	AWS_DEFAULT_REGION=us-west-2 \
	IN_BUCKET=frontiersi-odc-data \
	IN_PATH=raw/fiji \
	QUEUE=odc-sandbox-data-processing-queue \
	LIMIT=10 \
	./add_to_queue.py
