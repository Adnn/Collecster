# Django


## CODE TODO

* Clean up how to enable the custom template for demos (instead of commenting in settings)
* The extending admin/index.html is not used
* The custom Request class is not used

## Model

* Do not capitalize the first letter fo verbose_name

Relationships
* In a many to many relationship, it is possible to query with the name of the « other model » on both sides of the relationship!

Overriding model methods
* the signature should contain *args, **kwargs to automatically work if Django API changes
  * def save(self, *arks, **kwargs)

It is possible to create a proxy model: it inherits from a concrete model, but does not introduce a new table. It is usefull to change the Python behavior.

`Meta.managed=False` disable datable able creation and deletion… Does it still issue save/delete/etc ?

## Form
A Form (forms.Form) is the Python representation of a form to be displayed on a page. It is composed of  Fields, mapping to `<input>` elements (through Django Widgets).

* is_valid() method runs validation on the Form and place the data in cleaned_data member.
* is_bound() tells wether the form
  * has data bound to it (==submitted data), thus can test validity of such data
  * or not (rendered empty or default values)

* accessing unvalidated data should be done directly on request.POST

### In templates
In the template rendering a Form, the first `<form>` subelement should be
`{% csrf_token %}`
`{{ form }}` can be used to render the form content (except the parent <form> and the submit button)

Alternatively, `{{ form.${field_name} }}` can be used to render and individual form widget

 ### Validation
Triggered by calling is_valid() (or full_clean() or accessing .errors). The validation logic is only run on first call.

Raise ValidationError to indicate issue.

Validators are rune after the fields to_python() and validate()
then clean_$fieldname() (to be overrided by user classes). Must get its data from cleaned_data, and return it.
then the form’s sublcass clean() is run (to do form wide validation)

## Form
* full_clean() at some point invokes clean() on each field contained in the form, passing as data widget.value_from_datadict().

Each widget type knows how to retrieve its own data, because some widgets split data over several HTML fields.

Form data is just a dictionary mapping form-field names to string values. This is exactly what request.POST is (it is the usual data source for a form, but any other dict could actually do, see: https://docs.djangoproject.com/en/1.8/ref/forms/api/#checking-which-form-data-has-changed)

## ModelForm
ModelForm is a specialization that deduce its fields from a given Django Model. It fields can be populated by constructing it from an instance of the Model.

## forms.Field
(forms.Field) are associated to a Widget for rendering as HTML. For actual code triggering the render, see BoundField.as_widget() [somehow using widget.value_from_datadict() to get the value argument for rendering]

* prepare_value() is called before returning from BoundField.value()

### MultiValueField
clean() accepts a « decompressed » list of values, and returns the « compressed » data, applying compress()`to it.

## Widget
* render() should return the HTML wrapped in a SafeString
  * it accepts as arguments a name (assigned to the input element)

* value_from_datadict() is the method taking up the datadict (i.e. most of the times, the POST data), the widget name, and lookup the corresponding raw data (usually a trivial lookup data.get(name) ). It is invoked by the forms.Field when it needs the read the data !

### MultiWidget
Is a composite Widget, accepting a list of Widget in its constructor. It can render itself with the provided `value` being a list (one value per component widget), or a « compressed » single value (in which case the value will be first split using `decompress()` method).
The name assigned to component widgets is the `<multiwidgetname>_${index}`

* format_output() can be used to layout the component widgets

## Formset
A formset is a layer of abstraction to work with multiple forms on the same page

## ModelAdmin
ModelAdmin can be given as the second argument to admin.site.register(), allowing to control the admin pages for the model in the first argument.

* fieldsets allow to group fields, assigne html classes (like collapse)
* inlines lists ModelAdmin deriving from InlineModelAdmin (allows to edit a related table inline)

## Templates
They can be placed in a `templates/` folder inside the applications, default config will find them. Yet, the first template to match in the search path is used, so always put templates in namespaces e.g.:
`$django_project/$django_app/templates/$django_app_as_namespace/template.html`

* the `{% url … %}` tag alongside the name argument in url() allows decoupling.
* when including another url conf file, the optional ‘namespace’ argument allows to further separate named views from the imported url conf.

### Rendering from views
```
 template = loader.get_template(‘app/template.html')
    context = RequestContext(request, {
        ‘value’: 5,
    })
return HttpResponse(template.render(context))
or shorter
context = {‘value': 5}
return render(request, ‘app/template.html', context)
  ````

## Admin
### Fieldset
A grouping of form fields in the admin interface, given as a list of 2-tuples: `( (None, {« fields": « a » , « b »}), (« group 1 », {« fields »: « c »}) )`


## File upload
https://docs.djangoproject.com/en/1.8/ref/forms/api/#binding-uploaded-files-to-a-form

## General web dev
get should never modify the server side state (use post for that)
get is usefull to build urls that can be shared to give the same result
Always redirect after a successful post
