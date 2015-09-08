function before(selector, html_content)
{
    $(selector).before(html_content)
}

function div_replacer(html_content)
{
    // For each division at the top level of html_content, find a division with the same id in the dom, and replace
    // the div in the dom with the corresponding div in html_content.
    $(html_content).filter("div").each(function(index)
       {
           $("#"+this.id).replaceWith(this)
       })
}

function main_function()
{
    // Prepare the spot for specifics
    $(".submit-row").before("<div id=\"collecster_specifics\"></div>")

    // 'id_${field_name}' id is assigned by Django by default.
    $("#id_release").change(
        function()
        {
            var id = $("#id_release").val()
            if(!id)
            {
                id = 0
            }
            $.ajax("/data_manager/ajax/release/" + id  + "/specific_admin_formset/html/",
                   { success: div_replacer})
            $.ajax("/data_manager/ajax/release/" + id  + "/attributes_admin_formset/html/",
                   { success: div_replacer})
        })

    $("#id_concept").change(
        function()
        {
            var id = $("#id_concept").val()
            if(!id)
            {
                id = 0
            }
            $.ajax("/data_manager/ajax/concept/" + id  + "/specific_admin_formset/html/",
                   { success: div_replacer})
        })
}

$(document).ready(main_function)
