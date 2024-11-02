import cv2
import os
import numpy as np
from collections import deque
import time
import heapq

adb_tool_pth = "./adb_tool/platform-tools"
python_pth = "./python"
ip = "127.0.0.1"
port = 16384
w_w = 1600
w_h = 900
temp = 'resources/system/temp.png'

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

class TreeNode(object):
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def kthLargestLevelSum(root, k):
    if not root:
        return -1
    level_sums = []
    queue = deque([root])
    while queue:
        level_sum = 0
        for _ in range(len(queue)):
            node = queue.popleft()
            level_sum += node.val
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        level_sums.append(level_sum)
    if len(level_sums) < k:
        return -1
    return heapq.nlargest(k, level_sums)[-1]

def load_file(pth):
    memory = {}
    for file in os.listdir(pth):
        file_path = os.path.join(pth, file)
        if os.path.isfile(file_path) and file.endswith('.png'):
            memory[str(file).split('.')[0]] = cv2.imread(file_path)
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

def continue_battle():
    global system_flag
    flag = True
    while flag:
        if compare_img(392, 541, 147, 670, system_flag['low_power']): #用补充体力时的标题来当定位
            flag = False
            print("体力不足")
            exit()
        elif compare_img(934, 1152, 681, 731, system_flag['continue']):
            flag = False
            time.sleep(5)     
        else: 
            time.sleep(0.5)

def connect():
    adb_pth = os.path.abspath(adb_tool_pth)
    os.environ["Path"] += f";{adb_pth}"
    os.system(f"adb connect {ip}:{port}")

if __name__ == '__main__':
    connect()
    screen_shot(1157, 1436, 842, 880, 'no_wifi')

# 1157, 1436, 842, 880