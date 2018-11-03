# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    All Rights Reserved.
#
############################################################################
#
############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name": "Account print invoice",
    "version": "1.0",
    "author": "GALUP Sistemas",
    "description": """
        Este módulo modifica la vista de factura, para habilitar la impresión de factura en estado pagado
    """,
    "license": "AGPL-3",
    "depends": ['account'],
    "data": [
        'views/account_invoice_view.xml',
    ],
    'qweb': [],
    "installable": True,
    "active": False,
}
