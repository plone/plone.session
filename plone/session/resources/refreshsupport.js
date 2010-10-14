/* Session cookie refresh support */
/*jslint browser: true, devel: true */
/*global jQuery: false*/

(function($) {
    
var last_activity = new Date();

function sessionActivity() {
    last_activity = new Date();
}

function startSessionRefresh(index) {
    var src_last_refresh = new Date();
    var src = this.src;
    var match = src.match(new RegExp("[\\?|&]minutes=([^&#]*)"));
    var minutes = match ? parseFloat(match[1]) : null;
    minutes = minutes  ? minutes : 5.0;

    if (console && console.info) {
        console.info('plone.session.refreshsupport.js: Setting up ' + src +
            ' to refresh every ' + minutes + ' minutes');
    }

    function sessionRefresh() {
        if (last_activity > src_last_refresh) {
            src_last_refresh = new Date();
            $.getScript(src);
            if (console && console.info) {
                console.info( '[' + src_last_refresh +
                    '] plone.session.refreshsupport.js: Refreshing session: ' + src +
                    '. Last Activity: ' + last_activity);
            }
        } else {
            if (console && console.info) {
                console.info(
                    '[' + Date() +
                    '] plone.session.refreshsupport.js: Skipped refresh: ' + src +
                    ' Last Activity: ' + last_activity);
                }
        }
    }
    setInterval(sessionRefresh, minutes * 60 * 1000);
}

$(document).ready(function () {
    $('body').bind('mouseover click keydown', sessionActivity);
    $("head script[src*='?session_refresh=true']").each(startSessionRefresh);
});

})(jQuery);
