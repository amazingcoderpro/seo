from apscheduler.schedulers.background import BackgroundScheduler
import threading
import time
import pymysql

from sdk.shopify.get_shopify_products import ProductsApi
from config import logger


class DBUtil:
    def __init__(self, host="47.112.113.252", port=3306, db="seo", user="seo", password="seo@orderplus.com"):
        self.conn_pool = {}
        self.host = host
        self.port = port
        self.db = db
        self.user = user
        self.pwd = password

    def get_instance(self):
        try:
            name = threading.current_thread().name
            if name not in self.conn_pool:
                conn = pymysql.connect(
                    host=self.host,
                    port=self.port,
                    db=self.db,
                    user=self.user,
                    password=self.pwd,
                    charset='utf8'
                )
                self.conn_pool[name] = conn
        except Exception as e:
            logger.exception("connect mysql error, e={}".format(e))
            return None
        return self.conn_pool[name]


class TaskProcessor:
    def __init__(self, ):
        self.bk_scheduler = BackgroundScheduler()
        self.bk_scheduler.start()
        self.product_collections_job = None
        self.product_job = None

    def start_all(self, product_collections_interval=3600,product_interval=3600):
        logger.info("TaskProcessor start all work.")
        self.start_job_product_collections(product_collections_interval)
        self.start_job_product_job(product_interval)

    def start_job_product_collections(self, interval):
        logger.info("start_job_product_collections")
        self.product_collections()
        self.product_collections_job = self.bk_scheduler.add_job(self.product_collections, 'interval', seconds=interval, max_instances=50)

    def start_job_product_job(self, interval):
        logger.info("start_job_product_job")
        self.product()
        self.product_job = self.bk_scheduler.add_job(self.product, 'interval', seconds=interval, max_instances=50)

    def product_collections(self):
        logger.info("product_collections checking...")
        try:
            conn = DBUtil().get_instance()
            cursor = conn.cursor() if conn else None
            if not cursor:
                return False

            cursor.execute('''select id, name, uri, token, user_id from `store` where id = 2''')
            store = cursor.fetchall()
            if not store:
                logger.info("there have no new store to analyze.")
                return True
            print(store[0][3])
            print(store[0][2])
            collections = ProductsApi(store[0][3],store[0][2]).get_custom_collections()
            print(collections)
        except Exception as e:
            pass


    def product(self):
        pass

def main():
    tsp = TaskProcessor()
    tsp.start_all(product_collections_interval=3600, product_interval=3600)
    while 1:
        time.sleep(1)


if __name__ == '__main__':
    main()