/**
 * Created by axl on 16/8/9.
 */
'use strict';

/*
* popover details when hover '.tag' element
* note that some popover data content is get via ajax
*
* */
$(document).ready(function(){
    $("a.tag[href!='#']").popover({
            template: '<div class="popover col-xs-4" role="tooltip"><div class="arrow"></div><h3 class="popover-title"></h3><div class="popover-content"></div></div>',
            html: true,
            trigger: "hover",
            placement: "auto top",
            title: function(){return $(this).html();},
            content: '<div class="tag-intro">加载中...</div><div class="tag-operation">加载中...</div>',
            container: 'body',
            delay: {hide: 1000, show: 1500 }
        }).on('shown.bs.popover', function (event) {
            var that = this;
            $('div.popover').on('mouseenter', function () {
                $(that).attr('in', true);
            }).on('mouseleave', function () {
                $(that).removeAttr('in');
                $(that).popover('hide');
            });
            $.getJSON(that.href, function(data){
                $('.tag-intro').text(data['intro']);
                $('.tag-operation').empty().append($('<a>查看</a>').attr('href', that.href))
                        .append($('<span class="text-muted pull-right"><span>').text('文章数 ').append($('<strong></strong>').text(data['postsCnt'])));
            });
        }).on('hide.bs.popover', function (event) {
            if ($(this).attr('in')) {
                event.preventDefault();
            }
        });
});
