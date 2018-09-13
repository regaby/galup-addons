# -*- coding: utf-8 -*-

{
    "name": "Account register payments extension",
    "version": "1.0",
    "author": "Galup Sistemas",
    "category": "Custom",
    "website": "galup.com.ar",
    "description": "Este modulo agrega al wizard account.register.payment la relación con cheque",
    "depends": [
        "base",
        "account",
        "account_check",
    ],
    "init_xml": [
    ],
    "data": [
        "views/account_register_payments_view.xml",
    ],
    "active": False,
    "installable": True
}

