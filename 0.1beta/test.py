import cv2
import os
import numpy as np

adb_tool_pth = "./adb_tool/platform-tools"
python_pth = "./python"
ip = "127.0.0.1"
port = 16384
w_w = 1600
w_h = 900

def isValid(s):
    """
    :type s: str
    :rtype: bool
    """
    symbol = {')': '(', '}': '{', ']': '['}
    tmp = []
    for i in s:
        if i in symbol:
            top_element = tmp.pop() if tmp else '#'
            if symbol[i] != top_element:
                return False
        else:
            tmp.append(i)
    return not tmp

def longestCommonPrefix(strs):
    if not strs:
        return ""
    prefix = strs[0]
    for s in strs[1:]:
        while s[:len(prefix)] != prefix:
            prefix = prefix[:-1]
            if not prefix:
                return ""
    return prefix

def load_file(pth):
    memory = {}
    for file in os.listdir(pth):
        file_path = os.path.join(pth, file)
        if os.path.isfile(file_path) and file.endswith(('.png', '.jpg', '.jpeg')):
            memory[file] = cv2.imread(file_path)
    return memory

def convert_img(path):
    with open(path, "br") as f:
        bys = f.read()
        bys_ = bys.replace(b"\r\n",b"\n")
    with open(path, "bw") as f:
        f.write(bys_)

def screen_shot(x1, x2, y1, y2, usage_name="temp"):
    img_pth = f"resources/system/{usage_name}.png"
    os.system(f"adb shell screencap -p > {img_pth}")
    convert_img(img_pth)
    img = cv2.imread(img_pth)
    img = img[y1:y2, x1:x2]
    cv2.imwrite(img_pth, img)

def locate_img(target, min=0.9):
    screen_shot(0, w_w, 0, w_h)
    background = cv2.imread("resources/system/temp.png")
    if target is None:
        print(f"Error: 不存在'{target}")
        return
    result = cv2.matchTemplate(target, background, cv2.TM_CCOEFF_NORMED)
    loc = np.where(result >= min)
    if(len(loc[0]) > 0):
        os.remove("resources/system/temp.png")
        print("匹配成功")
        #tap(int(np.mean(loc[1])+target.shape[1]/2), int(np.mean(loc[0])+target.shape[0]/2))
        return True
    else:
        print("匹配失败")
        return False
    
def choose_support(support_collection):
    count = 0
    while True:
        #if(count == 3):
            #tap(1157, 158)
            #tap(1057, 711)
            #count = 0
            #time.sleep(5)
        for i in support_collection.values():
            if locate_img(i): return
        #swipe(20, 700, 20, 140, 1500)
        #count += 1
    
def connect():
    adb_pth = os.path.abspath(adb_tool_pth)
    os.environ["Path"] += f";{adb_pth}"
    os.system(f"adb connect {ip}:{port}")

def tap(x, y, time_interval=0.5):
    os.system(f"adb shell input tap {x} {y}")
    #time.sleep(time_interval)

if __name__ == '__main__':
    connect()
    servant_type = 6
    tap(115+84*(servant_type-1), 162)