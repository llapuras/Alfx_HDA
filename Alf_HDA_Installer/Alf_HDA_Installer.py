# !usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Alfxian
@software: PyCharm
@file: Alf_HDA_Installer.py
@time: 2022/8/16 01:10
"""
import os
import sys


Plugin_Name = "Alf_HDA.json"

js_text = '''
{
    "path": "$Alf_HDA", 
    "load_package_once": true, 
    
    "env": [
        {
            "Alf_HDA": "projectPath",
        },
        {
            "HOUDINI_OTLSCAN_PATH": 
            "folderPath$HOUDINI_OTLSCAN_PATH",
        },
    ],
}
'''


def CreatePackage():

    docPath = os.path.expanduser('~\Documents').replace("\\", "/") + "/houdini19.0/packages/" #TODO: version free
    packagePath = docPath + Plugin_Name
    # 判断路径是否存在，不存在则创建一个
    if not os.path.exists(docPath):
        os.makedirs(docPath)

    # 指定package路径
    plugin_path = os.getcwd().replace("\\", "/")
    hdaPath = plugin_path + "/otls"
    folderPath = "$Alf_HDA/otls;"
    for eachfolder in os.listdir(hdaPath):
        if os.path.isdir(hdaPath + "/" + eachfolder):
            folderPath += "$Alf_HDA/otls/"+eachfolder +";"

    temp = js_text.replace("projectPath", plugin_path)

    temp2 = temp.replace("folderPath", folderPath)

    f = open(packagePath, "w")
    f.write(temp2)
    f.close()


if __name__ == '__main__':
    CreatePackage()