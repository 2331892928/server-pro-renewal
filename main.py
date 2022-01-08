import os

import requests
import time
from PIL import Image
from hashlib import md5

'''
-----------------------配置文件
'''

cjyuser = 'AMEN12138'  # 超级鹰账户 www.chaojiying.com
cjypass = 'ljf147258..'  # 超级鹰密码 www.chaojiying.com
id = '927456'  # 超级鹰软ID   用户中心>>软件ID 生成一个替换 96001
serverid = '21747097'  # 服务器ID
usercookie = 'session=f039fcecf59ac0631ef22bb793b58cfe18889fd8'  # 用户cookie，格式:session=
v = '56' # 用户资料ID，用于查询服务器是否过期
servername = 'ymfwq.mcserv.me'  # 请输入已有的服务器域名
yzmcw = 5  # 验证码错误次数,无限0
tuisong = 'https://api.day.app/L2jvMvYBQCAPQHBdBBGZ9/server.pro签到/{}/?group=server.pro签到'
#BARK推送地址，推送消息用{}


def gb_tp(path):
    i = 1
    j = 1
    img = Image.open(path)  # 读取系统的内照片
    # print(img.size)  # 打印图片大小
    # print(img.getpixel((4, 4)))
    width = img.size[0]  # 长度
    height = img.size[1]  # 宽度
    for i in range(0, width):  # 遍历所有长度的点
        for j in range(0, height):  # 遍历所有宽度的点
            data = (img.getpixel((i, j)))  # 打印该图片的所有点
            # print(data)  # 打印每个像素点的颜色RGBA的值(r,g,b,alpha)
            # print(data[0])  # 打印RGBA的r值
            if (data[0] >= 93 and data[1] >= 94 and data[2] >= 95):  # RGBA的r值大于170，并且g值大于170,并且b值大于170
                img.putpixel((i, j), (0, 0, 0, 255))  # 则这些像素点的颜色改成大红色
    img = img.convert("RGB")  # 把图片强制转成RGB
    img.save(path)  # 保存修改像素点后的图片


def hd(path):
    image = Image.open(path)
    imgry = image.convert('L')
    table = get_bin_table()
    binary = imgry.point(table, '1')
    noise_point_list = collect_noise_point(binary)
    remove_noise_pixel(binary, noise_point_list)
    binary.save(path)


def get_bin_table(threshold=115):
    '''
    获取灰度转二值的映射table
    0表示黑色,1表示白色
    '''
    table = []
    for i in range(256):
        if i < threshold:
            table.append(0)
        else:
            table.append(1)
    return table


def remove_noise_pixel(img, noise_point_list):
    '''根据噪点的位置信息，消除二值图片的黑点噪声'''
    for item in noise_point_list:
        img.putpixel((item[0], item[1]), 1)


def collect_noise_point(img):
    '''收集所有的噪点'''
    noise_point_list = []
    for x in range(img.width):
        for y in range(img.height):
            res_9 = sum_9_region_new(img, x, y)
            if (0 < res_9 < 3) and img.getpixel((x, y)) == 0:  # 找到孤立点
                pos = (x, y)
                noise_point_list.append(pos)
    return noise_point_list


def sum_9_region_new(img, x, y):
    '''确定噪点 '''
    cur_pixel = img.getpixel((x, y))  # 当前像素点的值
    width = img.width
    height = img.height

    if cur_pixel == 1:  # 如果当前点为白色区域,则不统计邻域值
        return 0

    # 因当前图片的四周都有黑点，所以周围的黑点可以去除
    if y < 3:  # 本例中，前两行的黑点都可以去除
        return 1
    elif y > height - 3:  # 最下面两行
        return 1
    else:  # y不在边界
        if x < 3:  # 前两列
            return 1
        elif x == width - 1:  # 右边非顶点
            return 1
        else:  # 具备9领域条件的
            sum = img.getpixel((x - 1, y - 1)) \
                  + img.getpixel((x - 1, y)) \
                  + img.getpixel((x - 1, y + 1)) \
                  + img.getpixel((x, y - 1)) \
                  + cur_pixel \
                  + img.getpixel((x, y + 1)) \
                  + img.getpixel((x + 1, y - 1)) \
                  + img.getpixel((x + 1, y)) \
                  + img.getpixel((x + 1, y + 1))
            return 9 - sum


def tz(str):
    requests.get(tuisong.format(str))


class Chaojiying_Client(object):

    def __init__(self, username, password, soft_id):
        self.username = username
        password = password.encode('utf8')
        self.password = md5(password).hexdigest()
        self.soft_id = soft_id
        self.base_params = {
            'user': self.username,
            'pass2': self.password,
            'softid': self.soft_id,
        }
        self.headers = {
            'Connection': 'Keep-Alive',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0)',
        }

    def PostPic(self, im, codetype):
        """
        im: 图片字节
        codetype: 题目类型 参考 http://www.chaojiying.com/price.html
        """
        params = {
            'codetype': codetype,
        }
        params.update(self.base_params)
        files = {'userfile': ('ccc.jpg', im)}
        r = requests.post('http://upload.chaojiying.net/Upload/Processing.php', data=params, files=files,
                          headers=self.headers)
        return r.json()

    def ReportError(self, im_id):
        """
        im_id:报错题目的图片ID
        """
        params = {
            'id': im_id,
        }
        params.update(self.base_params)
        r = requests.post('http://upload.chaojiying.net/Upload/ReportError.php', data=params, headers=self.headers)
        return r.json()


