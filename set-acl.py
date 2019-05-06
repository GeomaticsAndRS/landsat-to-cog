#!/usr/bin/env python3
import boto3
from process_landsat import get_matching_s3_keys

BUCKET='frontiersi-odc-test'
PATH='rwanda-test'
client = boto3.client('s3')

LIMIT=False

def set_acls():
    all_keys = get_matching_s3_keys(BUCKET, prefix=PATH)

    count = 0
    for key in all_keys:
        print("Working on key: {}".format(key))
        count += 1
        if not LIMIT or count < LIMIT:
            client.put_object_acl(
                ACL='public-read',
                Bucket=BUCKET,
                Key=key
            )
        else:
            break
    print("Finished working on {} keys".format(count))


if __name__ == "__main__":
    set_acls()