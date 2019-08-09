# Landsat-to-cog
This converts zipped USGS landsat data to cloud optimised geotiffs (COGs)
 using AWS infrastructure.
Also, this repository defines Docker and Kubernetes components to support the conversion.

# Requirements
- Two AWS SQS queues; one will be used to identify .zip files to COG, the other is a deadletter queue for failed jobs.
- AWS S3 buckets; used to store the input zip files and the output COGs.
- IAM Permissions need to be set up correctly to access the queues and S3 buckets.

## Application Architecture

![application-architecture](img/orchestration-app.png)

