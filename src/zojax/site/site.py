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
from zope import interface, component, event
from zope.app.component import interfaces
from zope.app.component.site import LocalSiteManager
from zope.component.interfaces import IComponentLookup
from zope.security.proxy import removeSecurityProxy
from zope.copypastemove.interfaces import IObjectCopier
from zope.app.container.interfaces import IObjectAddedEvent
from zojax.content.space.content import ContentSpace

from interfaces import ISite
from config import reconfigureSite

from zojax.content.type.constraints import checkObject
from zope.lifecycleevent import ObjectCopiedEvent
from zope.app.container.interfaces import INameChooser
from zc.copy import copy
from zope.interface import Invalid


class Site(ContentSpace):
    interface.implements(ISite)

    showTabs = True
    showHeader = False
    workspaces = ('overview',)

    _sm = None

    def getSiteManager(self):
        return self._sm

    def setSiteManager(self, sm):
        #if interfaces.ISite.providedBy(self):
        #    raise TypeError("Already a site")

        if IComponentLookup.providedBy(sm):
            self._sm = sm
            sm.__name__ = '++etc++site'
            sm.__parent__ = self
        else:
            raise ValueError('setSiteManager requires an IComponentLookup')

        interface.directlyProvides(
            self, interface.directlyProvidedBy(self), interfaces.ISite)

        event.notify(interfaces.NewLocalSite(sm))


@component.adapter(ISite, IObjectAddedEvent)
def siteAddedHandler(site, event):
    site = removeSecurityProxy(site)
    site.setSiteManager(LocalSiteManager(site))
    reconfigureSite(site)


class SiteCopier(object):
    component.adapts(ISite)
    interface.implements(IObjectCopier)

    def __init__(self, object):
        self.context = object

    def copyTo(self, target, new_name=None):
        obj = self.context
        container = obj.__parent__

        orig_name = obj.__name__
        if new_name is None:
            new_name = orig_name

        checkObject(target, new_name, obj)

        chooser = INameChooser(target)
        new_name = chooser.chooseName(new_name, obj)

        new = copy(obj)
        event.notify(ObjectCopiedEvent(new, obj))

        target[new_name] = new
        new._sm = copy(obj._sm)
        return new_name

    def copyable(self):
        return True

    def copyableTo(self, target, name=None):
        if name is None:
            name = self.context.__name__

        try:
            checkObject(target, name, self.context)
        except Invalid:
            return False

        return True
