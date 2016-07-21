# Need to be executed too: the Concept base models are depending on ConfNature, defined per application.
with open("data_manager/models.py") as f:
        code = compile(f.read(), "data_manager/models.py", 'exec')
        exec(code)

import collections

##
## Forwarding most base models
##
class ConceptNature(ConceptNatureBase):
    pass

class TagToOccurrence(TagToOccurrenceBase):
    pass

class AttributeCategory(AttributeCategoryBase):
    pass

class Attribute(AttributeBase):
    pass

class Distinction(DistinctionBase):
    pass

class ReleaseDistinction(ReleaseDistinctionBase):
    pass

class ReleaseAttribute(ReleaseAttributeBase):
    pass

class ReleaseCustomAttribute(ReleaseCustomAttributeBase):
    pass

class ReleaseComposition(ReleaseCompositionBase):
    pass

class OccurrenceAttribute(OccurrenceAttributeBase):
    pass

class OccurrenceCustomAttribute(OccurrenceCustomAttributeBase):
    pass

class OccurrenceComposition(OccurrenceCompositionBase):
    pass


##
## Customization of the 3 base models
##
class Concept(ConceptBase):
    """ 
    Concret Concetp, deriving from abstract ConceptBase, to give it deployment-specific fields 
    without introducing an additional DB table. 
    """  
    pass


class Release(ReleaseBase):
    pass

class Occurrence(OccurrenceBase):
    pass

##
## Extra models
##