class server_pro:
    def __init__(self):
        self.h = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
            "Cookie": usercookie
        }

    def get_yzm(self):  # 获取验证码，放入./yzm.jpg并识别验证码删除.yzm.jpg
        time1 = int(time.time() * 1000)
        image = requests.get("https://server.pro/api/captcha/get?" + str(time1), headers=self.h)
        with open("./yzm.jpg", "wb") as f:
            f.write(image.content)
        gb_tp("./yzm.jpg")  # 提取验证码
        im = open('./yzm.jpg', 'rb').read()  # 本地图片文件路径 来替换 a.jpg 有时WIN系统须要//
        cjyjson = chaojiying.PostPic(im, 1902)
        # cjyjson = {'err_no':0,'pic_str':"1",'pic_id':'1'}
        os.remove('./yzm.jpg')
        print(cjyjson)
        if 'err_no' in cjyjson:
            if cjyjson['err_no'] == 0:
                return {
                    'str': cjyjson['pic_str'],
                    'id': cjyjson['pic_id']
                }
            else:
                if cjyjson['err_no'] == -1005:
                    return {
                        'str': '接口错误',
                        'id': '',
                    }
                else:
                    return {
                        'str': '验证码接口错误',
                        'id': ''
                    }
        else:
            return {
                        'str': '验证码接口错误',
                        'id': ''
                    }

    def sign(self, yzm_str):  # 签到,1没钱，2验证码错误,3打码平台错误,0成功,4签到接口错误，可以重试
        if yzm_str == '接口错误':
            return 1
        if yzm_str == '验证码接口错误':
            return 3
        if len(yzm_str) != 6:
            return 2
        qd = requests.post("https://server.pro/api/server/renew", headers=self.h, data={
            'id': serverid,  # 服务器ID
            'text': yzm_str
        })
        if qd.content.decode() == 'true':
            return 0
        if qd.content.decode() == 'false':
            return 2
        if qd.content.decode() == '':
            return 4

    def server_qy(self, yzm_str):  # 服务器已被到期，启用,0失败2未过期请求错误
        ym = requests.post("https://server.pro/api/queue/enqueue", headers=self.h, data={
            'id': serverid,
            'plan': "free",
            'pack': 'low',
            'name': servername,
            'service': 'mc',
            'typeId': 1015,
            'location': 'ca',
            'price': 0,
            'payment': '',
            'captcha': yzm_str,
            'token': ''
        })
        print(ym.content.decode())
        if ym.content.decode() == '':
            return 2
        if ym.json()['result'] == 'transfer':
            return 1
        else:
            return 0

    def server_status(self):  # 检查服务器是否到期.1没到期，0到期
        ym = requests.post("https://server.pro/api/meta/get", headers=self.h, data={
            'v': v
        })
        if ym.json()['servers'][serverid]['state'] == 'running':
            return 1
        else:
            return 0


# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    chaojiying = Chaojiying_Client(cjyuser, cjypass, id)  # 用户中心>>软件ID 生成一个替换 96001
    server = server_pro()
    cs = yzmcw
    sfgq = False
    if yzmcw <= 0:
        cs = 9999
    for i in range(1, yzmcw):
        if server.server_status() == 0:
            sfgq = True
            for j in range(1, yzmcw):
                ymz = server.get_yzm()
                if ymz['str'] == '接口错误':
                    tz("验证码接口没钱，请及时充值")
                    break
                if ymz['str'] != '验证码接口错误':
                    if server.server_qy(ymz['str']) == 0:
                        print(chaojiying.ReportError(ymz['id']))
                        continue  # 重试启动
                    else:
                        print("服务器已过期，已成功续费")
                        tz("服务器已过期，已成功续费")
                        break
        if sfgq:
            break
        str1 = server.get_yzm()  # 获取验证码
        status = server.sign(str1['str'])
        if status == 1:
            tz("验证码接口没钱，请及时充值")
            print("验证码接口没钱，请及时充值")
            break
        if status == 3:
            tz("打码平台错误")
            print("打码平台错误")
            break
        if status == 2:  # 验证码错误
            tz("验证码错误")
            print("签到验证码错误")
            chaojiying.ReportError(str1['id'])
        if status == 4:  # 签到接口错误，有可能过期
            tz("签到接口错误，有可能过期，恢复中")
            print("签到接口错误，有可能过期，恢复中")
        if status == 0:
            tz("签到成功")
            print("签到成功")
            break
        time.sleep(5)

    # ocr
    # f = open(r'./yzm.jpg', 'rb')  # 二进制方式打开图文件
    # ls_f = str(base64.b64encode(f.read()))  # 读取文件内容，转换为base64编码
    # f.close()
    # ls_f = ls_f[2:]
    # ls_f = ls_f[:-1]
    # ls_f = 'data:image/bmp;base64,' + ls_f
    # ym = requests.post("http://lsqy.xfywz.cn/ocr.php", data={
    #     'str': ls_f,
    #     'foramt': "txt"
    # })
    # print(ym.content.decode())
    # 登录
    # ym = requests.post("https://server.pro/r/user/login", headers=h, data={
    #     'email': '2331892928@qq.com',
    #     'password': 'ljf147258..',
    #     'rememberMe': 'false',
    #     'code': '',
    #     'captcha': '',
    #     'id': '21747097',
    # })
    # print(ym.content.decode())

# 访问 https://www.jetbrains.com/help/pycharm/ 获取 PyCharm 帮助
