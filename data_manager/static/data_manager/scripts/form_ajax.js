//function cleaner(selector)
//{
//    $(selector).empty()
//}
function inserter(selector, html_content)
{
    //cleaner(selector)
    //$(selector).append(html_content)
    $(selector).replaceWith(html_content)
}

function before(selector, html_content)
{
    $(selector).before(html_content)
}

function wrapped_inserter(selector)
{
    return function(html_content)
    {
        inserter(selector, html_content)
    }
}

function main_function()
{
    // Prepare the spot for specifics
    $(".submit-row").before("<div id=\"collecster_release_specifics\"></div>")

    // 'id_${field_name}' id is assigned by Django by default.
    $("#id_release").change(
        function()
        {
            var id = $("#id_release").val()
            if (id)
            {
                $.ajax("http://localhost:8000/OO/ajax/release/" + id  + "/admin_formset/html/",
                       { success: wrapped_inserter("#instanceattribute_set-group") })
                $.ajax("http://localhost:8000/OO_compo/ajax/release/" + id  + "/admin_formset/html/",
                       { success: wrapped_inserter("#container_of_set-group") })
            }
            else
            {
                $.ajax("http://localhost:8000/OO/ajax/release/empty_admin_formset/html/",
                       { success: wrapped_inserter("#instanceattribute_set-group") })
                $.ajax("http://localhost:8000/OO_compo/ajax/release/empty_admin_formset/html/",
                       { success: wrapped_inserter("#container_of_set-group") })
            }
        })

    $("#id_concept").change(
        function()
        {
            var id = $("#id_concept").val()
            if (id)
            {
                $.ajax("/data_manager/ajax/concept/" + id  + "/admin_formset/html/",
                       { success: inserter.bind(undefined, "#collecster_release_specifics")})
            }
            else
            {
                $.ajax("/data_manager/ajax/concept/empty_admin_formset/html/",
                       { success: inserter.bind(undefined, "#collecster_release_specifics")})
            }
        })
}

$(document).ready(main_function)
