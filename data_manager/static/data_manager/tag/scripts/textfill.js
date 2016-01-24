;(function($) {
$.fn.textfill = function(options) {
    //var fontSize = options.maxFontPixels;
    var fontSize = parseInt($(this).css("font-size"));
    var ourText = $('.tweak:visible:first', this);
    var maxHeight = $(this).height();
    var maxWidth = $(this).width();
    var cssMaxWidth = ourText.css('max-width');

    parent = ourText.parent();
    cssMaxWidth = parent.css("max-width");
    if (cssMaxWidth !== 'none')
    { 
        maxWidth = parseInt(cssMaxWidth);
        //ourText.css("max-width", "none"); // error, then the text is not limited anymore, so it does not wrap...
    }

    var textHeight;
    var textWidth;
    do {
        //ourText.css('font-size', fontSize);
        $(this).css('font-size', fontSize);
        textHeight = ourText.outerHeight(true);
        textWidth = ourText.outerWidth(true);
        fontSize = fontSize - 1;
    } while ((textHeight > maxHeight || textWidth > maxWidth) && fontSize > 3);

    $(this).height(textHeight); //resizes the ".jtextfill" to tightly hug its ".tweak" content

    //if (cssMaxWidth !== "none")
    //{
    //    ourText.css("max-width", textWidth);
    //}
    if (cssMaxWidth !== "none")
    {
        parent.css("max-width", textWidth)
    }

    // If the release_name freed up some space, give it the toe platform div
    if ($(this).hasClass("release_name")) 
    {
        $(".platform").height($(".upper_content").outerHeight() - ($(".sp1").outerHeight()+textHeight))
    }

    return this;
}
})(jQuery);

var fun = function() {
//$(window).load(function() {
    //$('.jtextfill').textfill({ maxFontPixels: 200 });
    $('.jtextfill').each(function(index)
                         {
                             $(this).textfill();
                         });
}
//$(document).ready(fun);
$(window).load(fun);
$(document).fun = fun;
