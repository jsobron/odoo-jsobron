# -*- coding: utf-8 -*-
import json
import logging
import pprint
import werkzeug

from odoo import http
from odoo.http import request

class CreditGroupController(http.Controller):

    @http.route('/api/create_credit_group', type='json', auth='public', methods=['POST'])
    def create_credit_group(self,**post):
        response = {}
        try:
            input_data = json.loads(http.request.httprequest.data)
            credit_groups = input_data.get('grupo_creditos', [])
            for credit_group_data in credit_groups:

                name = credit_group_data.get('name')
                code = credit_group_data.get('codigo')
                channel_code = credit_group_data.get('canal')
                credit_limit = credit_group_data.get('credito_global')
                channel_id = self.env['custom.channels'].search(['name','=','channel_code'])
                ch_id = channel_id.id
                # Crear un nuevo grupo de crédito
                credit_group = self.env['credit.groups'].create({
                    'name': name,
                    'code': code,
                    'channel_id': ch_id,  # Asegúrate de que este campo sea correcto
                    'credit_limit': credit_limit,
                })
                response['status'] = 'success'
                response['message'] = 'Grupo de crédito(s) creado(s) con éxito'
        
        except Exception as e:
            response['status'] = 'error'
            response['message'] = str(e)

        return response