# -*- coding: utf-8 -*-
{
    'name': 'Product Cost History',
    'author': 'GALUP Sistemas',
    'license': 'LGPL-3',
    'website': 'https://galup.com.ar',
    'version': '9.0.0.0.1',
    'category': 'Sales',
    'depends': [
        'base',
        'product',
        'purchase',
    ],
    'summary': """
        Product cost history
    """,
    'data': [
        'views/product_view.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
