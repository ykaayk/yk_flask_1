# coding:utf8
from PIL import Image
import urllib
import os
import sys
import flask
import qiniu.config
import random
from qiniu import Auth, put_file, etag


# 图片库更新时，请添加路径
# 路径
now_path = os.path.abspath(os.path.dirname(sys.argv[0]))  # 当前脚本路径
main_path = now_path+'/static/images/abstract'  # abstract路径
# main_path = now_path+'/../static/images/abstract'  # 如果作为主程序使用，此刻abstract的路径
main_pic_path = main_path + '/main-pic'  # 主图片路径
main_path_pic_before = 'F:\\code\\yk\\pic-pick'  # 处理之前的图片
dog_cq_pic_path = main_path_pic_before + '/p-animal/dog-cq/before'  # 柴犬图片路径
dog_cq_pic_path_after = main_path + '/p-animal/dog-cq/after'  # 柴犬图片处理之后路径
dog_pic_path = main_path_pic_before + '/p-animal/dog/before'  # 狗图片路径
dog_pic_path_after = main_path + '/p-animal/dog/after'  # 狗图片处理之后路径
meinv_js_pic_path = main_path_pic_before + '/p-meinv/meinv-jianshen/before'  # 健身美女图片路径
meinv_js_pic_path_after = main_path + '/p-meinv/meinv-jianshen/after'  # 健身美女图片处理之后路径
meinv_pic_path = main_path_pic_before + '/p-meinv/meinv/before'  # 美女图片路径
meinv_pic_path_after = main_path + '/p-meinv/meinv/after'  # 美女图片处理之后路径
football_pic_path = main_path_pic_before + '/p-sport/p-football/p-before'  # 足球图片路径
football_pic_path_after = main_path + '/p-sport/p-football/after'  # 足球图片处理之后路径
# 所有拼图路径
all_pic_path = []
for path in [(dog_cq_pic_path, dog_cq_pic_path_after), (dog_pic_path, dog_pic_path_after),
             (meinv_js_pic_path, meinv_js_pic_path_after), (meinv_pic_path, meinv_pic_path_after),
             (football_pic_path, football_pic_path_after)]:
    all_pic_path.append(path)
# 所有处理后拼图路径
all_pic_path_after = []
for path in all_pic_path:
    all_pic_path_after.append(path[1])

# 初始缩略图尺寸
# t_size = [(20, 20)]
# t_size = (10, 10)
# t_size = (40, 40)
# t_size = (30, 30)
base_t_size_list = [(10, 10), (20, 20), (30, 30), (40, 40)]
t_size_list = [(30, 30), (40, 40)]
# t_size_list = [(10, 10)]
# t_size_list = [(20, 20)]
# t_size_list = [(5, 5)]
# t_size_list = [(10, 10), (20, 20), (30, 30), (40, 40)]


# 原图, 测试不同尺寸下拼接图片的效果
# 缩略/扩大为不同尺寸
def change_hyr_size(hyr):
    os.chdir(main_pic_path)  # 改变路径
    # for i in [0.8, 0.5, 0.4, 0.3, 0.2, 0.1]:
    #     pic = Image.open(hyr)
    #     x = int(pic.size[0] * i)
    #     y = int(pic.size[1] * i)
    #     pic.thumbnail((x, y))
    #     pic.save(str(x) + '-' + str(y) + '-' + hyr)
    for i in [1, 1.5, 2, 4, 5]:
        pic = Image.open(hyr)
        x = int(pic.size[0] * i)
        y = int(pic.size[1] * i)
        new_pic = pic.resize((x, y), Image.ANTIALIAS)
        new_pic.save(str(x) + '-' + str(y) + '-' + hyr)


