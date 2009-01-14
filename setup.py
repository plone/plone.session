from setuptools import setup, find_packages

version = '2.1'

setup(name='plone.session',
      version=version,
      description="Session based authentication for Zope",
      long_description=open("README.txt").read() + open("docs/HISTORY.txt").read(),
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        "Topic :: System :: Systems Administration :: Authentication/Directory",
        ],
      keywords='PAS session authentication Zope',
      author='Wichert Akkerman - Plone Foundation',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://svn.plone.org/svn/plone/plone.session',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone'],
      include_package_data=True,
      zip_safe=False,
      download_url='http://code.google.com/p/plone/downloads/list',
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
        # 'DateTime',
        # 'Zope2',
      ],
      )
