/**
 * Created by axl on 16/7/9.
 */


'use strict';
$('.content').each(function(){
	var that = this;
	if(that.offsetHeight > 118){
		var fold = $('<a class="pull-right"></a>').html('<i class = "icon-resize-small"></i> <strong>收起<strong>').attr('href', '#' + $(that).parent().find('a:first').name);
		fold.click(function(){
			$(that).addClass('hidden').parent().find('.alternative').removeClass('hidden');
		});
		$(this).append(fold).addClass('hidden');
		var alternative = $('<div class="alternative clearfix"></div>');
		var firstImg = $(this).find('img:first');
        if(firstImg && (firstImg.attr('width') != 200 || firstImg.attr('height') != 112)){
            alternative.append($('<img class="img-inline">').attr('src', firstImg.attr('src')));
    	}
    	alternative.append(subStringByBytes($(that).text().replace(/\s+/g,' ')) + '...').append($('<a> 展开全部</a>').click(function(){
    		$(that).removeClass('hidden').parent().find('.alternative').addClass('hidden');
    	}));
        $(this).parent().append(alternative);
	}
});