# 修改拼接图片,参数：原始拼图路径， 拼图处理后保存路径，初始缩略图尺寸，缩略放大倍数，默认分析像素间隔
def change_img(img_path_before, img_path_after, thumbnail_size, chang_multiple=1, default_px=2):
    # 读取路径中的文件
    imgs = os.listdir(img_path_before)
    # 打开每个图片，依次分析处理
    for img in imgs:
        os.chdir(img_path_before)
        image = Image.open(img)
        if image.mode != 'RGB':
            continue
        width, height = image.size
        # 改为正方形
        if width == height:
            img_t = image
        elif width > height:
            left = (width-height)/2
            up = 0
            right = left+height
            down = height
            box = (left, up, right, down)
            img_t = image.crop(box)
        elif width < height:
            left = 0
            up = (height-width)/2
            right = width
            down = up+width
            box = (left, up, right, down)
            img_t = image.crop(box)
        # 缩略图
        real_thumbnail_size = (thumbnail_size[0] * chang_multiple, thumbnail_size[1] * chang_multiple)  # 最终缩略图尺寸
        img_t.thumbnail(real_thumbnail_size)
        # 分析主RGB值，默认2px/次
        r, g, b, w_px, h_px = [], [], [], 0, 0  # 初始化
        # 依次遍历像素点，得到RGB值，最后求平均值
        n = 0  # 像素点数量
        while h_px < real_thumbnail_size[1]:
            while w_px < real_thumbnail_size[0]:
                point = (w_px, h_px)
                pixel = img_t.getpixel(point)
                r.append(pixel[0])
                g.append(pixel[1])
                b.append(pixel[2])
                w_px += default_px
                n += 1
            h_px += default_px
            w_px = 0
        average_rgb = rgb_average((r, g, b), n)
        # 根据rgb值保存图片
        img_suffix = img.split('.')[-1]  # 图片后缀
        img_type = img_path_after.split('/')[-2]
        img_name = str(average_rgb[0])+'-'+str(average_rgb[1])+'-'+str(average_rgb[2])+'-'+img_type+'.'+img_suffix
        last_save_img_path = img_path_after + '/' + str(thumbnail_size[0])+'-'+str(thumbnail_size[1])
        if not os.path.exists(last_save_img_path):
            os.makedirs(last_save_img_path)
        os.chdir(last_save_img_path)  # 修改路径
        img_t.save(img_name)


# 求图片平均值
def rgb_average(rgb, n):
    new_rgb = []
    m = int(n * 0.1)
    if m == 0:
        m = 1
    for i in rgb:
        i.sort()
        sum_i = 0
        for num in i[m:-m]:
            sum_i += num
        new_rgb.append(sum_i/(n-2*m))
    return tuple(new_rgb)


# 主图片分析，参数：图片名，处理后小拼图的路径的集合，初始缩略图尺寸
def main_img_2(img_f, pic_path_after_list, thumbnail_size_list):
    os.chdir(main_pic_path)
    img = Image.open(img_f)
    width, height = img.size
    o_width, o_height = width, height
    # 判断是否需要将img的尺寸扩大
    if max(img.size) < 24*thumbnail_size_list[-1][0]:
        if width >= height:
            width = 24*thumbnail_size_list[-1][0]
            height = height*24*thumbnail_size_list[-1][0]/img.size[1]
        else:
            height = 24*thumbnail_size_list[-1][0]
            width = width*24*thumbnail_size_list[-1][0]/img.size[1]
        img = img.resize((width, height), Image.ANTIALIAS)

    # 根据thumbnail_size_list的数值依次拼图
    for thumbnail_size in thumbnail_size_list:
        w_px, h_px = 0, 0
        new_img_size = []

        # 确定最终拼图的总尺寸
        if width % thumbnail_size[0] == 0:
            new_img_size.append(width)
        else:
            new_img_size.append((width/thumbnail_size[0]+1)*thumbnail_size[0])
        if height % thumbnail_size[1] == 0:
            new_img_size.append(height)
        else:
            new_img_size.append((height/thumbnail_size[1]+1)*thumbnail_size[1])
        new_img = Image.new('RGB', tuple(new_img_size))

        while h_px < height:
            w_px = 0
            while w_px < width:
                point = (w_px, h_px)
                pixel = img.getpixel(point)
                img_pic, last_pic_path = choice_img(pixel, pic_path_after_list, thumbnail_size)  # 获取相应拼图
                # print point, pixel, img_pic, last_pic_path
                os.chdir(last_pic_path)  # 小拼图的路径
                new_img.paste(Image.open(img_pic), point)  # 贴图
                w_px += thumbnail_size[0]  # 像素点自增长
            h_px += thumbnail_size[1]  # 像素点自增长
        new_img_name = img_f
        last_main_pic_path = main_pic_path + '/' + str(thumbnail_size[0]) + '-' + str(thumbnail_size[1])
        if not os.path.exists(last_main_pic_path):
            os.mkdir(last_main_pic_path)
        os.chdir(last_main_pic_path)
        new_new_img = new_img.resize((o_width, o_height), Image.ANTIALIAS)
        # if o_width != width:
        #     new_img.save('original-'+new_img_name)
        new_new_img.save(new_img_name)


