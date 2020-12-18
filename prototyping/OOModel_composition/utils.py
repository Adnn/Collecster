from .models import *


def retrieve_release_composition(release_id):
    return ReleaseComposition.objects.filter(container_release=release_id)


def force_formset_size(formset, size):
    formset.extra   = size
    formset.max_num = size
    

def composition_queryset(formset, obj, release_id=None):
    if obj:
        release_id = obj.release

    if release_id is None or release_id==0:
        force_formset_size(formset, 0)
    else:
        nested_releases = [compo.nested_object for compo in retrieve_release_composition(release_id)]
        force_formset_size(formset, len(nested_releases))

        for release, form in zip(nested_releases, formset):
            form.fields['nested_instance'].queryset = Instance.objects.filter(release=release)
            form.fields['nested_instance'].label = "Nested {} instance".format(release.name)
