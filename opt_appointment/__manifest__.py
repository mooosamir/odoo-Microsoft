{
    'name': 'OPT Appointment',
    'category': 'General',
    'summary': 'Appointment Booking',
    'description': """Appointment Booking""",
    'author': 'Serpent Consulting Service Pvt. Ltd.',
    'website': 'www.serpentcs.com',
    'version': '1.0.0',
    'depends': ['base', 'opt_insurance', 'opt_custom', 'calendar', 'char_datetime_widget'],
    'data': [
        'security/ir.model.access.csv',
        'security/security_rules.xml',

        'views/assets.xml',
        'views/calendar_event.xml',
        # 'views/appointment_view.xml',
        'views/appointments_hours.xml',
        'views/schedule_appointment.xml',
        'views/appointments_holidays.xml',

        'wizard/appointment_schedule_report_view.xml',

        'report/report_appointment_view.xml',
        'report/report_view.xml',
    ],
    'qweb': [
        # "static/src/xml/SearchView.xml",
        'static/src/xml/appointment_book.xml',
    ],
    'installable': True,
}
