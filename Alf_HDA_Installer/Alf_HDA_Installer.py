# !usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Alfxian
@software: PyCharm
@file: Alfx_HDA_Installer.py
@time: 2022/8/16 01:10
"""
import os
import sys


Plugin_Name = "Alfx_HDA.json" # 定义json文件名

# json文件内容
js_text = '''
{
    "path": "$Alfx_HDA", 
    "load_package_once": true, 
    
    "env": [
        {
            "Alfx_HDA": "projectPath",
        },
        {
            "HOUDINI_OTLSCAN_PATH": 
            "otlPath$HOUDINI_OTLSCAN_PATH",
        },
        {
            "HOUDINI_TOOLBAR_PATH": 
            "toolbarPath",
        },
        {
            "HOUDINI_MENU_PATH": 
            "menuPath",
        },
    ],
}
'''

# 将自定义HDA库的otl文件夹下所有文件夹路径添加到HOUDINI_OTLSCAN_PATH中
def CreatePackage():

    docPath = os.path.expanduser('~\Documents').replace("\\", "/") + "/houdini19.5/packages/" #TODO: version free
    packagePath = docPath + Plugin_Name
    # 判断路径是否存在，不存在则创建一个
    if not os.path.exists(docPath):
        os.makedirs(docPath)

    # 指定package路径
    plugin_path = os.getcwd().replace("\\", "/")
    
    # hda path
    hdaPath = plugin_path + "/otls"
    folderPath = "$Alfx_HDA/otls;"
    for eachfolder in os.listdir(hdaPath):
        if os.path.isdir(hdaPath + "/" + eachfolder):
            folderPath += "$Alfx_HDA/otls/"+eachfolder +";"

    temp = js_text.replace("projectPath", plugin_path)
    newtxt = temp.replace("otlPath", folderPath)

    # toolbar path
    toolbar = "$Alfx_HDA" + "/toolbar"
    newtxt = newtxt.replace("toolbarPath", toolbar)

    # menu path
    menu = "$Alfx_HDA" 
    newtxt = newtxt.replace("menuPath", menu)


    f = open(packagePath, "w")
    f.write(newtxt)
    f.close()


if __name__ == '__main__':
    CreatePackage()