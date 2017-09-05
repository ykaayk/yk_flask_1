/**
 * Created by K_God on 2017/8/31.
 */
// 初始化播放器
$(function () {
    var song_id = $('.song').attr('song-id');
    $('#music-iframe').attr('src', '//music.163.com/outchain/player?type=2&id='+song_id+'&auto=0&height=66')
});

// 点击播放
$(function () {
    $('.song').click(function (event) {
        event.preventDefault();
        var song_id = $(this).attr('song-id')+'';
        var all_src = $('#music-iframe');
        $(this).css('color', '#f44336');
        $(this).siblings().css('color', '#333');
        all_src.attr('src', '//music.163.com/outchain/player?type=2&id='+song_id+'&auto=1&height=66')

    })
});

// 鼠标悬浮颜色
$(function () {
    $('.song').mouseenter(function (event) {
        event.preventDefault();
        $(this).css('background', '#ffc0cb');
        $(this).siblings().css('background', 'transparent')
    });
    $('.song').mouseleave(function (event) {
        event.preventDefault();
        $(this).css('background', 'transparent');
    });

});
