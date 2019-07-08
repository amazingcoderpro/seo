#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by charles on 2019-06-06
# Function:
import time
from task.task_processor import TaskProcessor


def main():
    tsp = TaskProcessor()
    tsp.start_all(product_collections_meta_interval=3600, product_meta_interval=600, product_interval=3600)
    while 1:
        time.sleep(1)


if __name__ == '__main__':
    main()
    #TaskProcessor().update_product()