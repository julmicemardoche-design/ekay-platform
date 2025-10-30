from setuptools import setup, find_packages

setup(
    name="ekay_platform",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'Flask==2.0.1',
        'Flask-SQLAlchemy==2.5.1',
        'Flask-Login==0.5.0',
        'Flask-WTF==0.15.1',
        'Flask-Migrate==3.1.0',
        'Werkzeug==2.0.1',
        'SQLAlchemy==1.4.23',
        'email-validator==1.1.3',
        'python-dotenv==0.19.0',
        'gunicorn==20.1.0',
        'Pillow==8.3.1',
        'WTForms==2.3.3'
    ],
)
