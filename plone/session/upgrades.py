# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName


def upgrade_1000_to_1001(context):
    # remove legacy registry, register in the new registry
    setup = getToolByName(context, 'portal_setup')
    setup.runAllImportStepsFromProfile('plone.session:remove-legacy-resources')
    setup.runAllImportStepsFromProfile('plone.session:default')
