# -*-coding:utf-8-*-
import requests
from config import logger
import json
from config import SHOPIFY_CONFIG
import urllib.parse


class ProductsApi:
    def __init__(self, access_token, shop_uri):
        """
        :param client_id: api key
        :param access_token: api password
        :param shop_URI: 店铺uri
        :param scopes: 权限
        :param callback_uri: callback url
        :param code: 1 状态正确， 2 状态错误， -1 出现异常
        """
        self.client_id = SHOPIFY_CONFIG.get("client_id")
        self.access_token = access_token
        self.shop_uri = shop_uri
        self.scopes = SHOPIFY_CONFIG.get("scopes")
        self.callback_uri = SHOPIFY_CONFIG.get("callback_uri")
        self.version_url = "/admin/api/2019-04/"
        self.headers = {'Content-Type': 'application/json'}

    def get_all_collections(self):
        shop_url = f"https://{self.client_id}:{self.access_token}@{self.shop_uri}{self.version_url}custom_collections.json"
        shop_url2 = f"https://{self.client_id}:{self.access_token}@{self.shop_uri}{self.version_url}smart_collections.json"
        try:
            result = requests.get(shop_url)
            result2 = requests.get(shop_url2)

            if result.status_code == 200 and result2.status_code == 200:
                logger.info("get shopify all collections info is success")
                res_dict = json.loads(result.text)
                res_dict.update(json.loads(result2.text))
                return {"code": 1, "msg": "", "data": self.parse_collections(res_dict)}
            else:
                logger.info("get shopify all collections info is failed")
                return {"code": 2, "msg": json.loads(result.text).get("errors", ""), "data": ""}
        except Exception as e:
            logger.error("get shopify all collections info is failed info={}".format(str(e)))
            return {"code": -1, "msg": str(e), "data": ""}

    @classmethod
    def parse_collections(cls, data):
        all_collections = []
        for col in data["custom_collections"] + data["smart_collections"]:
            all_collections.append(
                {
                    "uuid": col.get("id", ""),
                    "meta_title": col.get("title", ""),
                    "address": "/collections/" + col.get("title", "").lower().replace("'", "").replace(" ", "-"),
                    "meta_description": col.get("body_html", ""),
                }
            )
        return all_collections

    def get_shop_info(self):
        """
        获取用户信息
        :return:
        """
        shop_url = f"https://{self.client_id}:{self.access_token}@{self.shop_uri}{self.version_url}shop.json"
        try:
            result = requests.get(shop_url)
            if result.status_code == 200:
                logger.info("get shopify info is success")
                return {"code": 1, "msg": "", "data": json.loads(result.text)}
            else:
                logger.info("get shopify info is failed")
                return {"code": 2, "msg": json.loads(result.text).get("errors", ""), "data": ""}
        except Exception as e:
            logger.error("get shopify info is failed info={}".format(str(e)))
            return {"code": -1, "msg": str(e), "data": ""}

    def get_all_products(self, limit=250, since_id=""):
        """
        获取所有商品的信息
        :return:
        """
        if not since_id:
            products_url = f"https://{self.client_id}:{self.access_token}@{self.shop_uri}{self.version_url}products.json?limit={limit}"
        if since_id:
            products_url = f"https://{self.client_id}:{self.access_token}@{self.shop_uri}{self.version_url}products.json?limit={limit}&since_id={since_id}"
        try:
            result = requests.get(products_url)
            if result.status_code == 200:
                logger.info("get shopify all products is success")
                # print(result.text)
                return {"code": 1, "msg": "", "data": json.loads(result.text)}
            else:
                logger.info("get shopify all products is failed")
                return {"code": 2, "msg": json.loads(result.text).get("errors", ""), "data": ""}
        except Exception as e:
            logger.error("get shopify all products is failed info={}".format(str(e)))
            return {"code": -1, "msg": str(e), "data": ""}

    def get_product_id(self, id):
        """
        通过 id 获取商品的信息
        :param id: 商品id
        :return:
        """
        products_url = f"https://{self.client_id}:{self.access_token}@{self.shop_uri}{self.version_url}products/{id}.json"
        try:
            result = requests.get(products_url)
            if result.status_code == 200:
                logger.info("get shopify all prodects by id is success")
                return {"code": 1, "msg": "", "data": json.loads(result.text)}
            else:
                logger.info("get shopify all prodects by id is failed")
                return {"code": 2, "msg": json.loads(result.text).get("errors", ""), "data": ""}
        except Exception as e:
            logger.error("get shopify all prodects by id is failed info={}".format(str(e)))
            return {"code": -1, "msg": str(e), "data": ""}

    def get_order(self, create_start_time, create_end_time, key_word, financial_status="paid"):
        """
         获取订单
        :param create_start_time: 创建订单之前的时间
        :param create_end_time: 创建订单之后的时间
        :param key_word:  搜索关键字
        :param financial_status: 订单状态
             pending：付款待定。在这种状态下付款可能会失败。再次检查以确认付款是否已成功支付。
             authorized：付款已获得授权。
             partially_paid：订单已部分支付。
             paid：付款已付款。
             partial_refunded：付款已部分退还。
             refunded：付款已退款。
             voided：付款已无效
        :return:
        """
        order_url = f"https://{self.client_id}:{self.access_token}@{self.shop_uri}{self.version_url}orders.json" \
            f"?created_at_min={create_start_time}&created_at_max={create_end_time}&financial_status={financial_status}"
        try:
            result = requests.get(order_url)
            if result.status_code == 200:
                order_list = json.loads(result.text).get("orders", "")
                order_count = 0
                total_price = 0
                for order_info in order_list:
                    referring_site = str(order_info.get("referring_site"))
                    if str(key_word) in referring_site:
                        order_count += 1
                        order_price = float(order_info.get("total_price"))
                        total_price += order_price
                result_info = {"order_count": order_count, "total_price": round(total_price, 4)}
                # print(result_info)
                logger.info("get shopify all order by id is success")
                return {"code": 1, "msg": "", "data": result_info}
            else:
                logger.info("get shopify all order by id is failed")
                return {"code": 2, "msg": json.loads(result.text).get("errors", ""), "data": ""}
        except Exception as e:
            logger.error("get shopify all order by id is failed; info={}".format(str(e)))
            return {"code": -1, "msg": str(e), "data": ""}

    # def motify_product_meta(self, product_id, key, value):
    #     display = {
    #       "metafield": {
    #         "namespace": "global",
    #         "key": key,
    #         "value": value,
    #         "value_type": "string"
    #       }
    #     }
    #     #shop_url = f"https://{self.client_id}:{self.access_token}@{self.shop_uri}{self.version_url}products/1831407157293/metafields.json"
    #     shop_url = f"https://{self.client_id}:{self.access_token}@{self.shop_uri}{self.version_url}products/%s/metafields.json" %(product_id)
    #
    #     logger.info("url={}, display={}, shop_uri={}".format(shop_url, display, self.shop_uri))
    #     try:
    #         result = requests.post(shop_url, json.dumps(display), headers=self.headers)
    #         if result.status_code == 200:
    #             logger.info("get shopify token is successed, shopname={}".format(self.shop_uri))
    #             print(result.text)
    #             return {"code": 1, "msg": "", "data": json.loads(result.text).get("access_token")}
    #         else:
    #             logger.error("get shopify token is failed")
    #             return {"code": 2, "msg": "oauth failed", "data": ""}
    #     except Exception as e:
    #         logger.error("get shopify token is exception {}".format(str(e)))
    #         return {"code": -1, "msg": str(e), "data": ""}

    def motify_product_meta(self, product_id, title_tag, description_tag):
        """修改产品meta
        链接地址：https://help.shopify.com/en/api/reference/products/product
        接口地址：PUT /admin/api/2019-04/products/#{product_id}.json
        """
        display = {
            "product": {
                "id": product_id,
                "metafields_global_title_tag": title_tag,
                "metafields_global_description_tag": description_tag
            }
        }
        shop_url = f"https://{self.client_id}:{self.access_token}@{self.shop_uri}{self.version_url}products/%s.json" %(product_id)
        logger.info("url={}, display={}, shop_uri={}".format(shop_url, display, self.shop_uri))
        try:
            result = requests.put(shop_url, json.dumps(display), headers=self.headers)
            if result.status_code == 200:
                logger.info("get shopify token is successed, shopname={}".format(self.shop_uri))
                return {"code": 1, "msg": "", "data": json.loads(result.text).get("access_token")}
            else:
                logger.error("get shopify token is failed")
                return {"code": 2, "msg": "oauth failed", "data": json.loads(result.text).get("errors")}
        except Exception as e:
            logger.error("get shopify token is exception {}".format(str(e)))
            return {"code": -1, "msg": str(e), "data": ""}

    def get_metafields(self):
        shop_url = f"https://{self.client_id}:{self.access_token}@{self.shop_uri}{self.version_url}products/1831407157293/metafields.json"
        try:
            result = requests.get(shop_url)
            if result.status_code == 200:
                logger.info("get shopify info is success")
                return {"code": 1, "msg": "", "data": json.loads(result.text)}
            else:
                logger.info("get shopify info is failed")
                return {"code": 2, "msg": json.loads(result.text).get("errors", ""), "data": ""}
        except Exception as e:
            logger.error("get shopify info is failed info={}".format(str(e)))
            return {"code": -1, "msg": str(e), "data": ""}

    # def update_collection_by_id(self, collection_id, title, description):
    #     smart_shop_url = f"https://{self.client_id}:{self.access_token}@{self.shop_uri}{self.version_url}/smart_collections/{collection_id}.json"
    #     smart_params = {
    #         "smart_collection": {
    #             "id": collection_id,
    #             "body_html": description,
    #             "title": title
    #         }
    #     }
    #     custom_shop_url = f"https://{self.client_id}:{self.access_token}@{self.shop_uri}{self.version_url}/custom_collections/{collection_id}.json"
    #     custom_params = {
    #         "custom_collection": {
    #             "id": collection_id,
    #             "body_html": description,
    #             "title": title,
    #         }
    #     }
    #     try:
    #         result = requests.put(smart_shop_url, json.dumps(smart_params), headers=self.headers)
    #         if result.status_code == 404:
    #             result = requests.put(custom_shop_url, json.dumps(custom_params), headers=self.headers)
    #         if result.status_code == 200:
    #             logger.info("update shopify a collection({}) info is success".format(collection_id))
    #             return {"code": 1, "msg": "", "data": json.loads(result.text)}
    #         else:
    #             logger.info("update shopify a collection({}) info is failed".format(collection_id))
    #             return {"code": 2, "msg": json.loads(result.text).get("errors", ""), "data": ""}
    #     except Exception as e:
    #         logger.error("update shopify a collection({}) info is failed info={}".format(collection_id, str(e)))
    #         return {"code": -1, "msg": str(e), "data": ""}

    def update_collection_seo_title(self, collection_id, title):
        shop_url = f"https://{self.client_id}:{self.access_token}@{self.shop_uri}{self.version_url}/collections/{collection_id}/metafields.json"
        params = {
          "metafield": {
            "namespace": "global",
            "key": "title_tag",
            "value": title,
            "value_type": "string"
          }
        }
        try:
            result = requests.post(shop_url, json.dumps(params), headers=self.headers)
            if result.status_code == 200 or result.status_code == 201:
                logger.info("update shopify a collection({}) info is success".format(collection_id))
                return {"code": 1, "msg": "", "data": json.loads(result.text)}
            else:
                logger.info("update shopify a collection({}) info is failed".format(collection_id))
                return {"code": 2, "msg": json.loads(result.text).get("errors", ""), "data": ""}
        except Exception as e:
            logger.error("update shopify a collection({}) info is failed info={}".format(collection_id, str(e)))
            return {"code": -1, "msg": str(e), "data": ""}

    def update_collection_seo_description(self, collection_id, description):
        shop_url = f"https://{self.client_id}:{self.access_token}@{self.shop_uri}{self.version_url}/collections/{collection_id}/metafields.json"
        params = {
          "metafield": {
            "namespace": "global",
            "key": "description_tag",
            "value": description,
            "value_type": "string"
          }
        }
        try:
            result = requests.post(shop_url, json.dumps(params), headers=self.headers)
            if result.status_code == 200 or result.status_code == 201:
                logger.info("update shopify a collection({}) info is success".format(collection_id))
                return {"code": 1, "msg": "", "data": json.loads(result.text)}
            else:
                logger.info("update shopify a collection({}) info is failed".format(collection_id))
                return {"code": 2, "msg": json.loads(result.text).get("errors", ""), "data": ""}
        except Exception as e:
            logger.error("update shopify a collection({}) info is failed info={}".format(collection_id, str(e)))
            return {"code": -1, "msg": str(e), "data": ""}


