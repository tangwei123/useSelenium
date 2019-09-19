#/Library/Frameworks/Python.framework/Versions/3.6/bin/python3.6
# -*- coding:utf-8 -*-

__author__ = "tangwei"
from PIL import Image
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

from urllib import request
import os, time, ssl, cv2

def elementExists(dri, elementStr):
    try:
        dri.find_element_by_xpath(elementStr)
        return True
    except NoSuchElementException as err:
        return False

def getTracks(distance):#拿到滑动轨迹，模仿人去滑动滑块，先匀加速后匀减速
    #匀变速运动基本公式
    #1、v=v0+at
    #2、s=v0t+%at的平方
    #3、v的平方 - v0的平方 = 2as
    v = 0 #初速度
    t = 0.3 #单位时间为0.2秒来统计轨迹，即0.2秒内的运动位移
    tracks = [] #位移轨迹列表，其中的每一个值都是0.2秒内移动的距离
    current = 0 #当前的位移
    mid = (distance * 3) / 5 #当移动到中间段的时候开始减速
    while current < distance:
        if current < mid:
            a = 2
        else:
            a = -3
        s = v * t + 0.5 * a * (t ** 2) #0.2秒内的位移
        current += s #已经移动的距离
        tracks.append(round(s))
        v = v + a * t #速度已经达到v，那么该速度做为下次的初速度
    return tracks

#打开chromedriver
driver = webdriver.Chrome(executable_path="./chromedriver")


#打开豆瓣首页
driver.get("https://www.douban.com")

#因为selenium不能直接操作iframe里面的内容，所以需要加一步切换，切换到frame中，参数0为，本页面的第一个iframe
driver.switch_to.frame(0)

#打开页面之后 用xpath定位到要点击的地方，模拟点击
driver.find_element_by_xpath("/html/body/div[1]/div[1]/ul[1]/li[2]").click()

#用xpath定位到要输入的地方，模拟输入
driver.find_element_by_xpath('//*[@id="username"]').send_keys("*******")
driver.find_element_by_xpath('//*[@id="password"]').send_keys("*******")

print(driver.get_cookies())
print("登录之后的cookies")
#用xpath定位到登录按钮，模拟点击登录
driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[1]/div[5]/a").click()

time.sleep(2)
driver.switch_to.frame(0)

#如果出现图片滑块验证码，那么需要处理下拖动  首先要按住滑块  然后拖动滑块  最后松开滑块

