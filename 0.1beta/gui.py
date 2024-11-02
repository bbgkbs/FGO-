'''
GUI代码部分，内容如下：
1. 通过文件目录下的json文件夹逐个获取内容数据
2. 将每个从者按钮顶上的列表用json的'name'对应的str字符串填充、
3. 从者按钮的背景随着列表选择变化而变化
4. 按下'设置开始'按钮后进入选择模式，同时原按钮文本变为'下一回合'，然后变为'设置结束'
5. 通过按下不同的从者按钮得到一个order_list的python列表
6. 选择模式下下拉列表禁用，其他不相关按钮也禁用
7. 助战暂时还没有想好，这个部分随机性太强了(悲)
8. 因为上一步，连续刷本就变得困难起来了，反而使用金苹果续体力还轻松一点
9. 之后可以添加礼装系统，虽然可能UI布局会麻烦一点但是搞得定
10. 后续打算放个下拉列表，通过端口列表获取模拟器端口，而不是直接内置默认参数
11. 突然想起来有像宇宙凛那样的特殊二次选项，或者外星大姐头超长按键时长，难顶(悲)
12. 又突然想起来可能需要多线程来紧急暂停当前行动耶
13. 可以通过输出json文件达到缓存选择的效果，然后在读取，暂定在system文件夹下
'''

# 初始化各种乱七八糟的东西
from PyQt5 import uic
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QApplication, QTextBrowser, QComboBox
from PyQt5.QtGui import QPixmap, QIcon
import os
import json
from function_collection import *

order_list = []       # 重中之重
order_mode = False    # 选择模式Flag
battle_start = False  # 判断'启动！'按钮是否按下
use_apple = False     # 判断是否使用金苹果

# 各种组件的内部函数
# 遍历json_collection中的文件得到所有从者信息的列表
def get_json_list():
    data_list = []
    for file in os.listdir('resources/json_collection'):
        with open(f'resources/json_collection/{file}', 'r', encoding='utf-8') as f:
            data = json.load(f)
            data_list.append([data['name'], data['skill_1_step'], data['skill_2_step'], data['skill_3_step'], data['img_pth']])
    return data_list

servant_info_list = get_json_list()   # 这个列表包含json_collection的全部从者信息

# 根据当前下拉列表选项改变按钮背景
def change_servant_img(self, index):
    current = getattr(self.ui, f'servant_list{index}').currentText()
    if not order_mode:
        for i in range(len(servant_info_list)):
            if(current == servant_info_list[i][0]):
                img = QPixmap(f"resources/{servant_info_list[i][4]}")
                icon = QIcon(img)
                button = getattr(self.ui, f'servant{index}')
                button.setIcon(icon)
                button.setIconSize(QSize(button.width(), button.height()))
    else:
        for i in range(len(servant_info_list)):
            getattr(self.ui, f'servant_list{i}').setEnabled(False)
        
# 开启选择模式
def start_order_mode(self):
    global order_mode
    order_mode = True
    self.ui.set.setText('下一回合')

# 调用UI.ui文件，创建窗口
class Stats:
    def __init__(self):
        self.ui = uic.loadUi("UI.ui")
        self.ui.show()

        # 配置组件
        # 初始化下拉列表
        for i in range(1, 6):
            getattr(self.ui, f'servant_list{i}').addItems(['请选择从者'])
            for j in range(len(servant_info_list)):
                getattr(self.ui, f'servant_list{i}').addItem(servant_info_list[j][0])

        # 初始化从者和礼装列表
        self.ui.servant_list1.currentIndexChanged.connect(lambda: change_servant_img(self, 1))
        self.ui.servant_list2.currentIndexChanged.connect(lambda: change_servant_img(self, 2))
        self.ui.servant_list3.currentIndexChanged.connect(lambda: change_servant_img(self, 3))
        self.ui.servant_list4.currentIndexChanged.connect(lambda: change_servant_img(self, 4))
        self.ui.servant_list5.currentIndexChanged.connect(lambda: change_servant_img(self, 5))
        '''
        礼装列表设置
        '''

        # 初始化功能按键
        self.ui.set.clicked.connect(lambda: start_battle(order_list))
        '''
        金苹果按钮设置
        作战次数按钮设置
        添加助战素材按钮设置
        (未来)
        下拉端口选择菜单设置
        连接按钮设置

        '''
        

app = QApplication([])
stats = Stats()
stats.ui.show()
app.exec_()
#打包需要的命令：pyinstaller XXX.py --noconsole --hidden-import PySide6.QtXml
#.exe打包完后把.ui和其他窗口相关的资源复制到同目录下(很重要！)
# --noconsole 为不显示命令行窗口，如果需要知道哪里有问题就去掉这个，在运行之后的.exe文件时会显示错误
# --hidden-import 为在导入UI时需要导入的库，因为在QtXml中的导入为__import__
#后买你还可以加上 --icon="path.ico"来为.exe设置图标，图标为.ico文件
#UI方面会和多线程有很多联动(Thread)，要留意

'''

'''
