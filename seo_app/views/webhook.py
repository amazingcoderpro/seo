import datetime, json
import re

from rest_framework.response import Response
from rest_framework.views import APIView

from sdk.shopify.get_shopify_products import ProductsApi
from seo_app import models


class EventProductCreate(APIView):

    def post(self, request, *args, **kwargs):
        print("------------ order paid ------------:")
        print(json.dumps(request.data))
        store = models.Store.objects.filter(url=request.META["HTTP_X_SHOPIFY_SHOP_DOMAIN"]).first()
        if not store:
            return Response({"code": 200})
        pro = request.data
        uuid = str(pro.get("id", ""))
        sku = pro.get("handle", "")
        title = pro.get("title", "")
        domain = "https://{}/products/{}".format(store.url, sku)
        type = pro.get("product_type", "")
        variants = pro.get("variants", [])
        price = store.money_format + variants[0].get("price", "") if variants else 0
        time_now = datetime.datetime.now()

        # description
        p = re.compile(r"\s+")
        dr = re.compile(r'<[^>]+>', re.S)
        body_html = pro.get("body_html")
        dd = dr.sub('', str(body_html))
        description = ' '.join(p.split(dd.strip().replace("\n", " "))).strip()

        variants_price_str = store.money_format
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
            variants_str = " ".join(variants_list)
        curent_time = datetime.datetime.now()
        event_peoduct = models.Product.objects.create(
            thumbnail="",
            sku=sku,
            description=description,
            variants=variants,
            price=price,
            type=type,
            domain=domain,
            title=title,
            create_time=curent_time,
            update_time=curent_time,
            store_id=store.id,
            uuid=uuid,
            state=0
        )
        exit_product = models.Product.objects.filter(store=store).first()
        remark_title = exit_product.remark_title
        remark_description = exit_product.remark_description
        # id, domain, price, uuid, type, title, remark_title, remark_description, variants, description
        url = domain.split("//")[1].split(".")[0] + ".com"
        remark_dict = {"%Product Type%": type, "%Product Title%": title, "%Variants%": variants,
                       "%Product Price%": price, "%Product Description%": description, "%Domain%": url.capitalize()}
        for row in remark_dict:
            remark_title = remark_title.replace(row, remark_dict[row])
            remark_description = remark_description.replace(row, remark_dict[row])
        result = ProductsApi(store.token, store.url).motify_product_meta(uuid, remark_title, remark_description)

        if result["code"] == 1:
            event_peoduct.meta_title =  remark_title
            exit_product.meta_description = remark_description
            exit_product.state = 2

        else:
            exit_product.error_text = result["data"]
            exit_product.state = 3
        exit_product.save()
        return Response({"code": 200})


class EventProductUpdate(APIView):
    def post(self, request, *args, **kwargs):
        print("------------ Customer Create ------------:")
        # print(request.META, type(request.META))
        print(json.dumps(request.data))
        return Response({"code": 200})


