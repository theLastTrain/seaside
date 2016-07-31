function follow(followbtn){
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function(){
        if(4 === xhr.readyState){
            if(200 === xhr.status){
                var jsonRsp = JSON.parse(xhr.responseText);
                if(true === jsonRsp['following'])
                {
                    followbtn.classList.remove('btn-primary');
                    followbtn.classList.add('btn-default');
                    followbtn.innerText = '取消关注';
                }
                else {
                    followbtn.classList.remove('btn-default');
                    followbtn.classList.add('btn-primary');
                    followbtn.innerText = '关注';
                }
            }
            else if(403 === xhr.status)
            {
                $('#confirmationMoadl').modal();
            }
        }
    };
    xhr.open('get', followbtn.href, true);
    xhr.send();
}

var followbtn = document.getElementsByName('follow')[0];
followbtn.onclick = function(){
    follow(this);
    return false;
};