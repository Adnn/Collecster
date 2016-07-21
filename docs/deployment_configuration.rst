.. role:: app(emphasis)
.. role:: instance(emphasis)

============================
Deployment and configuration
============================

*******************
Management commands
*******************

Offline consistency checks
==========================

.. note::
   This scripts is coupled to advideogame for the moment, thus will only check for this specific configuration.

Run scripts/constraints_enforcer.py

.. _users_management:

Users management
================

:app:`supervisor` provides commands to manage users of Collecster::

     adduserext username

     addusercollection username configuration user_collection_id

.. warning::
   **deluserext** will also delete all data entered by this user. It should only be invoked if the user was never used.::

     deluserext username


*************************
Application configuration
*************************


Model attributes
================

Collecster reserve several class attributes, all prefixed with "collecster\_",
that it interprets with specific meanings when present.
This is one of the main mechanism that allows customization of behaviours for specific configurations.

.. _collecster_properties:

collecster_properties
---------------------

.. note::
   This attribute is applicable to following models: Release, Occurrence, and all of their specific models.

This attribute is added to a ``Model`` class, to control which of the fields of this model are required or forbidden, and under which conditions.

Its value is a dictionary, of the form::

        collecster_properties = {
            "forbidden_on_material":        ("field_A"),
            "required_on_non_material":         ("field_B", "field_C"),
            ...
        }

Each key-value pair in this dictionary defines a rule.

The keys have two possible forms: ``required_on_[non_]{condition}`` or ``forbidden_on_[non_]{condition}``, to control if the associated list of fields are respectively mandatory or forbidden when the condition is true (or when it is false, if ``non_`` optional modifier is present).
The condition itself is evaluated by invoking the evaluator method ``is_{condition}(self)`` on the ``Model`` class. This method must thus exist, and return a boolean value.

Additionally, a guard method ``{condition}_is_known(self)`` can optionally be implemented on the ``Model`` class, returning a boolean value.
When present, this method will be called before attempting to invoke the evaluator: only if this guard returns ``True`` will the corresponding evaluator be invoked.
When the guard returns ``False``, it is an indicator that the condition cannot currently be evaluated, thus the rule is ignored.

.. note::
   The properties allow M2M fields names in the value tuple.

.. note::
   **developper**: Those rules are enforced at the Form level, by inheriting from PropertyAwareModelForm (not at the model leve).


.. _collecster_readonly_edit:

collecster_readonly_edit
------------------------

This attribute can be added to :ref:`CollecsterModelAdmin` classes. Its value is a collection of field names.
Those fields will be restricted to read-only on edition forms, but writeable on addition forms.


.. _collecster_exclude_create:

collecster_exclude_create
-------------------------

This attribute can be added to :ref:`CollecsterModelAdmin` classes. Its value is a collection of field names.
Those fields will not be shown on addition forms when creating new objects, but will be shown on edition forms of existing objects.


.. _collector_dynamic_inline_classes:

collecster_dynamic_inline_classes
---------------------------------

This attribute can be added to :ref:`CollecsterModelAdmin` classes.
It supercedes the Django's `inlines` attribute, by allowing to dynamically generate admin inlines by invoking a callable, in addition to statically listing inlines classes.

Its value is an ordered dictionary, of the form

.. code:: python

        collector_dynamic_inline_classes = OrderedDict((
            ("specific",         (utils.occurrence_specific_inlines)),        
            ("group_b",          (AdminInlineClass_1, AdminInlineClass_2,)),        
            ...
        ))

In each key-value pair, the key is a group name, and the value is either:

* A collection of ``AdminInline`` classes, exactly like what Django's ``inlines`` attribute was expecting.
* A callable, taking two positional arguments, the :instance:`request` and the (potentially null) model :instance:`object`.
  This callable must return a collection of admin inline classes.

Group names offer an optional mechanism to only get inline instance for some given groups. See :ref:`collecster_payload_group` for further details.

