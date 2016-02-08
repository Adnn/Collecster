from .config_utils import *

from django.db import models

import collections

##
## Specifics
##
class ReleaseSpecific(object):
    """ ReleaseSpecific classes are added to Release instances depending on their nature(s) """

    class AbstractBase(models.Model):
        class Meta:
            abstract = True
        release = models.ForeignKey('Release')

    #class CustomRel(AbstractBase):

RelSp = ReleaseSpecific

class ReleaseCategory:
    EMPTY       = ()
    #CUSTOM       = (RelSp.CustomRel,)


class OccurrenceSpecific(object):
    """ OccurrenceSpecific classes are added to Occurrence instances depending on their nature(s) """

    class AbstractBase(models.Model):
        class Meta:
            abstract = True
        occurrence = models.ForeignKey('Occurrence')

    #class CustomOcc(AbstractBase):
   
OccSp = OccurrenceSpecific

class OccurrenceCategory:
    EMPTY   = ()
    #CUSTOM  = (OccSp.CustomOcc,)


def automatic_self():
    return (get_attribute("content", "self"), )

##
## Defines the natures and all their associeted data
##
class ConfigNature(ConfigNature):
    class UIGroup:
        _HIDDEN         = "_HIDDEN"
        _TOPLEVEL       = ""
        SOFT            = "Software"

    CONSOLE = "CONSOLE"
    GAME = "GAME"

    DataTuple = collections.namedtuple("DataTuple", ["ui_value", "ui_group", "tag_color", "release_category", "occurrence_category", "automatic_attributes"])
    DATA = collections.OrderedDict((
        #(CONSOLE,   DataTuple('Console',    UIGroup._TOPLEVEL,  "red",      ReleaseCategory.CONSOLE,   OccurrenceCategory.CONSOLE,      automatic_self )),
        #(GAME,      DataTuple('Game',       UIGroup.SOFT,       "green",    ReleaseCategory.SOFTWARE,  OccurrenceCategory.OPERATIONAL,  automatic_self )),
    ))
