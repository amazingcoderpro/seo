## 1. 服务器启动

```
MYSQL_HOST= MYSQL_PASSWD= python3 manage.py runserver 0.0.0.0:8000
```





## 1. 数据库创建数据
```
INSERT INTO `user` (`id`, `last_login`, `is_superuser`, `first_name`, `last_name`, `is_staff`, `is_active`, `date_joined`, `username`, `email`, `password`, `code`, `create_time`, `update_time`)
VALUES
	(1, NULL, 0, 'Tiptopfree', 'SEO', 0, 1, '2019-06-13 19:59:20.841303', 'tiptopfree.myshopify.com', 'service@tiptopfree.com', 'pbkdf2_sha256$120000$80m7eexzlrOI$VECOj4WpfkgCHLTFqQhibZY7dW2L1be7VRG0vBDKvws=', 'pOmaa0', '2019-06-13 19:59:20.856436', '2019-06-17 17:18:35.669399');

INSERT INTO `store` (`id`, `name`, `url`, `email`, `create_time`, `update_time`,  `user_id`)
VALUES
	(1, 'tiptopfree', 'www.tiptopfree.com', 'service@tiptopfree.com', '2019-06-13 19:59:20.413463', '2019-06-14 15:14:27.352727',1);

```

## 2. 测试店铺授权

```
https://tiptopfree.myshopify.com/admin/oauth/authorize?client_id=7fced15ff9d1a461f10979c3eae2eca8&scope=read_content,write_content,read_themes,write_themes,read_products,write_products,read_product_listings,read_customers,write_customers,read_orders,write_orders,read_shipping,write_draft_orders,read_inventory,write_inventory,read_shopify_payments_payouts,read_draft_orders,read_locations,read_script_tags,write_script_tags,read_fulfillments,write_shipping,read_analytics,read_checkouts,write_resource_feedbacks,write_checkouts,read_reports,write_reports,read_price_rules,write_price_rules,read_marketing_events,write_marketing_events,read_resource_feedbacks,read_shopify_payments_disputes,write_fulfillments&redirect_uri=https%3A//pinbooster.seamarketings.com/api/v1/auth/shopify/callback/&state=chicgostyle&grant_options[]=

Tiptopfree Shopify后台:登录网址：https://tiptopfree.myshopify.com/admin
登录邮箱：alicia.wang@orderplus.com
登录密码：%￥^&561

