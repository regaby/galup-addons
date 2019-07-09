# -*- coding: utf-8 -*-

{
    "name": "POS Cash Flow Report",
    "version": "1.0",
    "author": "Galup Sistemas",
    "category": "Point of Sale",
    "website": "galup.com.ar",
    "description": "Report of POS cash flow movements and balance",
    "depends": [
        "base",
        "point_of_sale",
    ],
    "init_xml": [
    ],
    "data": [
        'wizard/cash_flow_wizard_view.xml',
        'report/cash_flow_report.xml',

    ],
    "active": False,
    "installable": True
}
