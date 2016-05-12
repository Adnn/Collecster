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

    // moves potential specifics that would be present at page load (eg. correction of form error)
    // under the 'collectsr_specifis' div
    $(".collecster_specific_wrapper").appendTo("#collecster_specifics")
    
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
            $.ajax("/" + window.collecster_app_name +  "/ajax/release/" + id  + "/admin_formsets/html/",
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
            $.ajax("/" + window.collecster_app_name +  "/ajax/concept/" + id  + "/admin_formsets/html/",
                   { success: div_replacer})
        })


    /*
     * Event callbacks on live nature changes on the Concept form
     */
    // This function retrieves the values for all the nature select elements, and send the ajax request
    function request_concept_specifics(natures_selector)
    {
        var natures = []
        natures_selector.each(function(index, element)
            {
                if (element.value)
                {
                    natures.push(element.value)
                }
            })
        $.ajax("/" + window.collecster_app_name + "/ajax/concept_admin_formsets/html/",
               {
                    data: $.param({ nature: natures }, true),
                    success: div_replacer
               })
    }

    // This function retrieves all the nature select elements in the current page state, and assign them a change callback
    function get_natures_selector()
    { 
        var natures_selector = $("#additional_nature_set-group").find("select").add("#id_primary_nature") 
        natures_selector.off("change") // removes the existing change callbacks, as they would otherwise accumulate
        natures_selector.change({"natures_selector": natures_selector} , // dictionary forwarded into event.data
                                function(event){ request_concept_specifics(event.data.natures_selector) } )
        return natures_selector
    }

    if ($("#additional_nature_set-group").length) // considers that we are on the Concept form only if this is present
    {
        get_natures_selector(); // on document ready, there is already the primary nature select element,
                                // registers the change callback on it.

        // Observe changes in the div containing additional natures select elements
        var natures_count_observer = new MutationObserver(function(mutations, observer)
            {
                natures_selector = get_natures_selector()
                request_concept_specifics(natures_selector) // when the div content changes, we request the specifics each time
                    // in case the change was the removal of a non-empty additional nature
                    // (we could actually conditionally check for this situation analyzing "mutations", but let's not bother now).
            })
        natures_count_observer.observe($("#additional_nature_set-group")[0], {childList: true, subtree: true})
    }
}

$(document).ready(main_function)
