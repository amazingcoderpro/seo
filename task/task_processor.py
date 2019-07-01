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

MYSQL_PASSWD = os.getenv('MYSQL_PASSWD', None)
MYSQL_HOST = os.getenv('MYSQL_HOST', None)


class DBUtil:
    def __init__(self, host=MYSQL_HOST, port=3306, db="seo", user="seo", password=MYSQL_PASSWD):
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
        self.update_product_job = None
        self.update_collection_job = None

    def start_all(self, product_collections_meta_interval=3600, product_meta_interval=600, product_interval=3600):
        logger.info("TaskProcessor start all work.")
        # 修改产品类目meta
        # self.motify_product_collections_meta()
        # self.product_collections_job = self.bk_scheduler.add_job(self.motify_product_collections_meta, 'interval', seconds=product_collections_meta_interval, max_instances=50)
        # 修改产品meta
        self.motify_product_meta()
        self.product_job = self.bk_scheduler.add_job(self.motify_product_meta, 'interval',
                                                     seconds=product_meta_interval, max_instances=1)
        # 更新产品
        # self.update_product()
        self.update_product_job = self.bk_scheduler.add_job(self.update_product, 'interval', seconds=product_interval,
                                                            max_instances=1)
        # 更新类目信息
        self.update_collection()
        self.update_collection_job = self.bk_scheduler.add_job(self.update_collection, 'interval',
                                                               seconds=product_collections_meta_interval,
                                                               max_instances=1)

    def motify_product_collections_meta(self):
        pass
        # logger.info("product_collections checking...")
        # try:
        #     conn = DBUtil().get_instance()
        #     cursor = conn.cursor() if conn else None
        #     if not cursor:
        #         return False
        #
        #     cursor.execute('''select id, name, uri, token, user_id from `store` where id = 2''')
        #     store = cursor.fetchall()
        #     if not store:
        #         logger.info("there have no new store to analyze.")
        #         return True
        #     print(store[0][3])
        #     print(store[0][2])
        #     collections = ProductsApi(store[0][3],store[0][2]).get_custom_collections()
        #     print(collections)
        # except Exception as e:
        #     pass

    def motify_product_meta(self):
        """修改产品meta"""
        logger.info("motify_product_meta checking...")
        try:
            conn = DBUtil().get_instance()
            cursor = conn.cursor() if conn else None
            if not cursor:
                return False

            cursor.execute(
                '''select store.id,store.token,store.url from store left join user on store.user_id = user.id where user.is_active = 1''')
            stores = cursor.fetchall()
            if not stores:
                logger.info("there have no new store to analyze.")
                return True
            # store_list = [item[0] for item in store]
            for store in stores:
                cursor.execute(
                    '''select id, domain, price, uuid, type, title, remark_title, remark_description, variants from `product` where state=1 and store_id=%s''',
                    (store[0],))
                products = cursor.fetchall()
                if not products:
                    continue
                for item in products:
                    id, domain, price, uuid, type, title, remark_title, remark_description, variants = item
                    logger.info("start motify_product_meta product_id={}, store_id={}".format(id, store[0]))
                    url = domain.split("//")[1].split(".")[0] + ".com"
                    remark_dict = {"%Product Type%": type, "%Product Title%": title, "%Variants%": variants,
                                   "%Product Price%": price, "%Domain%": url}
                    for row in remark_dict:
                        remark_title = remark_title.replace(row, remark_dict[row])
                        remark_description = remark_description.replace(row, remark_dict[row])
                    result = ProductsApi(store[1], store[2]).motify_product_meta(uuid, remark_title, remark_description)
                    if result["code"] == 1:
                        logger.error("successful motify_product_meta product_id={}, store_id={}".format(id, store[0]))
                        cursor.execute(
                            '''update `product` set meta_title=%s, meta_description=%s, state=2 where id=%s''',
                            (remark_title, remark_description, id))
                    else:
                        logger.error("faild motify_product_meta product_id={}, store_id={}".format(id, store[0]))
                        cursor.execute(
                            '''update `product` set error_text=%s, state=3 where id=%s''',
                            (result["data"], id))
                    conn.commit()
        except Exception as e:
            logger.exception("motify_product_meta e={}".format(e))
            return False
        finally:
            cursor.close() if cursor else 0
            conn.close() if conn else 0
        return True

    def update_collection(self, url=""):
        """
        获取所有店铺的所有类目，并保存至数据库
        :param url: 店铺url
        :return:
        """
        logger.info("update_collection is cheking...")
        try:
            conn = DBUtil().get_instance()
            cursor = conn.cursor() if conn else None
            if not cursor:
                return False

            if url:
                cursor.execute(
                    '''select store.id, store.url,store.token from store left join user on store.user_id = user.id where user.is_active = 1 and url=%s''',
                    (url,))
            else:
                cursor.execute(
                    """select store.id, store.url,store.token from store left join user on store.user_id = user.id where user.is_active = 1""")
            stores = cursor.fetchall()

            # 遍历数据库中的所有store，更新产品信息
            for store in stores:
                # 删除当前店铺下所有的类目，拉最新类目信息插入
                store_id, store_uri, store_token = store
                if not all([store_uri, store_token]):
                    logger.warning("store url or token is invalid, store id={}".format(store_id))
                    continue

                if "shopify" not in store_uri:
                    logger.error("store uri={}, not illegal")
                    continue

                # 更新产品信息
                papi = ProductsApi(store_token, store_uri)
                res = papi.get_all_collections()
                if res["code"] == 1:
                    # 删除当前店铺所有类目信息
                    cursor.execute("""delete from collection where store_id = %s""", (store_id,))
                    # 插入新的数据
                    for collection in res["data"]:
                        uuid, meta_title, address, meta_description = collection.values()
                        now_time = datetime.datetime.now()
                        logger.info(
                            "update collection data: {} {} {} {}".format(uuid, address, meta_title, meta_description))
                        try:
                            cursor.execute(
                                '''insert into `collection` set uuid=%s, address=%s, meta_title=%s, meta_description=%s, store_id=%s, create_time=%s, update_time=%s''',
                                (uuid, address, meta_title, meta_description, store_id, now_time, now_time))
                            conn.commit()
                        except Exception as e:
                            logger.exception("update product exception.")
                else:
                    logger.warning("get shop collections failed. res={}".format(res))

        except Exception as e:
            logger.exception("update_collection e={}".format(e))
            return False
        finally:
            cursor.close() if cursor else 0
            conn.close() if conn else 0
        return True

    def update_product(self, url=""):
        """
         获取所有店铺的所有products, 并保存至数据库
         :return:
         """
        logger.info("update_product is cheking...")
        try:
            conn = DBUtil().get_instance()
            cursor = conn.cursor() if conn else None
            if not cursor:
                return False

            if url:
                cursor.execute(
                    '''select store.id, store.url,store.token from store left join user on store.user_id = user.id where user.is_active = 1 and url=%s''',
                    (url,))
            else:
                cursor.execute(
                    """select store.id, store.url,store.token from store left join user on store.user_id = user.id where user.is_active = 1""")
            stores = cursor.fetchall()

            # 遍历数据库中的所有store，更新产品信息
            for store in stores:
                store_id, store_uri, store_token = store

                # 取中已经存在的所有products, 只需更新即可
                cursor.execute('''select id, uuid from `product` where store_id=%s''', (store_id))
                exist_products = cursor.fetchall()
                exist_products_dict = {}
                for exp in exist_products:
                    exist_products_dict[exp[1]] = exp[0]

                if not all([store_uri, store_token]):
                    logger.warning("store url or token is invalid, store id={}".format(store_id))
                    continue

                if "shopify" not in store_uri:
                    logger.error("store uri={}, not illegal")
                    continue

                # 更新产品信息
                papi = ProductsApi(store_token, store_uri)

                since_id = ""
                max_fetch = 50  # 不管拉没拉完，最多拉250＊50个产品
                uuid_list = []
                while max_fetch > 0:
                    max_fetch -= 1
                    ret = papi.get_all_products(limit=250, since_id=since_id)
                    if ret["code"] != 1:
                        logger.warning("get shop products failed. ret={}".format(ret))
                        break
                    if ret["code"] == 1:
                        products = ret["data"].get("products", [])
                        logger.info("get all products succeed, limit=250, since_id={}, len products={}".format(since_id,
                                                                                                               len(
                                                                                                                   products)))
                        for pro in products:
                            uuid = str(pro.get("id", ""))
                            if uuid in uuid_list:
                                continue
                            sku = pro.get("handle", "")
                            title = pro.get("title", "")
                            domain = "https://{}/products/{}".format(store_uri, sku)
                            type = pro.get("product_type", "")
                            variants = pro.get("variants", [])
                            sku = pro.get("handle", "")
                            price = variants[0].get("price", "") if variants else 0
                            time_now = datetime.datetime.now()
                            variants_price_str = ""
                            variants_color_str = " Color"
                            variants_size_str = " Size"
                            variants_str = ""
                            if variants:
                                for item in variants:
                                    variants_price_str += " " + item["price"]
                                    variants_color_str += " " + item["option1"]
                                    variants_size_str += " " + item["option2"] if item["option2"] else ""
                                tmp_str = variants_price_str + variants_color_str + variants_size_str
                                variants_tmp_list = tmp_str.split(" ")
                                variants_list = list(set(variants_tmp_list))
                                variants_list.sort(key=variants_tmp_list.index)
                                variants_str = " ".join(variants_list) + " Sku " + str(sku)

                            img_obj = pro.get("image", {})
                            if img_obj:
                                pro_image = img_obj.get("src", "")
                            elif pro.get("images", []):
                                pro_image = pro.get("images")[0]
                            else:
                                pro_image = ""
                            thumbnail = self.image_2_base64(pro_image)

                            logger.info(
                                "update product data: {} {} {} {} {} {} {} {} {} {}".format(sku, variants_str, price,
                                                                                            type, domain, title,
                                                                                            time_now, time_now,
                                                                                            store_id, uuid))
                            try:
                                if uuid in exist_products_dict.keys():
                                    pro_id = exist_products_dict[uuid]
                                    logger.info(
                                        "product is already exist, pro_uuid={}, pro_id={}".format(uuid, pro_id))

                                    cursor.execute(
                                        '''update `product` set thumbnail=%s, sku=%s, variants=%s, price=%s, type=%s, domain=%s, title=%s, update_time=%s where id=%s''',
                                        (thumbnail, sku, variants_str, price, type, domain, title, time_now, pro_id))
                                else:
                                    cursor.execute(
                                        "insert into `product` (`thumbnail`, `sku`, `variants`, `price`, `type`,`domain`, `title`,`create_time`, `update_time`, `store_id`, `uuid`, `state`) values (%s, %s,%s,%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                                        (thumbnail, sku, variants_str, price, type, domain, title, time_now, time_now,
                                         store_id, uuid, 0))
                                    pro_id = cursor.lastrowid

                                conn.commit()
                                uuid_list.append(uuid)
                            except Exception as e:
                                logger.exception("update product exception.")

                        # 拉完了
                        if len(products) < 250:
                            break
                        else:
                            since_id = products[-1].get("id", "")
                            if not since_id:
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
    tsp.start_all(product_collections_meta_interval=3600, product_meta_interval=600, product_interval=3600)
    while 1:
        time.sleep(1)


if __name__ == '__main__':
    # main()
    # TaskProcessor().product()
    # TaskProcessor().update_product()
    TaskProcessor().update_collection()
    # TaskProcessor().motify_product_meta()
