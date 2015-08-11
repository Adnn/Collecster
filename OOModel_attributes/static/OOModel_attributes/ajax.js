function inserter(selector, html_content)
{
    $(selector).replaceWith(html_content)
}

// could use bind() instead, with a first argument of 'undefined'
function wrapped_inserter(selector)
{
    return function(html_content)
    {
        inserter(selector, html_content)
    }
}

function main_function()
{
    // 'id_${field_name}' id is assigned by Django by default.
    $("#id_release").change(
        function()
        {
            var id = $("#id_release").val()
            if (id)
            {
                $.ajax("http://localhost:8000/OO_attrib/ajax/release/" + id  + "/admin_formset/html/",
                       { success: wrapped_inserter("#instanceattribute_set-group") })
                $.ajax("http://localhost:8000/OO_compo/ajax/release/" + id  + "/admin_formset/html/",
                       { success: wrapped_inserter("#container_of_set-group") })
            }
            else
            {
                $.ajax("http://localhost:8000/OO_attrib/ajax/release/empty_admin_formset/html/",
                       { success: wrapped_inserter("#instanceattribute_set-group") })
                $.ajax("http://localhost:8000/OO_compo/ajax/release/empty_admin_formset/html/",
                       { success: wrapped_inserter("#container_of_set-group") })
            }
        })
}

$(document).ready(main_function)
