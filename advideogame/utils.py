from data_manager.collecster_exec import collecster_exec

collecster_exec("data_manager/utils.py")


def find_interface_detail(specification_interface):
    """
    Given a BaseSpecificationInterface instance, return its corresponding 
    SystemInterfaceDetail or CommonInterfaceDetail instance.
    """
    try:
        interface_detail = \
            SystemInterfaceDetail.objects.get(interfacedetailbase_ptr=specification_interface.interface_detail_base)
    except SystemInterfaceDetail.DoesNotExist:
        interface_detail = \
            CommonInterfaceDetail.objects.get(interfacedetailbase_ptr=specification_interface.interface_detail_base)
    return interface_detail
        

def region_ancestors(region):
    """ Returns the ancestors of 'region', but not region itself, from the direct parent up """
    ancestors = []
    parent = region.parent_region
    while parent:
        ancestors.append(parent)
        parent = parent.parent_region
    return ancestors


def is_region_superset(regions_superset, regions_subset):
    """
    Indicates wether ``regions_superset`` includes all the regions in ``regions_subset``.
    Taking into account the fact that a parent region logically includes any of its (recursively) nested regions.
    """
    subset      = set(regions_subset)
    superset    = set(regions_superset)

    not_in_superset = subset - superset
    for region in not_in_superset:
        if set(region_ancestors(region)).isdisjoint(superset):
            return False
    return True

