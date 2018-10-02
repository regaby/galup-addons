# -*- coding: utf-8 -*-
{
    'name': 'Pos Category Link',
    'author': 'GALUP Sistemas',
    'license': 'LGPL-3',
    'website': 'https://galup.com.ar',
    'version': '9.0.0.0.1',
    'category': 'Sales',
    'depends': [
        'base',
        'product',
        'point_of_sale',
    ],
    'summary': """
        This modules link product.category to pos.category
    """,
    'data': [
        'pos_category_view.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