# 主图片选拼图，参数：像素点RGB值，处理后的拼图路径列表
def choice_img(pixel, pic_path_after_list, thumbnail_size):
    # RGB值
    r = pixel[0]
    g = pixel[1]
    b = pixel[2]
    rgb_img_list = []  # 存储RGB值，文件名，路径
    for path_after in pic_path_after_list:  # 所有路径
        path_after = path_after + '/' + str(thumbnail_size[0])+'-'+str(thumbnail_size[1])
        if not os.path.exists(path_after):
            os.mkdir(path_after)
        files = os.listdir(path_after)
        for file in files:
            img_r = int(file.split('-')[0])
            img_g = int(file.split('-')[1])
            img_b = int(file.split('-')[2])
            abs_r = abs(r - img_r)
            abs_g = abs(g - img_g)
            abs_b = abs(b - img_b)
            rgb_img_list.append((abs_r, abs_g, abs_b, file, path_after))
        for n in rgb_img_list:
            if n[0] == 0 and n[1] == 0 and n[2] == 0:
                return n[3], n[4]

        for n in rgb_img_list:
            if (n[0] == 0 or n[0] <= 10) \
                    and (n[1] == 0 or n[1] <= 10) \
                    and (n[2] == 0 or n[2] <= 10):
                return n[3], n[4]
        for n in rgb_img_list:
            if (n[0] == 0 or n[0] <= 10 or n[0] <= 20) \
                    and (n[1] == 0 or n[1] <= 10 or n[1] <= 20) \
                    and (n[2] == 0 or n[2] <= 10 or n[2] <= 20):
                return n[3], n[4]
        for n in rgb_img_list:
            if (n[0] == 0 or n[0] <= 10 or n[0] <= 20 or n[0] <= 30) \
                    and (n[1] == 0 or n[1] <= 10 or n[1] <= 20 or n[1] <= 30) \
                    and (n[2] == 0 or n[2] <= 10 or n[2] <= 20 or n[2] <= 30):
                return n[3], n[4]
        for n in rgb_img_list:
            if (n[0] == 0 or n[0] <= 10 or n[0] <= 20 or n[0] <= 30 or n[0] <= 40) \
                    and (n[1] == 0 or n[1] <= 10 or n[1] <= 20 or n[1] <= 30 or n[1] <= 40) \
                    and (n[2] == 0 or n[2] <= 10 or n[2] <= 20 or n[2] <= 30 or n[2] <= 40):
                return n[3], n[4]
        for n in rgb_img_list:
            if (n[0] == 0 or n[0] <= 10 or n[0] <= 20 or n[0] <= 30 or n[0] <= 40 or n[0] <= 50) \
                    and (n[1] == 0 or n[1] <= 10 or n[1] <= 20 or n[1] <= 30 or n[1] <= 40 or n[1] <= 50) \
                    and (n[2] == 0 or n[2] <= 10 or n[2] <= 20 or n[2] <= 30 or n[2] <= 40 or n[2] <= 50):
                return n[3], n[4]
    return rgb_img_list[-1][3], rgb_img_list[-1][4]