if elementExists(driver, '//*[@id="slideBkg"]'):#自己写的方法，判断页面中的验证码元素存不存在，如果存在需要后续操作

    print("有滑块验证码，需要处理")

    rollBar = driver.find_element_by_xpath('//*[@id="tcaptcha_drag_thumb"]')#获取到滑块的element
    ActionChains(driver).click_and_hold(on_element=rollBar).perform()#click_and_hold 是指按住   perform执行

    bgImg = driver.find_element_by_xpath('//*[@id="slideBkg"]').get_attribute("src")#获取背景大图的地址，有残缺的
    smImg = driver.find_element_by_xpath('//*[@id="slideBlock"]').get_attribute("src")#获取需要拼上的小图地址
    yImg = bgImg[0:-1] + str(0)#获取需要拼上的原图地址，没有缺口
    print(yImg)

    yImgData = request.urlopen(yImg, context=ssl._create_unverified_context()).read()#读取完整图片的数据
    if not os.path.exists("./yanzhengma"):#创建存放图片的位置
        os.mkdir("./yanzhengma")
    yImgSaveName = "./yanzhengma/"+str(int(time.time()*10000))+".jpg"
    with open(yImgSaveName, "wb") as fd:
        fd.write(yImgData)

    bgImgData = request.urlopen(bgImg, context=ssl._create_unverified_context()).read()#读取远端图片数据
    if not os.path.exists("./yanzhengma"):#创建存放图片的位置
        os.mkdir("./yanzhengma")
    bgImgSaveName = "./yanzhengma/"+str(int(time.time()*10000))+".jpg"
    with open(bgImgSaveName, "wb") as fd:
        fd.write(bgImgData)

    smImgSaveName = "./yanzhengma/"+str(int(time.time()*10000))+".png"
    smImgData = request.urlopen(smImg, context=ssl._create_unverified_context()).read()#保存图片到本地
    with open(smImgSaveName, "wb") as fd:
        fd.write(smImgData)

    # 转化背景图片尺寸
    img_switch = Image.open(yImgSaveName)  # 读取图片
    img_deal = img_switch.resize((280, 158), Image.ANTIALIAS)  # 转化图片
    img_deal = img_deal.convert('RGB')  # 保存为.jpg格式才需要
    newYImgFileName = "./yanzhengma/" + str(int(time.time() * 1000)) + ".jpg"
    print("转换尺寸之后的背景图片名称：", newYImgFileName)
    img_deal.save(newYImgFileName)

    #转化背景图片尺寸
    img_switch = Image.open(bgImgSaveName)  # 读取图片
    img_deal = img_switch.resize((280, 158), Image.ANTIALIAS)  # 转化图片
    img_deal = img_deal.convert('RGB')  # 保存为.jpg格式才需要
    newBgImgFileName = "./yanzhengma/"+str(int(time.time()*1000))+".jpg"
    print("转换尺寸之后的背景图片名称：", newBgImgFileName)
    img_deal.save(newBgImgFileName)
    #转换模块图片尺寸
    img_switch = Image.open(smImgSaveName)  # 读取图片
    img_deal = img_switch.resize((55, 55), Image.ANTIALIAS)  # 转化图片
    newSmImgFileName = "./yanzhengma/" + str(int(time.time() * 1000)) + ".png"
    print("转换尺寸之后的模块图片名称：", newSmImgFileName)
    img_deal.save(newSmImgFileName)

    #获取到残缺位置的坐标
    newBgFileRGB = cv2.imread(newBgImgFileName)
    target_gray = cv2.cvtColor(newBgFileRGB, cv2.COLOR_BGR2GRAY)
    newSmFileRGB = cv2.imread(newSmImgFileName, 0)

    res = cv2.matchTemplate(target_gray, newSmFileRGB, cv2.TM_CCOEFF_NORMED)
    value = cv2.minMaxLoc(res)
    print("位置参数为：", value)

    minPrec = abs(value[0])
    maxPrec = abs(value[1])

    print("最低概率:", minPrec)

    print("最高概率:", maxPrec)

    if minPrec > maxPrec:
        padding = value[2][0]
    else:
        padding = value[3][0]

    print("采用的距离为：", padding)
    leftPadding = padding #这儿是滑块需要移动的距离，因为没有分析图片就大概测量了下，需要去研究图片

    ActionChains(driver).move_to_element_with_offset(to_element=rollBar, xoffset=140, yoffset=0).perform()

    tracksList = getTracks(leftPadding - 140)
    print(tracksList)
    for everyDistance in tracksList:
        ActionChains(driver).move_by_offset(xoffset=everyDistance, yoffset=0).perform()

    time.sleep(0.8)
    ActionChains(driver).release().perform()
    print(driver.get_cookies())
else:
    print(driver.get_cookies())
    print("已经登录")

# driver.close()#关闭浏览器
#driver.page_source()   当driver.get()之后，可以用该方法，拿到页面的源代码数据
#driver.add_cookie()    新增cookie到selenium
#driver.get_cookies()   获取到当前页面的cookies
#WebDriverWait(driver, 10, 0.5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="gt_slider_knob gt_show"]'))) 显示等待 最长等待10秒钟 每隔0.5秒就会就会检测后续元素有没有出现
#driver.find_element_by_xpath().get_attribute("src")    获取到标签之后，获取到标签中的数据
#from selenium.webdriver.support.select import Select     sel = Select(driver.find_element_by_xpath('xxxx'))   sel.select_by_index(0/1/2)   选择下拉框
#jsCode = "var num = 10;alert(num);" driver.execute_script(jsCode)  执行js代码
#jsCode = ""   driver.execute_script(jsCode)  执行下拉滚动条（也是一段js代码，具体的自己去找）

