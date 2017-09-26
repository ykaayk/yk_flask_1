/**
 * Created by K_God on 2017/9/18.
 */
$(function () {
    setInterval(function () {
        var li_pa = $('.s-f-pa');
        var a_pa = $('.a-select');
        var data_page = li_pa.attr('data-page');
        if (li_pa.attr('data-page') == 5){
            li_pa.removeClass('s-f-pa');
            a_pa.removeClass('a-select');
            $('.f-pa').first().addClass('s-f-pa');
            $('.dots a').first().addClass('a-select');
        }else {
            li_pa.removeClass('s-f-pa');
            a_pa.removeClass('a-select');
            $('.f-pa').filter(function () {
                return parseInt($(this).attr('data-page'))  == (parseInt(data_page)+1)
            }).addClass('s-f-pa');
            $('.dots a').filter(function () {
                return parseInt($(this).attr('data-page')) == (parseInt(data_page)+1)
            }).addClass('a-select');
        }
    }, 5000)
});

$(function () {
    $('.dots a').click(function (event) {
        event.preventDefault();
        var data_page = parseInt($(this).attr('data-page'));
        var li_pa = $('.f-pa');
        var li_s = li_pa.filter(function () {
            return parseInt($(this).attr('data-page')) == data_page
        });
        li_s.addClass('s-f-pa');
        li_s.siblings().removeClass('s-f-pa');
        $(this).siblings().removeClass('a-select');
        $(this).addClass('a-select');
    })
});

