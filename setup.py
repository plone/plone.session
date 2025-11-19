from setuptools import setup


version = "5.0.0a1"
longdescription = open("README.rst").read()
longdescription += "\n"
longdescription += open("CHANGES.rst").read()

setup(
    name="plone.session",
    version=version,
    description="Session based auth tkt authentication for Zope",
    long_description=longdescription,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Plone :: Core",
        "Framework :: Plone",
        "Framework :: Plone :: 6.2",
        "Framework :: Zope :: 5",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python",
        "Topic :: System :: Systems Administration :: Authentication/Directory",  # noqa
    ],
    keywords="PAS session authentication Zope auth_tkt",
    author="Plone Foundation",
    author_email="plone-developers@lists.sourceforge.net",
    url="https://github.com/plone/plone.session/",
    license="BSD",
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.10",
    extras_require=dict(
        test=[
            "plone.app.testing",
            "zope.publisher",
        ]
    ),
    install_requires=[
        "plone.keyring",
        "plone.protect",
        "Products.GenericSetup",
        "Products.PluggableAuthService",
        "Zope",
    ],
)