# 最终照片抽象化，参数：图片url，拼图type，拼图尺寸
# 照片处理后保存在七牛
def img_abstract(img_url, img_type, tt_size):
    name = ''
    # if flask.g.front_user:
    #     img_name = str(flask.g.front_user.id)+'-'+name+'-pic.jpg'
    # else:
    if img_type == '0':
        last_path = all_pic_path_after
    else:
        last_path = all_pic_path_after[img_type: img_type + 1]
    for i in random.sample('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890', 10):
        name += i
    img_name = 'nobody-' + name + '-pic.jpg'
    if tt_size == '0':
        ttt_size = [(20, 20)]
    else:
        ttt_size = [(40, 40)]
    urllib.urlretrieve(img_url, main_pic_path+'/'+img_name)
    main_img_2(img_name, last_path, ttt_size)
    os.remove(main_pic_path + '/' + img_name)
    last_main_pic_path = main_pic_path + '/' + str(ttt_size[0][0]) + '-' + str(ttt_size[0][1])
    last_url_img = qi_niu(img_name, last_main_pic_path)
    os.remove(last_main_pic_path+'/'+img_name)
    return last_url_img


# 七牛上传
def qi_niu(img_name, a_path):
    base_url = 'ouiyg2uq4.bkt.clouddn.com'
    # 需要填写你的 Access Key 和 Secret Key
    access_key = 'WjMGUpHwwns7bh5t8Loj-TZiPyYyxe15e5w-hXZf'
    secret_key = 'U-1Wp8BkeWl4HXXVXszisjMMwlMFbFLqjyO-JoHf'
    # 需要填写你的 Access Key 和 Secret Key
    q = Auth(access_key, secret_key)
    # 要上传的空间
    # bucket_name = 'ouiyg2uq4.bkt.clouddn.com'
    bucket_name = 'img-abstract'
    # 上传到七牛后保存的文件名
    key = img_name
    # 生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, key, 3600)
    localfile = a_path + '/' + img_name
    # localfile = './static/images/abstract/main-pic/'+a_path[-5:]+'/'+img_name
    ret, info = put_file(token, key, localfile)
    # print(info)
    assert ret['key'] == key
    assert ret['hash'] == etag(localfile)
    return 'http://'+base_url+'/'+key


if __name__ == '__main__':
    # if '384-240-zjl-6.jpg' not in os.listdir(main_pic_path):
    #     # 先修改图片分辨率
    #     change_hyr_size('p-173.jpg')
    #     print '主图片分辨率修改完毕'
    for path in all_pic_path:
        before_path = path[0]
        after_path = path[1]
        name = path[0].split('/')[-2]
        # last_path = after_path + '\\' + str(t_size[0]) + '-' + str(t_size[1])  # 最终处理后的路径
        if not os.path.exists(after_path):
            # 修改拼接图片
            print name, '拼图分析中...'
            # 根据t_size调整路径
            for t_size in base_t_size_list:
                change_img(before_path, after_path, t_size)
            print name, '拼图分析完毕'

    # 柴犬拼图
    # print '主图片分析中...'
    # main-pic目录下的主图片
    # os.chdir(main_pic_path)
    # for img in os.listdir(main_pic_path):
    #     if os.path.isfile(os.path.join(main_pic_path, img)):
    #         print img, '处理中...'
    #         main_img_2(img, all_pic_path_after, t_size_list)
    #         # main_img_2(img, all_pic_path_after[2:3], t_size_list)
    #         print img, '处理完毕...'

    # print '所有主图片拼图完成'
