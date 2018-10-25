
from openerp import fields, models, exceptions, api, _
import base64
import csv
import cStringIO
import urllib2
from openerp.exceptions import UserError, AccessError


class ImportProduct(models.TransientModel):
    _name = 'import.product'
    _description = 'import.product'

    def get_reader_info(self):
        if not self.data:
            raise exceptions.Warning(_("You need to select a file!"))
        # Decode the file data
        data = base64.b64decode(self.data)
        file_input = cStringIO.StringIO(data)
        file_input.seek(0)
        # location = self.location
        reader_info = []
        if self.delimeter:
            delimeter = str(self.delimeter)
        else:
            delimeter = ','
        reader = csv.reader(file_input, delimiter=delimeter,
                            lineterminator='\r\n')
        try:
            reader_info.extend(reader)
        except Exception:
            raise exceptions.Warning(_("Not a valid file!"))
        keys = reader_info[0]
        # check if keys exist
        if not isinstance(keys, list) or ('nombre' not in keys or
                                          'codigo' not in keys):
            raise exceptions.Warning(
                _("Not 'name' or 'code' keys found"))
        del reader_info[0]
        return keys, reader_info

    def _default_stock_location(self):
        warehouse = self.env['ir.model.data'].get_object('stock', 'warehouse0')
        return warehouse.lot_stock_id.id

    data = fields.Binary('File', required=True)
    name = fields.Char('Filename')
    delimeter = fields.Char('Delimeter', default=',',
                            help='Default delimeter is ","')
    model = fields.Selection( string="Model" ,selection=[('product','Product'),('category','Product Category')], default='product', required=True)
    action = fields.Selection( string="Action" ,selection=[('create','Create'),('update','Update')], default='create', required=True)
    stock = fields.Selection( string="Stock" ,selection=[('add','Add Current Stock'),('update','Update Qty on hand')], default='add', required=True)
    location = fields.Many2one('stock.location', 'Default Location', required=True, default=_default_stock_location)
    new_code = fields.Boolean('nuevo_codigo',default=False)
    standard_price = fields.Boolean('precio_costo',default=True)
    list_price = fields.Boolean('precio_lista',default=True)
    quantity = fields.Boolean('cantidad',default=True)
    category = fields.Boolean('categoria',default=False)
    imagen = fields.Boolean('imagen',default=False)

    @api.one
    def action_import(self):
        if self.model=='product' and self.action=='create':
            self.create_product()
        if self.model=='product' and self.action=='update':
            self.update_product()
        if self.model=='category':
            1/0
        return True

    @api.one
    def update_product(self):
        """Load Inventory data from the CSV file."""
        ctx = self._context
        stloc_obj = self.env['stock.location']
        inventory_obj = self.env['stock.inventory']
        # inv_imporline_obj = self.env['stock.inventory.import.line']
        product_obj = self.env['product.product']
        prodcat_obj = self.env['product.category']
        # if 'active_id' in ctx:
        #     inventory = inventory_obj.browse(ctx['active_id'])

        keys, reader_info = self.get_reader_info()

        values = {}

        for i in range(len(reader_info)):
            val = {}
            field = reader_info[i]
            values = dict(zip(keys, field))
            prod_category = False

            if self.standard_price:
                val['standard_price'] = values['precio_costo']
            if self.list_price:
                val['list_price'] = values['precio_lista']
            if self.category:
                if 'categoria' in values and values['categoria']:
                    locat_lst = prodcat_obj.search([('name', '=',
                                                   values['categoria'])])
                    if locat_lst:
                        prod_category = locat_lst[0]
                    else:
                        prod_category = prodcat_obj.create({'name':values['categoria']})
                val['categ_id'] = prod_category and prod_category.id
            if self.imagen:
                val['image_medium'] = False
                val['image'] = False

            prod_lst = product_obj.search([('default_code', '=',
                                            values['codigo'])])
            if prod_lst:
                prod_id = prod_lst[0].id
            else:
                raise UserError(_('Product not found with code %s.'%values['codigo']))
            product = product_obj.browse(prod_id)
            product.write(val)
        if self.quantity:
            keys.append(self.stock)
            self.change_product_qty(reader_info,keys)
        if self.imagen:
            self.import_image(reader_info,keys)


    @api.one
    def create_product(self):
        """Load Inventory data from the CSV file."""
        ctx = self._context
        stloc_obj = self.env['stock.location']
        inventory_obj = self.env['stock.inventory']
        # inv_imporline_obj = self.env['stock.inventory.import.line']
        product_obj = self.env['product.product']
        prodcat_obj = self.env['product.category']
        # if 'active_id' in ctx:
        #     inventory = inventory_obj.browse(ctx['active_id'])

        keys, reader_info = self.get_reader_info()

        values = {}
        # actual_date = fields.Date.today()
        # inv_name = self.name + ' - ' + actual_date
        # inventory.write({'name': inv_name,
        #                  'date': fields.Datetime.now(),
        #                  'imported': True, 'state': 'confirm'})
        for i in range(len(reader_info)):
            val = {}
            field = reader_info[i]
            values = dict(zip(keys, field))

            prod_category = False

            if 'categoria' in values and values['categoria']:
                locat_lst = prodcat_obj.search([('name', '=',
                                               values['categoria'])])
                if locat_lst:
                    prod_category = locat_lst[0]
                else:
                    prod_category = prodcat_obj.create({'name':values['categoria']})

            # prod_lst = product_obj.search([('default_code', '=',
            #                                 values['code'])])
            # if prod_lst:
            #     val['product'] = prod_lst[0].id
            # if 'lot' in values and values['lot']:
            #     val['lot'] = values['lot']

            val['name'] = values['nombre']
            print values['nombre']
            val['default_code'] = values['codigo']
            val['standard_price'] = values['precio_costo']
            val['list_price'] = values['precio_lista']
            val['sale_ok'] = True
            val['categ_id'] = prod_category and prod_category.id
            val['type'] = 'product'
            product_obj.create(val)
        if len(values['cantidad']) > 0:
            self.change_product_qty(reader_info,keys)
        self.import_image(reader_info,keys)

    @api.one
    def change_product_qty(self, reader_info,keys):
        """ Changes the Product Quantity by making a Physical Inventory. """
        inventory_obj = self.env['stock.inventory']
        inventory_line_obj = self.env['stock.inventory.line']
        product_obj = self.env['product.product']

        # for data in self.browse(cr, uid, ids, context=context):
        #     if data.new_quantity < 0:
        #         raise UserError(_('Quantity cannot be negative.'))
        #     ctx = context.copy()
        #     ctx['location'] = data.location_id.id
        #     ctx['lot_id'] = data.lot_id.id

        actual_date = fields.Date.today()
        # inv_name = self.name + ' - ' + actual_date
        # inventory.write({'name': inv_name,
        #                  'date': fields.Datetime.now(),
        #                  'imported': True, 'state': 'confirm'})
        inventory_id = inventory_obj.create({
            'name': self.name + ' - ' + actual_date,
            'date': fields.Datetime.now(),
            'filter': 'file',
            'location_id': self.location.id})
        for i in range(len(reader_info)):
            val = {}
            field = reader_info[i]
            values = dict(zip(keys, field))

            prod_lst = product_obj.search([('default_code', '=',
                                            values['codigo'])])
            if prod_lst:
                val['product'] = prod_lst[0].id
                val['uom_id'] = prod_lst[0].uom_id.id
                val['qty_available'] = prod_lst[0].qty_available

            # product = data.product_id.with_context(location=data.location_id.id, lot_id= data.lot_id.id)
            # th_qty = product.qty_available
            if 'add' in keys:
                qty = prod_lst[0].qty_available + float(values['cantidad'])
            else:
                qty = values['cantidad']
            line_data = {
                'inventory_id': inventory_id.id,
                'product_qty': qty,
                'location_id': self.location.id,
                'product_id': val['product'],
                'product_uom_id': val['uom_id'],
                'theoretical_qty': qty,
                # 'prod_lot_id': data.lot_id.id
            }
            inventory_line_obj.create(line_data)
        # inventory_obj.action_done([inventory_id])
        inventory_id.action_done()
        return {}

    def import_image(self, reader_info, keys):
        # prod_obj = conn.get_model('product.product')
        # imd_obj = conn.get_model('ir.model.data')
        prod_obj = self.env['product.product']

        row_count = 0

        #         # loop over csv rows
        # for row in reader:
        for i in range(len(reader_info)):
            val = {}
            field = reader_info[i]
            values = dict(zip(keys, field))

            row_count += 1

            prod_lst = prod_obj.search([('default_code', '=',
                                            values['codigo'])])
            if prod_lst:
                prod_id = prod_lst[0].id

            prod_path = values['imagen']
            if not prod_path:
                continue

            try:
                prod_path = urllib2.quote(bytes(prod_path.replace('\\', '/').encode('utf-8')), safe=":/'")
            except UnicodeEncodeError as e:
                print row_count
                print 'URL encoding error for string: %s' % prod_path
                print 'Original path: %s' % prod_path
                print unicode(e)
                print ''

            # get image and convert to base64
            try:
                image = None

                if prod_path[0:4] == 'http':
                    response = urllib2.urlopen(prod_path)
                    image = response.read()
                    response.close()
                else:
                    image_file = open(prod_path)
                    image = image_file.read()
                    image_file.close()

                image_base64 = base64.encodestring(image)
            except urllib2.URLError as e:
                print row_count
                print 'could not get image %s: %s' % (prod_path, unicode(e))
                print ''
                continue

            # write to openerp
            try:
                product = prod_obj.browse(prod_id)
                product.write({'image': image_base64})
                # done_file.write('%s\n' % prod_xml_id)
                print 'updated img for prod id: %s' % (prod_id)
            except Exception, e:
                print row_count
                print 'rpc error while uploading: %s' % unicode(e)
                print ''

        # close csv file
        print 'finished uploading %s product images' % row_count

            # close done file
