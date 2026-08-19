
import logging
_logger = logging.getLogger(__name__)

import requests
from odoo import http
from odoo.http import request
import json


class SolidWorksController(http.Controller):

    @http.route('/api/products', type='http', auth='public', methods=['GET'])
    def get_products(self, **kwargs):
        products = request.env['product.product'].sudo().search([], limit=10)
        data = []
        for p in products:
            data.append({
                "id": p.id,
                "name": p.name,
                "price": p.lst_price,
                "default_code": p.default_code
            })

        return data

    @http.route('/authorise_user', type='json', auth='bearer', methods=['POST'])
    def send_data(self, **kwargs):

        token = "8244a2edc9f460aafc243463320dfd3b48222efc"

        url = "http://localhost:8069/ak_solidworks/sync"

        post_data = {
            "name": "Demo ApI called HIT"
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": token
        }

        response = requests.post(url, json=post_data, headers=headers)
        return response.json()


    @http.route('/ak_solidworks/sync', type='jsonrpc', auth='bearer', methods=['POST'])
    def sync_cad_data(self, **kwargs):
        """
        SolidWorks Sync Endpoint - Odoo 19
        Uses API Token authentication (auth='bearer').
        """
        data = kwargs
        print('........custom API Called..................',data)

        _logger.info("\n\n\nSolidWorks Sync: Authenticated successfully as user %s", request.env.user.name)

        if not kwargs:
            return {'status': 'error', 'message': 'No data received in params'}
        else:
            return {'status': 'success', "msg": 'Run sucessfully'}

        # try:
        #     # Process Data
        #     result_product = request.env['solidworks.sync'].process_cad_data(kwargs)
        #
        #     return {
        #         'status': 'success',
        #         'product_id': result_product.id,
        #         'product_name': result_product.name,
        #         'default_code': result_product.default_code
        #     }
        # except Exception as e:
        #     _logger.error("SolidWorks Sync Error: %s", str(e))
        #     return {'status': 'error', 'message': str(e)}
