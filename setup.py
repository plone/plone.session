from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='plone.session',
      version=version,
      description="Session based authentication for Zope",
      long_description="""\
Session based authentication for the Zope Pluggable Authentication Services.""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Zope2",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
	"Topic :: System :: Systems Administration :: Authentication/Directory",
        ],
      keywords='PAS session authentication Zope',
      author='Wichert Akkerman',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://svn.plone.org/svn/plone/plone.session',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
