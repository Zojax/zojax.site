##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""

$Id$
"""
from zope import component, interface
from zope.publisher.browser import TestRequest
from zope.security.proxy import removeSecurityProxy
from zope.security.management import queryInteraction
from zope.app.component.hooks import getSite, setSite
from z3c.configurator import configure, ConfigurationPluginBase

from zojax.portlet.interfaces import ENABLED, IPortletManager
from zojax.controlpanel.interfaces import IConfiglet
from zope.securitypolicy.interfaces import IRolePermissionManager
from zope.securitypolicy.interfaces import IPrincipalPermissionManager
from zope.app.security.interfaces import IEveryoneGroup, IAuthenticatedGroup
from zope.securitypolicy.interfaces import Allow

from interfaces import ISite


def reconfigureSite(app, *args):
    site = removeSecurityProxy(app)
    configure(site, {})


class BasicSiteConfiguration(ConfigurationPluginBase):
    component.adapts(ISite)

    def __call__(self, data):
        portal = self.context


class SkinConfiguration(ConfigurationPluginBase):
    component.adapts(ISite)

    dependencies = ('basic',)

    def __call__(self, data):
        portal = self.context

        site = getSite()
        setSite(portal)

        request = None
        interaction = queryInteraction()
        if interaction is not None:
            for participation in interaction.participations:
                request = participation
                break

        if request is None:
            request = TestRequest()

        sm = portal.getSiteManager()

        # setup default skin
        skintool = sm.queryUtility(IConfiglet, 'ui.portalskin')
        skintool.skin = u'zojax'

        interface.directlyProvides(request, *skintool.generate())

        # setup portlets
        portlets = sm.queryMultiAdapter(
            (portal, request, None), IPortletManager, 'columns.left')
        portlets.status = ENABLED
        portlets.__data__['portletIds'] = ('portlet.login', 'portlet.actions')

         # set portal access to open
        manager = IPrincipalPermissionManager(portal)
        everyone = sm.queryUtility(IEveryoneGroup)
        if everyone is not None:
            manager.grantPermissionToPrincipal(
                'zojax.AccessSite', everyone.id)

        authenticated = sm.queryUtility(IAuthenticatedGroup)
        if authenticated is not None:
            manager.unsetPermissionForPrincipal(
                'zojax.AccessSite', authenticated.id)

        # install catalog
        #sm.getUtility(IConfiglet, 'system.catalog').install()

        setSite(site)
