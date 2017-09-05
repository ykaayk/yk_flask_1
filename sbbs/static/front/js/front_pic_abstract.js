/**
 * Created by K_God on 2017/8/11.
 */

// 七牛，用户上传图片
$(function () {
    var domain = 'http://oqwrm9r74.bkt.clouddn.com/';
    var uploader = Qiniu.uploader({
      runtimes: 'html5,flash,html4',      // 上传模式，依次退化
      browse_button: 'abstract-pic',         // 上传选择的点选按钮，必需
      // 在初始化时，uptoken，uptoken_url，uptoken_func三个参数中必须有一个被设置
      // 切如果提供了多个，其优先级为uptoken > uptoken_url > uptoken_func
      // 其中uptoken是直接提供上传凭证，uptoken_url是提供了获取上传凭证的地址，如果需要定制获取uptoken的过程则可以设置uptoken_func
      // uptoken : '<Your upload token>', // uptoken是上传凭证，由其他程序生成
      uptoken_url: '/qiniu_token',         // Ajax请求uptoken的Url，强烈建议设置（服务端提供）
      // uptoken_func: function(){    // 在需要获取uptoken时，该方法会被调用
      //    // do something
      //    return uptoken;
      // },
      get_new_uptoken: false,             // 设置上传文件的时候是否每次都重新获取新的uptoken
      // downtoken_url: '/downtoken',
      // Ajax请求downToken的Url，私有空间时使用，JS-SDK将向该地址POST文件的key和domain，服务端返回的JSON必须包含url字段，url值为该文件的下载地址
      unique_names: true,              // 默认false，key为文件名。若开启该选项，JS-SDK会为每个文件自动生成key（文件名）
      // save_key: true,                  // 默认false。若在服务端生成uptoken的上传策略中指定了sava_key，则开启，SDK在前端将不对key进行任何处理
      domain: domain,     // bucket域名，下载资源时用到，必需
      //container: 'container',             // 上传区域DOM ID，默认是browser_button的父元素
      max_file_size: '100mb',             // 最大文件体积限制
      //flash_swf_url: 'path/of/plupload/Moxie.swf',  //引入flash，相对路径
      max_retries: 3,                     // 上传失败最大重试次数
      dragdrop: true,                     // 开启可拖曳上传
      drop_element: 'abstract-pic',          // 拖曳上传区域元素的ID，拖曳文件或文件夹后可触发上传
      chunk_size: '4mb',                  // 分块上传时，每块的体积
      auto_start: true,                   // 选择文件后自动上传，若关闭需要自己绑定事件触发上传
      filters : {
      	max_file_size : '100mb',
      	prevent_duplicates: true,
       	// Specify what files to browse for
        mime_types: [
        	{title : "Image files", extensions : "jpg,png"} // 限定jpg,gif,png后缀上传
            ]
        },
      multi_selection: false,         //限制上传数量为一个
      //x_vars : {
      //    查看自定义变量
      //    'time' : function(up,file) {
      //        var time = (new Date()).getTime();
                // do something with 'time'
      //        return time;
      //    },
      //    'size' : function(up,file) {
      //        var size = file.size;
                // do something with 'size'
      //        return size;
      //    }
      //},
      init: {
          'FilesAdded': function(up, files) {
              plupload.each(files, function(file) {
                  // 文件添加进队列后，处理相关的事情
                  var abstract_pic = $('#abstract-pic');
                  var abstract_pic_b = $('#abstract-pic-b');
                  abstract_pic.css('display', 'none');
                  abstract_pic_b.css('display', 'block');
              });
          },
          'BeforeUpload': function(up, file) {
                 // 每个文件上传前，处理相关的事情
          },
          'UploadProgress': function(up, file) {
                 // 每个文件上传时，处理相关的事情
          },
          'FileUploaded': function(up, file, info) {
                 // 每个文件上传成功后，处理相关的事情
                 // 其中info是文件上传成功后，服务端返回的json，形式如：
                 // {
                 //    "hash": "Fh8xVqod2MQ1mocfI4S4KpRL6D98",
                 //    "key": "gogopher.jpg"
                 //  }
                 // 查看简单反馈
                 // var domain = up.getOption('domain');
                 // var res = parseJSON(info);
                 // var sourceLink = domain +"/"+ res.key; 获取上传成功后的文件的Url
                var fileUrl = domain + file.target_name;
                var imgTag = $('#show-pic').attr('src', fileUrl).animate({'width': '200px'}, 2000);
                $('#abstract-submit').css('display', 'block').show(1000);
                var abstract_pic = $('#abstract-pic');
                var abstract_pic_b = $('#abstract-pic-b');
                abstract_pic.val('换一张试试 : )');
                abstract_pic.css('display', 'block');
                abstract_pic_b.css('display', 'none');
          },
          'Error': function(up, err, errTip) {
                 //上传出错时，处理相关的事情
          },
          'UploadComplete': function() {
                 //队列文件处理完毕后，处理相关的事情
          },
          'Key': function(up, file) {
              // 若想在前端对每个文件的key进行个性化处理，可以配置该函数
              // 该配置必须要在unique_names: false，save_key: false时才生效

              var key = "";
              // do something with key here
              return key
          }
      }
  });

  // domain为七牛空间对应的域名，选择某个空间后，可通过 空间设置->基本设置->域名设置 查看获取

  // uploader为一个plupload对象，继承了所有plupload的方法
    return uploader;
});

// 选择t-type
$(function () {
    $('.t-type').click(function (event) {
        event.preventDefault();
        var img_type = $('#img-type');
        img_type.html($(this).text()+'<span class="caret"></span>');
        img_type.attr('t-size', $(this).attr('t-size'));
        $('.t-type').css('display', 'block');
        $(this).css('display', 'none');
    })
});

// 上传图片进行处理
$(function () {
    var abstract_submit = $('#abstract-submit');
    abstract_submit.click(function (event) {
        event.preventDefault();
        $(this).css('display', 'none');
        $('#abstract-submit-b').css('display', 'block');
        var img_url = $('#show-pic').attr('src');
        var img_type = $('#img-type').attr('img-type');
        var t_size = 1; // 暂定为0
        xtajax.post({
            'url': '/img_abstract_do/',
            'data':{
                'img_url': img_url,
                'img_type': img_type,
                'tt_size': t_size
            },
            'success': function (data) {
                if(data['code'] == '200'){
                    var pic_after_abstract_url = data['data']['img_url'];
                    $('#abstract-submit-b').css('display', 'none');
                    $('#pic-after-abstract').attr('src', pic_after_abstract_url).animate({'width': '200px'}, 2000);
              }
            }
        })
    })
});

// 点击图片放大缩小
$(function () {
    var show_pic = $('.pic-show');
    show_pic.click(function () {
        if($(this).css('width') == '200px'){
            $(this).animate({'width': '400px'});
        }else if($(this).css('width') == '400px'){
            $(this).animate({'width': '800'});
        }else($(this).animate({'width': '200px'}))
    });
});
