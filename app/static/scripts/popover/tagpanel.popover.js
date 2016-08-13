'use strict';
$(document).ready(function(){
    $(".tag-panel").load('/tags', function(data, status){
        if(status === "error") {
            alert("未知错误");
        }
        if(status === "success") {
            $("[role='presentation']:first").addClass("active");
            $('[role="tabpanel"]:first').addClass("active");
            $('#input-tags').click(function(){$(this).next().toggle();});
            $('a.tag').click(function(){
                var tag = $(this).text();
                $('#input-tags').val(function(index, oldvalue){
                    var tagArry = oldvalue.split(';');
                    if(tagArry.length >= 6 || (-1 != $.inArray(tag, tagArry))){
                        return oldvalue;
                    }
                    return oldvalue + tag + ';' ;
                });
                return false;
            });
        }
    });
});