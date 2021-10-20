# -*- coding: utf-8 -*-
from odoo import http

# class ProductSpecs(http.Controller):
#     @http.route('/product_specs/product_specs/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/product_specs/product_specs/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('product_specs.listing', {
#             'root': '/product_specs/product_specs',
#             'objects': http.request.env['product_specs.product_specs'].search([]),
#         })

#     @http.route('/product_specs/product_specs/objects/<model("product_specs.product_specs"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('product_specs.object', {
#             'object': obj
#         })