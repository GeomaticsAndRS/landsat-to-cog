#!/usr/bin/env python3

import json

from process_landsat import get_metadata

file = "temp/LC081720622018080501T1-SC20181129194514/LC08_L1TP_172062_20180805_20180814_01_T1.xml"
meta = get_metadata(file)

print(meta)