.. note::
   **developper**: This is handled by ``CollecsterModelAdmin`` override of ``get_inline_instances`` method.


.. _collecster_instance_callback:

collecster_refresh_inline_classes
---------------------------------

Defines an optional list of group names from :ref:`collector_dynamic_inline_classes` whose inline formsets will be 
updated on ajax requests.

collecster_instance_callback
----------------------------

This attribute can be added to :ref:`CollecsterModelAdmin` classes.
When the `collector_dynamic_inline_classes`_ allowed to dynamically assign new inline **classes** to a ``Form``,
this attribute allows to dynamically configure **instances** of those inlines when they are constructed.

Its value is a callable, taking three positional arguments: the :instance:`formset` to configure, the :instance:`request` and the (potentially null) model :instance:`object`. The callable does not return any value. 
As an example, the callable is a good place to dynamically set initial values, or querysets of foreign keys. 

.. note::
   **developper**: This is handled by ``CollecsterModelAdmin`` override of ``_create_formsets`` method.

form_callback
-------------

In the case of *specific* model classes, it is possible to define a ``form_callback`` method taking the ``form``, the
``request`` and the ``object``. This method can thus customise the provided ``form``.

When present, this method is invoked as if the `ModelAdmin` of the corresponding :instance:`specific` instance was
defining a `collecster_instance_callback`_ forwarding the first (and only) form of the formset to ``form_callback``.


Natures
=======

**Nature** is a central concept of Collecster, and the other major point of configurability, alongside with the models.

The natures, which are assigned at the :instance:`concept` level, drive several aspects of the system,
and most notably they control which *specifc*\(s) will be assigned to each of the :ref:`3 base models <three_base_models>`.

Those behaviour are controlled by defining a ``ConfigNature`` class, deriving from ``data_manager.ConfigNature``,
and with a ``DATA`` member. This member must be an ``OrderedDict`` associating nature database values to an instance 
of ``data_manager.ConfigNature.DataTuple``.

natures display
---------------

The two first elements in a ``DataTuple`` control the display name of the nature, and an optional group name (which is
also used as the display value for the group).

There are two reserved group names:

* the empty string ``""``, which is interpreted as top level (i.e., not nested under any group)
* ``"_HIDDEN"``, which means the nature will not be displayed for the user to select. It is intented for advanced uses
  where the system defines some special natures, potentially assigned to built-in special concepts (eg. the :instance:`combo`).
  Its is recommended to prefix the database value of such special natures with and underscore. (eg. ``_COMBO``).

.. _specific_mapping:

controlling specific(s)
-----------------------

The configuration controls which *specifc* models are assigned to ``Concept``, ``Release`` and ``Occurrence``, depending
on the *nature*\(s) assigned to the :instance:`concept`.

.. note::
   A good example of the code as a whole involved in the *specific*\s configuration is found in the file
   advideogame/configuration.py

The first step in assigning *specific* is of course to define the *specific* models.
The only requirement, appart from deriving from ``django.db.models.Model`` as usual, is that a specific must have
a foreign key to the corresponding base class (i.e. either ``Concept`` or ``Release`` or ``Occurrence``), whose name
is the lowercase class name.

.. note::
   It is recommanded to group ``specific`` models for a given base class under a class (eg. ``ConceptSpecific``), 
   and to have the concrete ``specific`` derive from an ``AbstractBase`` defining the foreign key.

Once the ``specific`` models are defined, they can be grouped in different tuples, called **categories**.
The ``compose`` function allows to flatten several tuples into one, allowing to easily define a *category* 
as a superset of another.

Finally, those *categories* are assigned to corresponding entries in the ``DataTuple`` instances 
associated to the *natures* of interest.
This way, the associated *natures* will have all the ``specific`` in the assigned *category*.

.. note::
   As advertised, a :instance:`concept` can have multiple natures. In this case, the base classes will be assigned
   the distinct set of all the specific models corresponding to the union of the categories for each nature.
   If the same specific appears in different natures, only one is assigned.
