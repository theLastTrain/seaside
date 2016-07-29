/**
 * Created by axl on 16/7/14.
 */

'use strict';


/*
* get the first 240 bytes of a string,
* meaning 120 chinese characters or 240 ascii characters
*
* */
function subStringByBytes(str) {
    var len = 0;
    for (var i = 0; i < str.length; i++)
    {
        if(str[i].match(/[^x00-xff]/ig) != null) {
            len += 2;
        }
        else {
            len += 1;
        }
        if(len >= 240){
            break;
        }
    }
    return str.substr(0, i);
}

/*
* load js dynamically
* */
function loadScripts(url) {
    var script = document.createElement('script');
    script.type = 'text/javascript';
    script.src = url;
    document.body.appendChild(script);
}

