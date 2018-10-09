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
    "name": "Galup Hotel",
    "version": "1.0",
    "author": "GALUP Sistemas",
    "description": """
        Galup Hotel
    """,
    "license": "AGPL-3",
    "depends": ['hotel','hotel_reservation','hr','account_tax_python', 'partner_identification','report_aeroo','auditlog','amount_to_text_es'],
    "data": [
        'security/ir.model.access.csv',
        'security/ir_ui_menu_view.xml',
        'view/res_partner_view.xml',
        'view/hotel_folio_view.xml',
        'view/hotel_reservation_view.xml',
        'view/hotel_discount_view.xml',
        'view/hotel_room_view.xml',
        'view/account_tax_view.xml',
        'view/hotel_room_state_view_view.xml',
        'view/quick_room_blocked_view.xml',
        'view/quick_reservation_view.xml',
        'view/quick_folio_view.xml',
        'view/account_invoice_view.xml',
        'wizard/room_issue_wizard_view.xml',
        'wizard/check_reservation_view.xml',
        'wizard/make_invoice_wizard.xml',
        'data/discount_data.xml',
        'data/floor_data.xml',
        'data/room_type_data.xml',
        'data/room_data.xml',
        'data/account_tax_data.xml',
        # 'data/state_data.xml',
        'data/service_data.xml',
        # 'reports/report_folio_view.xml',
        'reports/report_folio_template.xml',
        'views.xml',
        'reports/registro_huesped_report.xml',
        'reports/recibo_x_report.xml',

    ],
    'qweb': ['static/src/xml/base.xml'],
    "installable": True,
    "active": False,
}
