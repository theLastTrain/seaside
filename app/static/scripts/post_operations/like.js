/**
 * Created by axl on 16/7/9.
 */


'use strict';
function like(domItem){
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function(){
        if(4 === xhr.readyState && 200 === xhr.status){
            var icon = domItem.childNodes[1];
            var cnt = domItem.getElementsByTagName('div')[0];
            var jsonRsp = JSON.parse(xhr.responseText);
            if(false===jsonRsp['liking']){
                icon.setAttribute('class', 'icon-heart-empty');
                cnt.innerHTML = jsonRsp['cnt'];
            }
            else{
                icon.setAttribute('class', 'icon-heart');
                cnt.innerHTML = jsonRsp['cnt'];
            }
        }
    };
    xhr.open("get", domItem.href, true);
    xhr.send();
}

var likebtns = document.getElementsByClassName('btn-like');
for(var i = 0; i < likebtns.length; i++)
{
    likebtns[i].onclick = function(){
        like(this);
        return false;
    };
}