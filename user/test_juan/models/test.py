from odoo import _, api, fields, models, exceptions
from odoo.exceptions import UserError, AccessError, ValidationError


# Agregamos nueva clase
class SaleChannel(models.Model):
    _name = 'custom.sale.channels'
    _description = 'Canales de Venta'

    name = fields.Char(string='Nombre', required=True,track_visibility=False)   #Nombre obligatorio
    code = fields.Char(string='Código', readonly=True)   #Codigo
    warehouse_id = fields.Many2one('stock.warehouse', string='Depósito') #Almacen donde se guarda la mercaderia
    journal_id = fields.Many2one('account.journal', string='Diario de Factura') #Diario de venta
    message_ids = fields.One2many('mail.message', 'res_id', domain=[('model', '=', 'custom.sale.channels')],
        string='Mensajes', help='Comunicaciones relacionadas con este canal de venta.', readonly = True)
    
    create_uid = fields.Many2one('res.users', 'Creado por', readonly=True, copy=False)
    create_date = fields.Datetime('Fecha de creación', readonly=True, copy=False)
    write_uid = fields.Many2one('res.users', 'Modificado por', readonly=True, copy=False)
    write_date = fields.Datetime('Fecha de modificación', readonly=True, copy=False)

    @api.model
    def create(self, vals):
        if not vals.get('code'):
            vals['code'] = 'CH' + str(self.env['ir.sequence'].next_by_code('channel.sequence'))
        return super(SaleChannel,self).create(vals)

    def write(self,vals):
        # Obtén el usuario actual que realiza el cambio
        #import pdb; pdb.set_trace()
        old_name = self.name
        if vals.get('name'):
            current_user = self.env.user
            new_name = vals.get('name')
            res = super(SaleChannel, self).write(vals)
            if res:
                message = self.env['mail.message'].create({
                'subject': 'Campo Nombre modificado',
                'body': f'El campo Name ha sido modificado de {old_name} a {new_name} por {current_user.name} el {fields.Datetime.now()}',
                'model': 'custom.sale.channels',
                'res_id': self.id,
                'message_type': 'comment',
            })
            return res
        else: 
            return super(SaleChannel,self).write(vals)
        


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    channel_id = fields.Many2one('custom.sale.channels',string='Canal de Venta',required = True) #Campo relacion con los canales de venta. OBLIGATORIO
    journal_id = fields.Many2one('account.journal', string='Diario de Factura', readonly = True) #Diario de venta

    # #Punto 4 Selections
    # credit_status = fields.Selection([
    #     ('no_credit_limit', 'Sin límite de crédito'),
    #     ('credit_available', 'Crédito Disponible'),
    #     ('credit_blocked', 'Crédito Bloqueado'),
    # ], string='Crédito', compute='_compute_credit_status', store=True)



    # def _compute_credit_status(self):
    #     import pdb; pdb.set_trace()
    #     #Buscar el credit de partner
    #     #Buscar el canal de venta del canal del partner

    #     for order in self:
    #         if order.credit_status != 'no_credit_limit':
    #             if order.partner_id and order.channel_id:
    #                 # Buscar el grupo de crédito para el cliente y canal de venta
    #                 credit_group = self.env['credit.groups'].search([
    #                     ('channel_id','=', order.channel_id.id),
    #                     ],limit=1)
                    


    @api.model
    def create(self,vals):
        order = super(SaleOrder, self).create(vals)
        #Busco canal de venta
        channel_id = self.env['custom.sale.channels'].browse(vals['channel_id'])
        # Actualizo partner_shipping
        order.partner_shipping_id = channel_id.warehouse_id.partner_id
        order.journal_id = channel_id.journal_id
        return order


    @api.model
    def write(self, vals):
        #import pdb; pdb.set_trace()
        res = super(SaleOrder, self).write(vals)
        if vals.get('channel_id'):
            self.partner_shipping_id = self.channel_id.warehouse_id.partner_id
            self.journal_id = self.channel_id.journal_id.id

    def _create_invoices(self):
        #import pdb; pdb.set_trace()
        invoice_vals = super(SaleOrder, self).create_invoices()
        if self.channel_id:
            invoice_vals['journal_id'] = self.channel_id.journal_id.id
        return invoice_vals
    


#Grupos de credito   

class CreditGroup(models.Model):
    _name = 'credit.groups'
    _description = 'Grupos de credito'

    name = fields.Char(string='Nombre', required=True) #Nombre 
    code = fields.Char(string='Código', required=True) 
    channel_id = fields.Many2one('custom.sale.channels', string='Canal de Venta', required=True) #Canal de venta
    credit_limit = fields.Float(string='Credito global', required=True)
    #Campso computados
    credit_used = fields.Float(string='Credito utilizado', readonly=True, compute='_compute_credit_used') 
    credit_available = fields.Float(string='Credito disponible', readonly=True, compute='_compute_credit_available')

    @api.model
    def create(self, vals):
        #import pdb; pdb.set_trace()
        if vals.get('code').find('026') >= 0 :  #Restriccion 026
            raise ValidationError( 'El código del grupo no puede contener la secuencia "026"')
        
        return super(CreditGroup,self).create(vals)
    

    def _compute_credit_used(self):
        #import pdb; pdb.set_trace()
        for group in self : 
            total_credit_used = 0
            #Buscamos las sale_orders en estado sale y no facturadas.
            sale_orders = self.env['sale.order'].search([('channel_id','=',group.channel_id.id),('state','=','sale'),('invoice_status', '!=', 'invoiced'),]) 
            for order in sale_orders:
                total_credit_used += order.amount_total

            group.credit_used = total_credit_used
    
    def _compute_credit_available(self):
        """Calculo el crédito disponible"""
        for group in self: 
            group.credit_available = group.credit_limit - group.credit_used


#4 

class ResPartner(models.Model):
    _inherit = 'res.partner' #Heredo res_partner

    #Nuevos campos
    has_credit = fields.Boolean(string='Tiene control de credito?') #Booleano para saber si tiene contro de credito
    credit_groups = fields.Many2many('credit.groups',string='Grupos de Credito') #Many2many, recibe mas de un grupo de credito



#Reporte

class CreditReport(models.Model):
    _name = 'credit.report'
    _description = 'Reporte de creditos'


    name = fields.Char(string='Nombre')
    code = fields.Char(string='Código')
    channel_id = fields.Many2one('custom.sale.channels', string='Canal de Venta')
    customers = fields.One2many('res.partner', 'credit_groups', string='Clientes Asociados')


    @api.model
    def _get_report_values(self, docids, data=None):
        # Obtén los datos para el informe
        credit_groups = self.env['credit.groups'].search([])
        report_data = []
        for group in credit_groups:
            group_data = {
                'name': group.name,
                'code': group.code,
                'channel_id': group.channel_id.name,
                'customers': [],
            }
            for customer in group.customer_ids:
                customer_data = {
                    'name': customer.name,
                    'doc_number': customer.doc_number,
                    'phone': customer.phone,
                    'email': customer.email,
                }
                group_data['customers'].append(customer_data)
            report_data.append(group_data)
        return {'report_data': report_data}