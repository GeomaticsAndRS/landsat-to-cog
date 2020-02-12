push:
	docker build --tag alexgleith/landsat-to-cog .
	docker push alexgleith/landsat-to-cog

up:
	docker-compose up

add-items:
	docker-compose run \
		-e LIMIT=1000000 \
		pygdal \
		./add_to_queue.py

deploy:
	kubectl create -f k8s/landsat-processor.yaml

update-deployment:
	kubectl replace -f k8s/landsat-processor.yaml

delete-deployment:
	kubectl delete deployment landsat-processor-deployment

# add-items-L5-Ghana_original:
# 	AWS_DEFAULT_REGION=us-west-2 \
# 	IN_BUCKET=deafrica-staging-west \
# 	IN_PATH=L5-Ghana_original \
# 	QUEUE=dsg-test-queue \
# 	LIMIT=705 \
# 	./add_to_queue.py

# add-items-L5-Kenya_original:
# 	AWS_DEFAULT_REGION=us-west-2 \
#         IN_BUCKET=deafrica-staging-west \
#         IN_PATH=L5-Kenya_original \
#         QUEUE=dsg-test-queue \
#         LIMIT=2670 \
#         ./add_to_queue.py

# add-items-L5-Senegal_original:
# 	AWS_DEFAULT_REGION=us-west-2 \
#         IN_BUCKET=deafrica-staging-west \
#         IN_PATH=L5-Senegal_original \
#         QUEUE=dsg-test-queue \
#         LIMIT=1500 \
#         ./add_to_queue.py

# add-items-L5-SierraLeone_original:
# 	AWS_DEFAULT_REGION=us-west-2 \
#         IN_BUCKET=deafrica-staging-west \
#         IN_PATH=L5-SierraLeone_original \
#         QUEUE=dsg-test-queue \
#         LIMIT=340 \
#         ./add_to_queue.py

# add-items-L5-Tanzania_original:
# 	AWS_DEFAULT_REGION=us-west-2 \
#         IN_BUCKET=deafrica-staging-west \
#         IN_PATH=L5-Tanzania_original \
#         QUEUE=dsg-test-queue \
#         LIMIT=5650 \
#         ./add_to_queue.py

# add-items-rwanda_burundi_new:
# 	AWS_DEFAULT_REGION=us-west-2 \
#         IN_BUCKET=deafrica-staging-west \
#         IN_PATH=rwanda_burundi_new \
#         QUEUE=dsg-test-queue \
#         LIMIT=5650 \
#         ./add_to_queue.py

# add-items-L7-Tanzania_original2:
# 	AWS_DEFAULT_REGION=us-west-2 \
#         IN_BUCKET=deafrica-staging-west \
#         IN_PATH=L7-Tanzania_original2 \
#         QUEUE=dsg-test-queue \
#         LIMIT=99999 \
#         ./add_to_queue.py

# add-items-ARDC-L7Ghana_Original_Data:
# 	AWS_DEFAULT_REGION=us-west-2 \
#         IN_BUCKET=deafrica-staging-west \
#         IN_PATH=ARDC-L7Ghana_Original_Data \
#         QUEUE=dsg-test-queue \
#         LIMIT=99999 \
#         ./add_to_queue.py

# add-items-ARDC-L7Kenya_Original_Data:
# 	AWS_DEFAULT_REGION=us-west-2 \
#         IN_BUCKET=deafrica-staging-west \
#         IN_PATH=ARDC-L7Kenya_Original_Data \
#         QUEUE=dsg-test-queue \
#         LIMIT=99999 \
#         ./add_to_queue.py

# add-items-ARDC-L7Senegal_Original_Data:
# 	AWS_DEFAULT_REGION=us-west-2 \
#         IN_BUCKET=deafrica-staging-west \
#         IN_PATH=ARDC-L7Senegal_Original_Data \
#         QUEUE=dsg-test-queue \
#         LIMIT=99999 \
#         ./add_to_queue.py

# add-items-ARDC-L7SierraLeone_Original_Data:
# 	AWS_DEFAULT_REGION=us-west-2 \
#         IN_BUCKET=deafrica-staging-west \
#         IN_PATH=ARDC-L7SierraLeone_Original_Data \
#         QUEUE=dsg-test-queue \
#         LIMIT=99999 \
#         ./add_to_queue.py

# add-items-ARDC-L7Tanzania_Original_Data:
# 	AWS_DEFAULT_REGION=us-west-2 \
#         IN_BUCKET=deafrica-staging-west \
#         IN_PATH=ARDC-L7Tanzania_Original_Data \
#         QUEUE=dsg-test-queue \
#         LIMIT=99999 \
#         ./add_to_queue.py

# add-items-ARDC-L8Ghanna_Original_Data:
# 	AWS_DEFAULT_REGION=us-west-2 \
#         IN_BUCKET=deafrica-staging-west \
#         IN_PATH=ARDC-L8Ghanna_Original_Data \
#         QUEUE=dsg-test-queue \
#         LIMIT=99999 \
#         ./add_to_queue.py

# add-items-ARDC-L8Kenga_Original_Data:
# 	AWS_DEFAULT_REGION=us-west-2 \
#         IN_BUCKET=deafrica-staging-west \
#         IN_PATH=ARDC-L8Kenya_Original_Data \
#         QUEUE=dsg-test-queue \
#         LIMIT=99999 \
#         ./add_to_queue.py

# add-items-ARDC-L8Senegal_Original_Data:
# 	AWS_DEFAULT_REGION=us-west-2 \
#         IN_BUCKET=deafrica-staging-west \
#         IN_PATH=ARDC-L8Senegal_Original_Data \
#         QUEUE=dsg-test-queue \
#         LIMIT=99999 \
#         ./add_to_queue.py

# add-items-ARDC-L8SierraLeone_Original_Data:
# 	AWS_DEFAULT_REGION=us-west-2 \
#         IN_BUCKET=deafrica-staging-west \
#         IN_PATH=ARDC-L8SierraLeone_Original_Data \
#         QUEUE=dsg-test-queue \
#         LIMIT=99999 \
#         ./add_to_queue.py

# add-items-ARDC-L8Tanzania_Original_Data:
# 	AWS_DEFAULT_REGION=us-west-2 \
#         IN_BUCKET=deafrica-staging-west \
#         IN_PATH=ARDC-L8Tanzania_Original_Data \
#         QUEUE=dsg-test-queue \
#         LIMIT=99999 \
#         ./add_to_queue.py

# add-items-cape-verde:
# 	AWS_DEFAULT_REGION=us-west-2 \
#         IN_BUCKET=deafrica-staging-west \
#         IN_PATH=from_frontiersi/cape-verde \
#         QUEUE=dsg-test-queue \
#         LIMIT=99999 \
#         ./add_to_queue.py

