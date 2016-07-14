/**
 * Created by axl on 16/7/9.
 */


'use strict';
var posts = document.getElementsByClassName('content');
for(var i = 0; i < posts.length ; i++) {
    var foldable = posts[i];
    if(foldable.offsetHeight > 118) { //hide the original then create alternative
        //create fold button
        var fold = document.createElement('button');
        fold.setAttribute('class', 'a-styled-button pull-right text-muted');
        fold.innerHTML = '<i class = "icon-resize-small"></i> <strong>收起<strong>';
        fold.onclick = function(){
            this.parentElement.style.display = 'none'
            this.parentElement.parentElement.getElementsByClassName('alternative')[0].style.display = '';
        };
        foldable.appendChild(fold);
        foldable.style.display = 'none';
        var alternative = document.createElement('div');
        alternative.setAttribute('class', 'alternative clearfix');
        //get first 240 bytes of original text
        var text = foldable.innerText;
        text = text.replace(/<[^>]+>/g,'').replace(/\s+/g,'');
        text = subStringByBytes(text) + '...';
        //create text node
        var tnode = document.createTextNode(text);
        alternative.appendChild(tnode);
        //make banner from first img if exist
        var firstImg = foldable.getElementsByTagName('img')[0];
        //create banner
        if(firstImg && (firstImg.width != 200 || firstImg.height != 112)){
            var banner = document.createElement('img');
            banner.setAttribute('class', 'img-inline');
            banner.src = firstImg.src;
            alternative.insertBefore(banner, tnode);
        }
        //create unfold button
        var unfold = document.createElement('a');
        unfold.innerText = ' 展开全部';
        unfold.onclick = function(){
            this.parentElement.style.display = 'none';
            this.parentElement.parentElement.getElementsByClassName('content')[0].style.display = '';
        };
        alternative.appendChild(unfold);
        foldable.parentElement.appendChild(alternative);
    }
}


function like(postId, domItem){
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function(){
        if(4 === xhr.readyState && 200 === xhr.status){
            var icon = domItem.childNodes[1];
            var cnt = domItem.getElementsByTagName('div')[0];
            console.log(cnt);
            var jsonRsp = JSON.parse(xhr.responseText);
            if(false===jsonRsp['liking']){
                icon.setAttribute('class', 'icon-heart-empty');
                cnt.innerHTML = jsonRsp['cnt'];
            }
            else if(true===jsonRsp['liking']){
                icon.setAttribute('class', 'icon-heart');
                cnt.innerHTML = jsonRsp['cnt'];
            }
        }
    }
    xhr.open("get", "/like/"+postId , true);
    xhr.send();
}