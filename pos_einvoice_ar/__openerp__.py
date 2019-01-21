# -*- coding: utf-8 -*-
{
    'name': 'POS einvoice AR',
    'version': '0.1',
    'author': 'Galup Sistemas',
    'license': 'LGPL-3',
    'category': 'Point Of Sale',
    'website': 'www.galup.com.ar',
    'depends': ['point_of_sale'],
    'data': [
        'views/pos_einvoice_ar.xml',
    ],
    'qweb': [
        'static/src/xml/pos_payment.xml',
    ],
    'installable': True,
}
