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

select-l8-files: clear-dirs
	cp data/raw/LC08*sr*.tif data/many/
	cp data/raw/LC08*.xml data/many/

clear-dirs:
	-rm data/many/*
	-rm -r data/out/*

build:
	docker-compose build

process-one:
	docker-compose run pygdal \
		./geotiffcog.py --path /opt/data/one --output /opt/data/out

process-many:
	docker-compose run pygdal \
		./geotiffcog.py --path /opt/data/many --output /opt/data/out

test-example:
	docker-compose run pygdal \
		./process_landsat.py


sync:
	aws s3 sync \
		--exclude "*.aux.xml" \
		data/out/many s3://frontiersi-odc-test/firstcog

sync-down:
	aws s3 sync \
		--exclude "*.aux.xml" \
		s3://frontiersi-odc-test/firstcog data/out/many

delete-rubbish:
	aws s3 rm s3://frontiersi-odc-test/firstcog/ \
		--recursive \
		--exclude "*.*" \
		--include "*.aux.xml"

push:
	docker build --tag alexgleith/landsat-processor .
	docker push alexgleith/landsat-processor
