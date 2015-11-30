function before(selector, html_content)
{
    $(selector).before(html_content)
}

function div_replacer(html_content)
{
    // For each division at the top level of html_content, find a division with the same id in the dom, and replace
    // the div in the dom with the corresponding div in html_content.
    // Plus potientially do the same with a <script> element following the <div>
    // (this script would be responsible for "Add another ..." button)
    $(html_content).filter("div").each(function(index)
        {
            script = ""
            // if the new <div> is followed by a script, save the element for later insertion
            if($(this).next().prop("tagName") == "SCRIPT")
            {
                script = $(this).next()
            }

            // replace the page's <div> having the same id with the new <div>
            $("#"+this.id).replaceWith(this)

            // if the <div> was followed by a <script> in the page, remove this script
            if($("#"+this.id).next().prop("tagName") == "SCRIPT")
            {
                $("#"+this.id).next().remove();
            }

            // insert the new script if it exists
            if(script)
            {
                $("#"+this.id).after(script);
            }
       })
}

function main_function()
{
    /*
     * Setup
     */
    // prepares the spot for specifics
    $(".submit-row").before("<div id=\"collecster_specifics\"></div>")

    
    // Hack to have the Django Admin Popup trigger a change event on the <select> when it completes
    // see: http://stackoverflow.com/a/33937138/1027706
    function triggerChangeOnField(win, chosenId)
    {
        var name = windowname_to_id(win.name);
        var elem = document.getElementById(name);
        $(elem).change();
    } 

    // original function defined in RelatedObjectLookups.js
    window.ORIGINAL_dismissAddRelatedObjectPopup = window.dismissAddRelatedObjectPopup
    window.dismissAddRelatedObjectPopup = function(win, chosenId, newRepr)
    {
        ORIGINAL_dismissAddRelatedObjectPopup(win, chosenId, newRepr);
        triggerChangeOnField(win, chosenId);
    }


    /*
     * Attach event callbacks
     */ 
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
