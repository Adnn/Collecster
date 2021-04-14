========
Archived
========

**********************
Rubber duck discussion
**********************

* What about accessories with several functions (eg. Action replay Saturn EMS)
  -> ALLOW MULTIPLE ACCESSORY SUBCATEGORIES IN CONCEPT

  * and perhaps even cross console/accessory (imagine, a console contained in a gamepad) -> YES, no limits on the combinations
  * do we allow « main » function ? -> YES, there is a primary nature


*  Several releases of the same console contain exactly the same product, yet we have to duplicate the  « compatibility list » each time.

   * -> Introduce another layer of abstraction for hardware, describing its compatibility.
     When releasing a hardware concept, do not directly select base system or media, but a « system specification »
     containing the compatible system/media, and extensible with other informations (e.g.: peripheral interfaces,…).
   * It could also store features like wireless, force feeback, etc… for accessories
     -> NO, details like force feedback, rumble do not affect the compatibility of the system.
     Decoupling the notions make the system spec more generic, and maximizes its reusability.
     Wireless is a special kind of interface, which is model like other interfaces by system spec.


* What if several different media are distributed, how does the self handles that ?

  * do like with games, and allow for a cardinality ?
    -> NO, it introduces a special case forcing to repeat some specifics.
  * go the other way, remove cardinality, and take advantage of composition capacities
    (removing the need for cardinalty, replacing it by the same number of nested releases)
    -> YES, naturally leverage the base behaviour to store data for each (nested) media.


* Accessories sold with a console should not be required to be instances of a loose release: it is semantically not loose !
  But, unlike an immaterial software, it is a physical object, which could have specificities, color, etc.

  * optional radio button between

    * loose
    * part of package ??
    * unsure of the content

  * What about just releasing it, potentially without attributes set, but not marking it loose ? -> YES
    Also mark it another distiction than loose like "part of pack without discrete box"


* Is it required to make a release for a loose object ??

  * It has specificities… a loose game still has a platfrom, etc. -> WE NEED TO RELEASE


* How to enter an accessory with for example 2 pads and the RF receiver ?

  * make the RF and attribute, and compose the top level release with two release of the wireless controller
    -> NO, the problem is that the wireless controller would often not exist as a separate release,
    making this approach introduce "virtual releases"
  * consider it is a non-composed release, and self is the receiver + 2 pads ? (but potential problem with colors of the two pads)
  * fiddle around the notion of sub-release, introducing a sub-release with no concept, inheriting it concept from the composed one ?

    * Just make a new « special release value » ‘subobject' <- actually, woud be rendered very complicated by the specifics: which to assign to subobjects, etc..

  * Simply duplicates the [content]self attribute, and use the optional note to distinguish which "part" the self corresponds to
    -> YES, this is already possible, and the case is really exceptional. If the sub-component have distinct colors,
    leverage that to make distinctive note while retaining the information
    (drawback: info is retained in a non-structured manner, though)


* Should we split release notion between « object » and « release » (deriving from object) <- NO

  * this way a release could have sub-objects not correspondng to releases (e.g.. the RF pads for NES)
  * Or just make them both objects at the same level, and possibly compose release with release OR object (an object mandatorily being in a release)
  * [ANSWER] NO need: multiples [self] attributes (only the first one being automatic), the note is used to distinguish the different subjects


* should not owner on instance be a user ?

  * It is a person, and users are optionaly linked to a person
    <- YES, it was decided that the owner is not necessarily a user on the system.
    It would be uncommon, but it facilitates "hosting" someone else occurrences, and since several users can be attached to the same Person,
    it would make "re-rooting" a collection into a different deployment a bit easier.


* How to model company division/team (Sega AM#… etc). Note that divisions can be sold, thus change "mother company" !

  * Do not worry about owners, and model development studios as separate companies
    <- YES, for the moment. Introduction of the "Company Service" table to indicate the capacities of each company.
