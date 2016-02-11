from .config_utils import *

from django.db import models

import collections

##
## Specifics
##
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

    DataTuple = collections.namedtuple("DataTuple", ["ui_value", "ui_group", "tag_color", "release_category", "occurrence_category", "automatic_attributes"])
    DATA = collections.OrderedDict((
        (COMBO,     DataTuple(COMBO,    UIGroup._HIDDEN,    "grey", ReleaseCategory.EMPTY,     OccurrenceCategory.EMPTY,    (), )),
        (RECORD,    DataTuple('Record', UIGroup._TOPLEVEL,  "blue", ReleaseCategory.EMPTY,     OccurrenceCategory.EMPTY,    automatic_attributes, )),
    ))
