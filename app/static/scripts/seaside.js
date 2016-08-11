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

function updateEmailStatus(statusUrl){
    $.getJSON(statusUrl, function(data){
        if(data['state'] === 'SUCCESS'){
            var msg = $('<div class="cast-away-margin alert alert-md alert-success"></div>')
                    .text(data['message']);
            $('#resendRet').empty().append(msg);
        }
        else if(data['state']==='FAILURE'){
            var msg = $('<div class="cast-away-margin alert alert-md alert-danger"></div>')
                    .text(data['message']);
            $('#resendRet').empty().append(msg);
        }
        else{
            setTimeout(function(){
               updateEmailStatus(statusUrl)
            }, 3000);
        }
    });
}

$(document).ready(function(){
    $("#resendConfirmation").click(function(){
        $.ajax({
            type: 'GET',
            url:'/auth/confirm',
            success: function(data, status, request){
               var statusUrl = request.getResponseHeader('Location');
                updateEmailStatus(statusUrl);
            },
            error: function(){alert('未知错误');}
        });
        return false;
    });
});


function generate_thumbnail(){
	$('.content').each(function(){
		var that = this;
		if(that.offsetHeight > 118){
			//create fold btn
			var fold = $('<a class="pull-right"></a>').html('<i class = "icon-resize-small"></i> <strong>收起<strong>').attr('href', '#' + $(that).parent().find('a:first').name);
			fold.click(function(){
				$(that).addClass('hidden').parent().find('.alternative').removeClass('hidden');
			});
			$(this).append(fold).addClass('hidden');
			//create 'div.alternative' which is a thumbnail version of 'div.content'
			var alternative = $('<div class="alternative clearfix"></div>');
			var firstImg = $(this).find('img:first');
			if(firstImg && (firstImg.attr('width') != 200 || firstImg.attr('height') != 112)){
				alternative.append($('<img class="img-inline">').attr('src', firstImg.attr('src')));
			}
			alternative.append(subStringByBytes($(that).text().replace(/\s+/g,' ')) + '...').append($('<a> 展开全部</a>').click(function(){
				//show 'div.content' then hide 'div.alternative'
				$(that).removeClass('hidden').parent().find('.alternative').addClass('hidden');
			}));
			$(this).parent().append(alternative);
		}
	});
}

function like_function(){
    $('.btn-like').each(function(){
        var that = this;
        that.onclick = function(){
            like(this);
            return false;
        };
    });
}

function like(domItem){
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function(){
        if(4 === xhr.readyState){
            if(200 === xhr.status) {
                //if(xhr.responseText.match(/^\{(.+:.+,*)+\}$/)){ //json response
                    var icon = domItem.childNodes[1];
                    var cnt = domItem.getElementsByTagName('div')[0];
                    var jsonRsp = JSON.parse(xhr.responseText);
                    if (false === jsonRsp['liking']) {
                        icon.setAttribute('class', 'icon-heart-empty');
                        cnt.innerHTML = jsonRsp['cnt'];
                    }
                    else {
                        icon.setAttribute('class', 'icon-heart');
                        cnt.innerHTML = jsonRsp['cnt'];
                    }
                //}
                //else
                //{
                //    var resp = $('<div></div>').text(xhr.responseText);
                //    $('#confirmationMoadl').append(resp).modal();
                //}
            }
            else if(403 === xhr.status){
                $('#confirmationMoadl').modal();
            }
            else if(401 === xhr.status){
                window.location.pathname='/auth/login';
            }
        }
    };
    xhr.open("get", domItem.href, true);
    xhr.send();
}


$(document).ready(function(){
    generate_thumbnail();
    like_function();
});