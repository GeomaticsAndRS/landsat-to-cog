#!/usr/bin/env python3

import os

from process_landsat import get_matching_s3_keys
import boto3

s3 = boto3.client('s3')

LIMIT = int(os.environ.get('LIMIT', 3))


def get_all_s3_keys(bucket):
    """Get a list of all keys in an S3 bucket."""
    keys = []

    kwargs = {'Bucket': bucket}
    while True:
        resp = s3.list_objects_v2(**kwargs)
        for obj in resp['Contents']:
            keys.append(obj['Key'].split('/')[-1])

        try:
            kwargs['ContinuationToken'] = resp['NextContinuationToken']
        except KeyError:
            break

    return keys

#
if __name__ == "__main__":
    bucket = 'in-test-results-deafrica-staging-west'
    bucket = 'deafrica-staging-west'
    # prefix = 'L5-Ghana-original'
    prefix_list = ['L5-Kenya_original', 'L5-Tanzania_original', 'rwanda_burundi_new']
    prefix_list = ['L5-Ghana_original', 'L5-Ghana_original_dup']
    thelist = []
    names = []
    full_names = []
    keys = get_all_s3_keys(bucket)
    #thelist.extend(keys)
    theset = set(keys)
    print ('len theset {}', len(theset))
    print ('len list {}', len(keys))
    #print (keys)
    #print (full_names)




if False:
    bucket = 'in-test-results-deafrica-staging-west'
    #bucket = 'deafrica-staging-west'
    # prefix = 'L5-Ghana-original'
    prefix_list = ['L5-Kenya_original', 'L5-Tanzania_original', 'rwanda_burundi_new']
    prefix_list = ['L5-Ghana_original', 'L5-Ghana_original_dup']
    thelist = []
    names = []
    full_names = []
    for prefix in prefix_list:
        print(bucket)
        print(prefix)
        items = get_matching_s3_keys(bucket, prefix=prefix)
        for item in items:
            names.append(item.split('/')[-1])
            full_names.append(item)
       # thelist.extend(items)
    theset = set(names)
    print ('len theset {}', len(theset))
    print ('len list {}', len(names))
    print (names)
    print (full_names)
#    for item in items:
 #       print(items)

