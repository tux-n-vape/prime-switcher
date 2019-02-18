#!/bin/env python3

import switchers

open_driver = True

if __name__ == '__main__':
    sw = switchers.NvidiaSwitcher()
    print(sw.get_current_gpu_name())
