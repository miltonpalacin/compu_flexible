
import fileHelper
import configNormalAgent as config


for file in fileHelper.fileList(config.sf_path):
    print(file)