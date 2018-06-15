# -*- coding: utf-8 -*-

{
    "name": "Attendance Terminal",
    "version": "1.0",
    "author": "Galup Sistemas",
    "category": "Custom",
    "website": "galup.com.ar",
    "description": "A Module for Time Attendance Terminal",
    "depends": [
        "base",
        "hr_attendance",
    ],
    "init_xml": [
    ],
    "data": [
        'security/ir.model.access.csv',
        'security/hr_attendance_security.xml',
        'views/attendance_terminal_view.xml',
        'views/hr_attendance_view_view.xml',
        # 'views/attendance_template.xml',
        'wizard/load_attendance_wizard_view.xml',
    ],
    "active": False,
    "installable": True
}
