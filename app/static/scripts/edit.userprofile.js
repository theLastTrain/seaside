/**
 * Created by axl on 16/7/9.
 */


'use strict';
var
    parent = document.getElementById('item-location'),
    hiddens = parent.getElementsByClassName('edit-wrap')[0],
    self = hiddens.getElementsByTagName('a')[0];
    if(self != null && self != undefined) {
       self.onclick = function(){
           hiddens.style.display = 'none';
           parent.getElementsByClassName('edit-hidden')[0].style.display = 'inline-block';
       }
    }


function changeLocation(){
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if(4 == xhr.readyState && 200 == xhr.status) {
            parent.style.display = "none";
            parent.parentElement.getElementsByTagName('span')[0].style.display='inline';
            document.getElementById("user-location").innerHTML = xhr.responseText;
        }
    }
    xhr.open("post", "/edit-profile/location", true);
    var
            parent = document.getElementById("item-location").getElementsByClassName('edit-hidden')[0],
            form = parent.getElementsByTagName('form')[0];
    xhr.send(new FormData(form));
}
