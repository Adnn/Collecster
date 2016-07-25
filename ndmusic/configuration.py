from .config_utils import *

from django.db import models

import collections

##
## Specifics
##
class ConceptCategory:
    EMPTY       = ()

class ReleaseCategory:
    EMPTY       = ()

class OccurrenceCategory:
    EMPTY   = ()


##
## Defines the natures and all their associeted data
##
def automatic_attributes():
    return (
        get_attribute("content", "media"),
        get_attribute("packaging", "sleeve"),
    )


class ConfigNature(ConfigNature):
    class UIGroup:
        _HIDDEN         = "_HIDDEN"
        _TOPLEVEL       = ""

    COMBO = "_COMBO"
    RECORD = "REC"

    DATA = collections.OrderedDict((
        (COMBO,     NatureData(COMBO,       UIGroup._HIDDEN,    "grey", ConceptCategory.EMPTY,  ReleaseCategory.EMPTY,  OccurrenceCategory.EMPTY,   (), )),
        (RECORD,    NatureData("Record",    UIGroup._TOPLEVEL,  "blue", ConceptCategory.EMPTY,  ReleaseCategory.EMPTY,  OccurrenceCategory.EMPTY,   automatic_attributes, )),
    ))
