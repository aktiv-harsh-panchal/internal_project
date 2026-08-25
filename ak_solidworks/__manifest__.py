{
    'name': 'SolidWorks CAD Integration',
    'version': '19.0.1.0.0',
    'summary': 'Collect data from SolidWorks CAD Server via JSON',
    'description': """
        Features:
        - JSON Controller for CAD Server data push.
        - Automatic Product/BOM creation.
        - Recursive Multi-level BOM support.
        - Automatic Versioning via DateTime Reference.
    """,
    'author': 'Your Consultant',
    'category': 'Manufacturing/Manufacturing',
    'depends': ['product', 'mrp'],
    'data': [
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
