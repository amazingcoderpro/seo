from apscheduler.schedulers.background import BackgroundScheduler
import datetime
import threading
import time
import pymysql
import os

from io import BytesIO
import base64
from PIL import Image
import requests

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

    def product(self, url=""):
        """
                 获取所有店铺的所有products, 并保存至数据库
                 :return:
                 """
        logger.info("update_shopify_data is cheking...")
        try:
            conn = DBUtil().get_instance()
            cursor = conn.cursor() if conn else None
            if not cursor:
                return False

            if url:
                cursor.execute('''select id, name, url, token, user_id, store_view_id from `store` where url=%s''',
                               (url,))
            else:
                cursor.execute("""select id from `user` where is_active=1""")
                users = cursor.fetchall()
                users_list = [user[0] for user in users]
                cursor.execute(
                    '''select id, name, url, token, user_id, store_view_id from `store` where user_id in %s''',
                    (users_list,))
            stores = cursor.fetchall()

            # 取中已经存在的所有products, 只需更新即可
            cursor.execute('''select id, uuid from `product` where id>=0''')
            exist_products = cursor.fetchall()
            exist_products_dict = {}
            for exp in exist_products:
                exist_products_dict[exp[1]] = exp[0]

            cursor.execute('''select tag from `product_history_data` where id>0''')
            tags = cursor.fetchall()
            tag_list = [tag[0] if tag[0] else 0 for tag in tags]
            tag_max = max(tag_list)

            # 遍历数据库中的所有store
            for store in stores:
                store_id, store_name, store_url, store_token, user_id, store_view_id = store
                if not all([store_url, store_token]):
                    logger.warning("store url or token is invalid, store id={}".format(store_id))
                    continue

                cursor.execute('''select username from `user` where id=%s''', (user_id,))
                user = cursor.fetchone()
                store_uri = ""
                if user:
                    store_uri = user[0]

                if "shopify" not in store_uri:
                    logger.error("store uri={}, not illegal")
                    continue

                # 更新店铺信息
                papi = ProductsApi(store_token, store_uri)

                since_id = ""
                max_fetch = 50  # 不管拉没拉完，最多拉250＊50个产品
                while max_fetch > 0:
                    max_fetch -= 1
                    uuid_list = []
                    ret = papi.get_all_products(limit=250, since_id=since_id)
                    if ret["code"] == 1:
                        time_now = datetime.datetime.now()
                        products = ret["data"].get("products", [])
                        logger.info("get all products succeed, limit=250, since_id={}, len products={}".format(since_id,
                                                                                                               len(
                                                                                                                   products)))
                        for pro in products:
                            # print(products)
                            pro_uuid = str(pro.get("id", ""))
                            if pro_uuid in uuid_list:
                                continue

                            pro_title = pro.get("title", "")
                            handle = pro.get("handle", "")
                            pro_url = "https://{}/products/{}".format(store_url, handle)
                            pro_type = pro.get("product_type", "")
                            variants = pro.get("variants", [])
                            pro_sku = ""

                            pro_price = 0
                            if variants:
                                pro_sku = variants[0].get("sku", "")
                                pro_price = float(variants[0].get("price", "0"))

                            pro_tags = pro.get("tags", "")
                            img_obj = pro.get("image", {})
                            if img_obj:
                                pro_image = img_obj.get("src", "")
                            elif pro.get("images", []):
                                pro_image = pro.get("images")[0]
                            else:
                                pro_image = ""
                            thumbnail = self.image_2_base64(pro_image)
                            try:
                                if pro.get("published_at", ""):
                                    time_str = pro.get("published_at", "")[0:-6]
                                    pro_publish_time = datetime.datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S")
                                else:
                                    pro_publish_time = None
                            except:
                                pro_publish_time = None

                            try:
                                if pro_uuid in exist_products_dict.keys():
                                    pro_id = exist_products_dict[pro_uuid]
                                    logger.info(
                                        "product is already exist, pro_uuid={}, pro_id={}".format(pro_uuid, pro_id))
                                    cursor.execute(
                                        '''update `product` set sku=%s, url=%s, name=%s, price=%s, tag=%s, update_time=%s, image_url=%s, thumbnail=%s, publish_time=%s where id=%s''',
                                        (pro_sku, pro_url, pro_title, pro_price, pro_tags, time_now, pro_image,
                                         thumbnail, pro_publish_time, pro_id))
                                else:
                                    cursor.execute(
                                        "insert into `product` (`sku`, `url`, `name`, `image_url`,`thumbnail`, `price`, `tag`, `create_time`, `update_time`, `store_id`, `publish_time`, `uuid`) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                                        (pro_sku, pro_url, pro_title, pro_image, thumbnail, pro_price, pro_tags,
                                         time_now,
                                         time_now, store_id, pro_publish_time, pro_uuid))
                                    pro_id = cursor.lastrowid

                                conn.commit()
                                uuid_list.append(pro_uuid)
                            except:
                                logger.exception("update product exception.")

                            if not store_view_id:
                                logger.warning(
                                    "this product have no store view id, product id={}, store id={}".format(pro_id,
                                                                                                            store_id))
                                continue

                            # pro_uuid = "google" # 测试
                            # ga_data = gapi.get_report(key_word=pro_uuid, start_time="1daysAgo", end_time="today")
                            time_now = datetime.datetime.now()
                        # 拉完了
                        if len(products) < 250:
                            break
                        else:
                            since_id = products[-1].get("id", "")
                            if not since_id:
                                break
                    else:
                        logger.warning("get shop products failed. ret={}".format(ret))
                        break

        except Exception as e:
            logger.exception("get_products e={}".format(e))
            return False
        finally:
            cursor.close() if cursor else 0
            conn.close() if conn else 0
        return True


    def image_2_base64(self, image_src, is_thumb=True, size=(70, 70), format='png'):
        try:
            base64_str = ""
            if not image_src:
                return base64_str
            if not os.path.exists(image_src):
                response = requests.get(image_src)
                image = Image.open(BytesIO(response.content))
            else:
                image = Image.open(image_src)

            if is_thumb:
                image.thumbnail(size)

            output_buffer = BytesIO()
            if "jp" in image_src[-4:]:
                format = "JPEG"
            image.save(output_buffer, format=format)
            byte_data = output_buffer.getvalue()
            base64_str = base64.b64encode(byte_data)
            base64_str = base64_str.decode("utf-8")
        except Exception as e:
            logger.error("image_2_base64 e={}".format(e))
        return base64_str

def main():
    tsp = TaskProcessor()
    tsp.start_all(product_collections_interval=3600, product_interval=3600)
    while 1:
        time.sleep(1)


if __name__ == '__main__':
    main()