from .config_utils import *

from django.db import models

import collections

##
## Specifics
##
class ConceptSpecific(object):
    """ ConceptSpecific classes are added to Concept instances depending on their nature(s) """

    class AbstractBase(models.Model):
        class Meta:
            abstract = True
        concept = models.OneToOneField('Concept')

        def get_parent_instance(self):
            return self.concept

    #class CustomCon(AbstractBase):

ConSp = ConceptSpecific

class ConceptCategory:
    EMPTY   = ()
    #CUSTOM  = (ConSp.CustomCon,)


class ReleaseSpecific(object):
    """ ReleaseSpecific classes are added to Release instances depending on their nature(s) """

    class AbstractBase(models.Model):
        class Meta:
            abstract = True
        release = models.ForeignKey('Release')

        def get_parent_instance(self):
            return self.release

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

        def get_parent_instance(self):
            return self.occurrence

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

    DATA = collections.OrderedDict((
                        #       "ui_value", "ui_group",         "tag_color","concept_category",     "release_category",         "occurrence_category",          "automatic_attributes"]
        #(CONSOLE,   NatureData('Console',  UIGroup._TOPLEVEL,  "red",      ConceptCategory.CONSOLE, ReleaseCategory.CONSOLE,   OccurrenceCategory.CONSOLE,     automatic_self )),
        #(GAME,      NatureData('Game',     UIGroup.SOFT,       "green",    ConceptCategory.SOFTWARE,ReleaseCategory.SOFTWARE,  OccurrenceCategory.OPERATIONAL, automatic_self )),
    ))