if __name__ == '__main__':
    client_id = "7fced15ff9d1a461f10979c3eae2eca8"
    access_token = "e6688922edb4a21f02b72977bb7889f1"
    shop = "ordersea.myshopify.com"
    scopes = "write_orders,read_customers"
    callback_uri = "http://www.orderplus.com/index.html"
    id = "3583116148816"
    shop_uri = "markepink.myshopify.com"
    products_api = ProductsApi(access_token=access_token, shop_uri=shop_uri)
    # print(products_api.get_all_collections())
    # a = [80778231853,80778199085,80776429613,80776855597,80778330157,80776462381,80776495149,80776593453,80778723373,80778395693,80776888365]
    # for i in [81154736173,80777314349,80776921133,80778002477,80778592301,80776986669,80777216045,80777674797,80777838637,80777379885,80777281581,80777510957,80777412653,80777609261,80778526765,80777478189,80777183277,80777445421,80777740333,80777805869,80778035245,80777052205,80776953901,80777347117,80777969709,80778756141]:
        # print(products_api.update_collection_by_id(i, "Hot Sale", '<div style="text-align: center;"><strong>🎁 Over $69 Get Extra 5% OFF (CODE: PUSH5)</strong></div>\n<div style="text-align: center;"><strong>🎁 Over $109 Get Extra 10% OFF (CODE: PUSH10)</strong></div>\n<div style="text-align: center;"><strong>🎁 Over $139 Get Extra 15% OFF (CODE: PUSH15)</strong></div>'))
    print(products_api.update_collection_seo_title(90986283098, "Hot Sale Test"))
    print(products_api.update_collection_seo_description(90986283098, "very nice"))
    # print(products_api.update_custom_collection_by_id(81154736173, 1, 1))
    # products_api.get_all_products(limit="250", since_id="1833170796589")
    # products_api.get_order(create_start_time="2019-05-22T0:0:0-04:00", create_end_time="2019-05-28T0:0:0-04:00", key_word="google", financial_status="paid")
    # products_api.get_shop_info()
    # products_api.get_product_id()
