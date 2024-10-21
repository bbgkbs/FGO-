# 导入需要的库
import time
import os
import cv2
import gc
import re
import numpy as np

# 各种变量
adb_tool_pth = "./adb_tool/platform-tools"
ip = "127.0.0.1"
port = 16384
w_w = 1600
w_h = 900
temp = 'resources/system/temp.png'

# 一级函数
def tap(x, y, time_interval=0.5):
    os.system(f"adb shell input tap {x} {y}")
    time.sleep(time_interval)

def swipe(x1, y1, x2, y2, duration=500, time_interval=0.5):
    os.system(f"adb shell input swipe {x1} {y1} {x2} {y2} {duration}")
    time.sleep(time_interval)

def screen_shot(x1=0, x2=w_w, y1=0, y2=w_h, usage_name="temp"):
    img_pth = f"resources/system/{usage_name}.png"
    os.system(f"adb shell screencap -p > {img_pth}")
    convert_img(img_pth)
    img = cv2.imread(img_pth)
    img = img[y1:y2, x1:x2]
    cv2.imwrite(img_pth, img)

def convert_img(path):
    # adb截图后和windows默认的换行符不符，需要额外处理
    with open(path, "br") as f:
        bys = f.read()
        bys_ = bys.replace(b"\r\n",b"\n")
    with open(path, "bw") as f:
        f.write(bys_)

