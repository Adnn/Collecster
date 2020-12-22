;(function($) {
$.fn.textfill = function(options) {
    // CSS font-size will act as the upper-limit, since it is the starting value for recursion
    var fontSize = parseInt($(this).css("font-size"));
    var ourText = $('.tweak:visible:first', this);
    // We rely on the flow giving correct sizes to the element
    // (even when the text overflows due to initial fontsize)
    var maxHeight = $(this).height();
    var maxWidth = $(this).width();

    // Note: I am not sure this is useful anymore.
    // the parent of the .tweak element might specify a max-width
    // ensure it is taken into consideration
    parent = ourText.parent();
    cssMaxWidth = parent.css("max-width");
    if (cssMaxWidth !== 'none')
    {
        maxWidth = parseInt(cssMaxWidth);
        //ourText.css("max-width", "none"); // error, then the text is not limited anymore, so it does not wrap...
    }

    var textHeight;
    var textWidth;
    // Recurse to find the maximal font-size fitting in maxWidth,maxHeight
    do {
        $(this).css('font-size', fontSize);
        // Attention: ourText.outerHeight() returns the decimal height as a rounded int
        // This can break the layout when rounding to a lower int
        textWidth = Math.ceil(ourText[0].getBoundingClientRect().width);
        textHeight = Math.ceil(ourText[0].getBoundingClientRect().height);
        fontSize = fontSize - 1; // Used by next iteration
    } while ((textHeight > maxHeight || textWidth > maxWidth) && fontSize > 3);

    // Resizes the ".jtextfill" to tightly hug its ".tweak" content
    // This allows to keep relative distance between release name and platform,
    // even if release is made smaller.
    $(this).height(textHeight);

    // If the parent specified a max-width, it is better to resize it so it hugs the text content
    // (otherwise it might use max-width as it width, wasting horizontal space that could be used by other elements)
    if (cssMaxWidth !== "none")
    {
        parent.css("max-width", textWidth)
    }

    // Note: commented-out, we keep the platform height static now
    //// If the release_name freed up some space, give it to the platform div
    //if ($(this).hasClass("release_name"))
    //{
    //    $(".platform").height($(".upper_content").height()
    //                            - $(".sp1").outerHeight()
    //                            - $(this).outerHeight())
    //}

    return this;
}
})(jQuery);

var fun = function() {
    $('.jtextfill').each(function(index)
                         {
                             $(this).textfill();
                         });
}
$(window).load(fun);
