/**
 * Created by axl on 16/7/19.
 */

'use strict';

$(document).ready(function(){
    $('nav li').click(function(){
        $(this).addClass('active').siblings().removeClass('active');
    });
});


$(document).ready(function(){
    $('a.load-section').each(function(){
       var that = this;
       that.onclick = function(){
           $('.user-profile-section-wrap').load(this.href, function(responseText, statusTxt, xhr){
               if('success' === statusTxt){
                   generate_thumbnail();
                   bind_follow();
                   bind_like();
               }
               if('error' === statusTxt){
                   alert("Error: " + xhr.status + ": "+xhr.statusText);
               }
           });
           return false;
       };
    });
});


function loadSection(route, sectionClassName) {
    var sectionXhr = new XMLHttpRequest();
    sectionXhr.onreadystatechange = function(){
        if(4 === sectionXhr.readyState && 200 === sectionXhr.status){
            document.getElementsByClassName(sectionClassName)[0].innerHTML = sectionXhr.responseText;
            generate_thumbnail();
            bind_follow();
            bind_like();
        }
    };
    sectionXhr.open('get', route, true);
    sectionXhr.send();
}