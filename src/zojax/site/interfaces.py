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
from zope import schema, interface
from zope.i18nmessageid import MessageFactory
from zojax.content.space.interfaces import IContentSpace

_ = MessageFactory(u'zojax.site')


class ISite(IContentSpace):
    """ zojax portal instance """

    title = schema.TextLine(
        title = _(u'Title'),
        description = _(u'Site title.'),
        required = True)
    title.order = 1

    description = schema.Text(
        title = _(u'Description'),
        description = _(u'Site description.'),
        required = False)
    description.order = 2