def compare_img(x1, x2, y1, y2, compare_img, min=0.9):
    '''
    x1, x2, y1, y2: 截图区域
    compare_img:    需要对比的图片
    '''
    screen_shot(x1, x2, y1, y2)
    compare_img = cv2.cvtColor(compare_img, cv2.COLOR_BGR2GRAY)
    target_img = cv2.imread(temp)
    target_img = cv2.resize(target_img, (compare_img.shape[1], compare_img.shape[0]))
    compare_img = cv2.calcHist([compare_img], [0], None, [256], [0, 256])
    compare_img = cv2.normalize(compare_img, compare_img, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
    target_img = cv2.cvtColor(target_img, cv2.COLOR_BGR2GRAY)
    target_img = cv2.calcHist([target_img], [0], None, [256], [0, 256])
    target_img = cv2.normalize(target_img, target_img, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
    
    result = cv2.compareHist(target_img, compare_img, cv2.HISTCMP_CORREL)
    os.remove("resources/system/temp.png")
    return result >= min

def locate_img(compare_img, min=0.9, return_str='匹配成功'):
    # 通过opencv的matchTemolate定位图片位置
    screen_shot()
    background = cv2.imread("resources/system/temp.png")
    if compare_img is None:
        print(f"Error: '{compare_img}'图片不存在")
        return
    result = cv2.matchTemplate(compare_img, background, cv2.TM_CCOEFF_NORMED)
    loc = np.where(result >= min)
    if(len(loc[0]) > 0):
        os.remove("resources/system/temp.png")
        print(return_str)
        tap(int(np.mean(loc[1])+compare_img.shape[1]/2), int(np.mean(loc[0])+compare_img.shape[0]/2))
        return True
    else:
        return False

# 二级函数，被调用的
def connect():
    adb_pth = os.path.abspath(adb_tool_pth)
    os.environ["Path"] += f";{adb_pth}"
    os.system(f"adb connect {ip}:{port}")
    devices_output = os.popen("adb devices").read()
    if "device" in devices_output:
        print("连接成功，设备在线")
    else:
        print("未能连接到设备，请确认设备已开启")

def load_file(pth):
    memory = {}
    for file in os.listdir(pth):
        file_path = os.path.join(pth, file)
        if os.path.isfile(file_path) and file.endswith('.png'):
            memory[str(file).split('.')[0]] = cv2.imread(file_path)
    return memory

def choose_support(servant_type):
    '''
    servant_type: 助战从者的职介，从左往右
    '''
    global support_collection

    tap(115+84*(servant_type-1), 162)
    time.sleep(0.5)
    count = 0           # 滑了三次没找到就刷新
    while True:
        if(count == 3):
            tap(1157, 158)
            tap(1057, 711)
            count = 0
            time.sleep(5)
        for i in support_collection.values():
            if locate_img(i, return_str='找到助战了'): return
        swipe(20, 700, 20, 140, 1500)
        count += 1

def wait(Time=20, x1=1462, x2=1524, y1=222, y2=290, end=False):
    global system_flag
    time.sleep(Time)
    if not end:  
        flag = compare_img(x1, x2, y1, y2, system_flag['battle_flag'])
        while not flag:
            flag = compare_img(x1, x2, y1, y2, system_flag['battle_flag'])
            tap(800, 450)
            time.sleep(0.25)

def use_skill(servant, skill, target=None, special2=None, special3=None):
    tap(94 + 111*(skill-1) + 396*(servant-1), 740, 0.25)
    if target is not None:
        tap(400 + (target-1)*402, 536, 0.25)
    if special2 is not None:
        #类似宇宙凛的技能
        pass
    if special3 is not None:
        #类似大姐姐的技能
        pass
    tap(94+111*(skill-1)+396*(servant-1), 740, 0.25)
    wait(Time=1.5)

def use_NP(servant1, servant2=None, servant3=None, end=False):
    tap(1429, 774, 0.75)
    tap(519 + (servant1-1) * 287, 283, 0.25)
    if servant2 is not None:
        tap(519 + (servant1-1) * 287, 283, 0.25)
    if servant3 is not None:
        tap(519 + (servant1-1) * 287, 283, 0.25)
    tap(117, 709, time_interval=0.25)
    tap(486, 709)
    if end:
        pass
    else:
        wait()

def master_skill(skill, target=None, special1=None, special2=None):
    '''
    skill:              技能
    target:             释放目标(可选)
    special1, special2: 从者换位
    '''
    tap(1493, 430)
    tap(1140 + (skill-1)*111, 410)
    if target is not None:
        tap(400 + (target-1)*402, 536, 0.25)
    if special1 is not None:
        tap(189+(special1-1)*231, 496, 0.25)
        tap(189+(special2-1)*231, 496, 0.25)
        tap(800, 829, 0.75)
    tap(1140 + (skill-1)*111, 410)
    wait(Time=1)

def continue_battle():
    global system_flag
    flag = True
    while flag:
        if compare_img(934, 1152, 681, 731, system_flag['continue']):
            flag = False
            tap(1034, 717)
            time.sleep(5)
        elif compare_img(546, 1050, 42, 118, system_flag['low_power']): #用补充体力时的标题来当定位
            flag = False
            print("体力不足")
        else: 
            tap(1358, 801)
            time.sleep(0.5)

def start(first_time=False):
    global system_flag
    if first_time:
        compare_img(841, 942, 823, 873, system_flag['start_flag'])
        time.sleep(1)
        tap(1488, 845)

# 测试
def start_battle(List):
    for action in List:
        command, *args = action
        if command == 'skill':
            use_skill(*args)
        elif command == 'NP':
            use_NP(*args)
        elif command == 'master':
            if len(args) == 1:
                master_skill(*args)
            elif len(i) == 2:
                master_skill(args[0], target=args[1])
            elif len(i) == 3:
                master_skill(args[0], special1=args[1], special2=args[2])

order_list = [['skill', 1, 1],
              ['skill', 1, 3], 
              ['skill', 2, 3, 1],
              ['skill', 3, 3, 1],
              ['NP', 1],

              ['skill', 2, 1],
              ['skill', 2, 2, 1],
              ['skill', 3, 2, 1],
              ['NP', 1],

              ['skill', 3, 1],
              ['master', 3, 3, 5],
              ['master', 1],
              ['skill', 3, 1, 1],
              ['skill', 3, 2],
              ['skill', 3, 3],
              ['NP', 1]]

if __name__ == "__main__":
    connect()
    system_flag = load_file('./resources/system')
    support_collection = load_file('./resources/system/support')
    if system_flag and support_collection:
        print("资源加载成功")
    else:
        print("资源加载失败")
        exit()
    i = 0
    result = input("开始？(y/n)")
    if result == "y":
        #while i < 10:
            #choose_support(6)
            # if(i == 0):
            #     start(True)
            wait(1)
            start_battle(order_list)
            continue_battle()
            gc.collect()
            i += 1
            print(f"第{i}次结束")
            exit()
    result = input("是否继续？(y/n)")

