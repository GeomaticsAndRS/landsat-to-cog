build:
	docker-compose build

process-one:
	docker-compose run pygdal \
		./geotiff-cog.py --path /opt/data/one --output /opt/data/out

process-many:
	docker-compose run pygdal \
		./geotiff-cog.py --path /opt/data/many --output /opt/data/out