/**
 * Created by axl on 16/7/9.
 */
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