#!/usr/bin/env python3

import os

from process_landsat import get_items


LIMIT = int(os.environ.get('LIMIT', 10))

if __name__ == "__main__":
    get_items(LIMIT=LIMIT)
