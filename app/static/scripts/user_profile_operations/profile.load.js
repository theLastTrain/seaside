/**
 * Created by axl on 16/7/19.
 */

'use strict';

function loadSection(route, sectionClassName) {
    var sectionXhr = new XMLHttpRequest();
    sectionXhr.onreadystatechange = function(){
        if(4 === sectionXhr.readyState && 200 === sectionXhr.status){
            loadScripts('../static/scripts/post_operations/generate.thumbnail.js');
            loadScripts('../static/scripts/post_operations/like.js');
            document.getElementsByClassName(sectionClassName)[0].innerHTML = sectionXhr.responseText;
        }
    };
    sectionXhr.open('get', route, true);
    sectionXhr.send();
}

var
        user_posts = document.getElementsByClassName('load-section')[0],
        like_posts = document.getElementsByClassName('load-section')[1],
        followers = document.getElementsByClassName('load-section')[2],
        followed = document.getElementsByClassName('load-section')[3];
user_posts.onclick = function(){
    loadSection(user_posts.href, 'user-profile-section-wrap');
    this.parentElement.parentElement.getElementsByClassName('active')[0].classList.remove('active');
    this.parentElement.classList.add('active');
    return false;
};
like_posts.onclick = function(){
    loadSection(like_posts.href, 'user-profile-section-wrap');
    this.parentElement.parentElement.getElementsByClassName('active')[0].classList.remove('active');
    this.parentElement.classList.add('active');
    return false;
};
followers.onclick = function(){
    loadSection(followers.href, 'user-profile-section-wrap');
    return false;
};
followed.onclick = function(){
    loadSection(followed.href, 'user-profile-section-wrap');
    return false;
}


