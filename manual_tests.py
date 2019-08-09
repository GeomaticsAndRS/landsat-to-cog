#!/usr/bin/env python3

from process_landsat import get_matching_s3_keys


if __name__ == "__main__":
    results = get_matching_s3_keys('frontiersi-odc-test', 'from-tony/alex1129', '.tar.gz')

    for key in results:
        print(key)
