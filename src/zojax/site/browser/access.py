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
from zope.component import getUtility
from zope.security.proxy import removeSecurityProxy
from zope.securitypolicy.interfaces import Allow
from zope.securitypolicy.interfaces import IPrincipalPermissionManager
from zope.app.security.interfaces import IEveryoneGroup, IAuthenticatedGroup

from zojax.layoutform.subform import PageletEditSubForm
from zojax.statusmessage.interfaces import IStatusMessage
from zojax.site.interfaces import _


class SiteAccessSettings(PageletEditSubForm):

    weight = 0

    def extractData(self, setErrors=True):
        return {}, ()

    def update(self):
        self.everyone = getUtility(IEveryoneGroup).id
        self.authgroup = getUtility(IAuthenticatedGroup).id

        manager = IPrincipalPermissionManager(removeSecurityProxy(self.context))

        if 'site.access.save' in self.request:
            val = self.request.get('site.access', None)
            if val == 'open':
                manager.grantPermissionToPrincipal(
                    'zojax.AccessSite', self.everyone)
                manager.unsetPermissionForPrincipal(
                    'zojax.AccessSite', self.authgroup)

            if val == 'private':
                manager.grantPermissionToPrincipal(
                    'zojax.AccessSite', self.authgroup)
                manager.unsetPermissionForPrincipal(
                    'zojax.AccessSite', self.everyone)

            IStatusMessage(self.request).add(
                _('Site access settings has been changed.'))

        self.everyoneAllowed = manager.getSetting(
            'zojax.AccessSite', self.everyone) is Allow

        self.authgroupAllowed = manager.getSetting(
            'zojax.AccessSite', self.authgroup) is Allow

    def isAvailable(self):
        return True

    def postUpdate(self):
        pass
