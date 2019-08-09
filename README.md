# Landsat-to-cog
This converts zipped USGS landsat data to cloud optimised geotiffs (COGs)
 using AWS infrastructure.
Also, this repository defines Docker and Kubernetes components to support the conversion.

---
## Requirements
- Amazon EKS; There needs to be Kubernetes cluster to deploy to.
- Two AWS SQS queues; one will be used to identify .zip files to COG, the other is a deadletter queue for failed jobs.
- AWS S3 buckets; used to store the input zip files and the output COGs.
- IAM Permissions need to be set up correctly to access the queues and S3 buckets.

---
## Application Architecture
<!---
This image was created using https://www.draw.io/. Thanks for your help Tom.
-->

![application-architecture](img/orchestration-app.png)


---
## Process
Using landsat-to-cog is a manual process. To add zip files to the queue set the appropriate environment variables
  and run `add_to_queue.py`.
Note there are examples saved in the `Makefile` that can be executed with commands
such as `make add-items-cape-verde`.

A kubenetes deployment configuration is used to set-up the main process. An example of this is
 `k8s\user-africa-dev-pod.yaml`. The deployment can be managed using `Kubectl`, the
 Kubernetes command line interface. The table below gives examples of useful `Kubectl` commands.

<!---
https://www.tablesgenerator.com/markdown_tables#
-->

| Action                     | Command                                                         |
|----------------------------|-----------------------------------------------------------------|
| Create                     | `kubectl create -f user-africa-dev-pod.yaml`                    |
| Delete                     | `kubectl delete -f user-africa-dev-pod.yaml`                    |
| Monitor                    | `kubectl get pods`                                              |
| Get logs                   | `kubectl logs -f africa-frak-deployment-fcb56b69c-xlvl`         |
| Change # of  deployed pods | `kubectl scale deployment africa-frak-deployment --replicas=51` |

So firstly create the deployment to process the jobs.  Monitor it via the Kubernetes command line interface
and the SQS AWS page.
Scale up the deployment to meet demand. When the message queue has been processed the deployment can be deleted.
