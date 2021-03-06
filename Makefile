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
	docker build --tag geoscienceaustralia/landsat-to-cog_pygdal .
	docker push geoscienceaustralia/landsat-to-cog_pygdal

add-items-test:
	AWS_DEFAULT_REGION=us-west-2 \
        IN_BUCKET=deafrica-staging-west \
        IN_PATH=L5-Ghana_original \
        QUEUE=dsg-test-queue \
        LIMIT=5 \
        ./add_to_queue.py


add-items-L5-Ghana_original:
	AWS_DEFAULT_REGION=us-west-2 \
	IN_BUCKET=deafrica-staging-west \
	IN_PATH=L5-Ghana_original \
	QUEUE=dsg-test-queue \
	LIMIT=705 \
	./add_to_queue.py

add-items-L5-Kenya_original:
	AWS_DEFAULT_REGION=us-west-2 \
        IN_BUCKET=deafrica-staging-west \
        IN_PATH=L5-Kenya_original \
        QUEUE=dsg-test-queue \
        LIMIT=2670 \
        ./add_to_queue.py

add-items-L5-Senegal_original:
	AWS_DEFAULT_REGION=us-west-2 \
        IN_BUCKET=deafrica-staging-west \
        IN_PATH=L5-Senegal_original \
        QUEUE=dsg-test-queue \
        LIMIT=1500 \
        ./add_to_queue.py

add-items-L5-SierraLeone_original:
	AWS_DEFAULT_REGION=us-west-2 \
        IN_BUCKET=deafrica-staging-west \
        IN_PATH=L5-SierraLeone_original \
        QUEUE=dsg-test-queue \
        LIMIT=340 \
        ./add_to_queue.py

add-items-L5-Tanzania_original:
	AWS_DEFAULT_REGION=us-west-2 \
        IN_BUCKET=deafrica-staging-west \
        IN_PATH=L5-Tanzania_original \
        QUEUE=dsg-test-queue \
        LIMIT=5650 \
        ./add_to_queue.py

add-items-rwanda_burundi_new:
	AWS_DEFAULT_REGION=us-west-2 \
        IN_BUCKET=deafrica-staging-west \
        IN_PATH=rwanda_burundi_new \
        QUEUE=dsg-test-queue \
        LIMIT=5650 \
        ./add_to_queue.py

add-items-L7-Tanzania_original2:
	AWS_DEFAULT_REGION=us-west-2 \
        IN_BUCKET=deafrica-staging-west \
        IN_PATH=L7-Tanzania_original2 \
        QUEUE=dsg-test-queue \
        LIMIT=99999 \
        ./add_to_queue.py

add-items-ARDC-L7Ghana_Original_Data:
	AWS_DEFAULT_REGION=us-west-2 \
        IN_BUCKET=deafrica-staging-west \
        IN_PATH=ARDC-L7Ghana_Original_Data \
        QUEUE=dsg-test-queue \
        LIMIT=99999 \
        ./add_to_queue.py

add-items-ARDC-L7Kenya_Original_Data:
	AWS_DEFAULT_REGION=us-west-2 \
        IN_BUCKET=deafrica-staging-west \
        IN_PATH=ARDC-L7Kenya_Original_Data \
        QUEUE=dsg-test-queue \
        LIMIT=99999 \
        ./add_to_queue.py

add-items-ARDC-L7Senegal_Original_Data:
	AWS_DEFAULT_REGION=us-west-2 \
        IN_BUCKET=deafrica-staging-west \
        IN_PATH=ARDC-L7Senegal_Original_Data \
        QUEUE=dsg-test-queue \
        LIMIT=99999 \
        ./add_to_queue.py

add-items-ARDC-L7SierraLeone_Original_Data:
	AWS_DEFAULT_REGION=us-west-2 \
        IN_BUCKET=deafrica-staging-west \
        IN_PATH=ARDC-L7SierraLeone_Original_Data \
        QUEUE=dsg-test-queue \
        LIMIT=99999 \
        ./add_to_queue.py

add-items-ARDC-L7Tanzania_Original_Data:
	AWS_DEFAULT_REGION=us-west-2 \
        IN_BUCKET=deafrica-staging-west \
        IN_PATH=ARDC-L7Tanzania_Original_Data \
        QUEUE=dsg-test-queue \
        LIMIT=99999 \
        ./add_to_queue.py

add-items-ARDC-L8Ghanna_Original_Data:
	AWS_DEFAULT_REGION=us-west-2 \
        IN_BUCKET=deafrica-staging-west \
        IN_PATH=ARDC-L8Ghanna_Original_Data \
        QUEUE=dsg-test-queue \
        LIMIT=99999 \
        ./add_to_queue.py

add-items-ARDC-L8Kenga_Original_Data:
	AWS_DEFAULT_REGION=us-west-2 \
        IN_BUCKET=deafrica-staging-west \
        IN_PATH=ARDC-L8Kenya_Original_Data \
        QUEUE=dsg-test-queue \
        LIMIT=99999 \
        ./add_to_queue.py

add-items-ARDC-L8Senegal_Original_Data:
	AWS_DEFAULT_REGION=us-west-2 \
        IN_BUCKET=deafrica-staging-west \
        IN_PATH=ARDC-L8Senegal_Original_Data \
        QUEUE=dsg-test-queue \
        LIMIT=99999 \
        ./add_to_queue.py

add-items-ARDC-L8SierraLeone_Original_Data:
	AWS_DEFAULT_REGION=us-west-2 \
        IN_BUCKET=deafrica-staging-west \
        IN_PATH=ARDC-L8SierraLeone_Original_Data \
        QUEUE=dsg-test-queue \
        LIMIT=99999 \
        ./add_to_queue.py

add-items-ARDC-L8Tanzania_Original_Data:
	AWS_DEFAULT_REGION=us-west-2 \
        IN_BUCKET=deafrica-staging-west \
        IN_PATH=ARDC-L8Tanzania_Original_Data \
        QUEUE=dsg-test-queue \
        LIMIT=99999 \
        ./add_to_queue.py

add-items-cape-verde:
	AWS_DEFAULT_REGION=us-west-2 \
        IN_BUCKET=deafrica-staging-west \
        IN_PATH=from_frontiersi/cape-verde \
        QUEUE=dsg-test-queue \
        LIMIT=99999 \
        ./add_to_queue.py

