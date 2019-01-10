#!/usr/bin/env python3

from process_landsat import get_items


if __name__ == "__main__":
    get_items(10, 'LC08')
    get_items(10, 'LT05')
    get_items(10, 'LE07')
