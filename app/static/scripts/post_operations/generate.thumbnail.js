/**
 * Created by axl on 16/7/9.
 */


'use strict';
var posts = document.getElementsByClassName('content');
for(var i = 0; i < posts.length ; i++) {
    var foldable = posts[i];
    if(foldable.offsetHeight > 118) { //hide the original then create alternative
        //create fold button
        var fold = document.createElement('a');
        fold.style.cssText = 'float: right; display:inline-block;';
        fold.innerHTML = '<i class = "icon-resize-small"></i> <strong>收起<strong>';
        fold.href = '#' + foldable.parentElement.getElementsByTagName('a')[0].name;
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
        text = text.replace(/\s+/g,' ');
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
        unfold.style.display = 'inline-block';
        unfold.onclick = function(){
            this.parentElement.style.display = 'none';
            this.parentElement.parentElement.getElementsByClassName('content')[0].style.display = '';
        };
        alternative.appendChild(unfold);
        foldable.parentElement.appendChild(alternative);
    }
}


