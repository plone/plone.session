from setuptools import setup, find_packages

version = '3.0b5'

setup(name='plone.session',
      version=version,
      description="Session based authentication for Zope",
      long_description=open("README.txt").read() + '\n' + open("CHANGES.txt").read(),
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Topic :: System :: Systems Administration :: Authentication/Directory",
        ],
      keywords='PAS session authentication Zope',
      author='Wichert Akkerman, Laurence Rowe - Plone Foundation',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://pypi.python.org/pypi/plone.session',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone'],
      include_package_data=True,
      zip_safe=False,
      extras_require=dict(
        test=[
            'zope.configuration',
            'zope.publisher',
            'Products.PloneTestCase',
        ]
      ),
      install_requires=[
        'setuptools',
        'plone.keyring',
        'plone.protect',
        'zope.component',
        'zope.interface',
        'Products.PluggableAuthService',
        'Zope2',
      ],
      )
