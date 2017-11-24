# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2017 Soltic S.R.L 
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
    "name": "Sig IVA",
    "version": "1.0",
    "author": "GALUP Sistemas",
    "category": "Account",
    "description": """
        Sistema IVA AFIP
    """,
    "license": "AGPL-3",
    "depends": ['account','report_aeroo'],
    "data": [
        # view
        'view/menu_view.xml',
        'view/sigvat_payroll_view.xml',
        'view/sigvat_payroll_line_view.xml',
        'view/sigvat_payroll_category_view.xml',
        'view/sigvat_payroll_concept_view.xml',
        'view/sigvat_payroll_concept_type_view.xml',
        'view/res_partner_view.xml',
        'view/res_currency_view.xml',
        'view/account_tax_view.xml',
        'view/sigvat_journal_view.xml',
        'view/sigvat_voucher_type_view.xml',
        'view/sigvat_journal_purchase_line_view.xml',
        'view/sigvat_journal_sale_line_view.xml',
        # wizard
        'wizard/sigvat_reginfo_cv_view.xml',
        'wizard/libro_sueldo_view.xml',
        # Data
        'data/sigvat_data.xml',
        # Security
        'security/sigvat_security.xml',
        'security/ir.model.access.csv',
        # Report
        'report/payroll_report.xml',
        'report/libro_iva_report.xml',
        'report/libro_sueldo_report.xml',
    ],
    "installable": True,
    "active": False,
}
