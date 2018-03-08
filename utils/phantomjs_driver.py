from selenium import webdriver
from config.config import MIRROR_PROXY

def phantomjs_driver(loadImages=False, diskCache=True, ignoreSslErrors=True, proxy={}):
    service_args=[]
    service_args.append('--load-images=' + ('true' if loadImages else 'false'))
    service_args.append('--disk-cache=' + ('true' if diskCache else 'false'))
    service_args.append('--ignore-ssl-errors=' + ('true' if ignoreSslErrors else 'false'))
    if proxy:
        service_args.append('--ignore-ssl-errors=' + ('true' if ignoreSslErrors else 'false'))
    driver = webdriver.PhantomJS("/usr/bin/phantomjs", service_args=service_args)
    #driver.implicitly_wait(10)        #设置超时时间
    #driver.set_page_load_timeout(10)  #设置超时时间
    return driver

def phantomjs_driver_mirror(loadImages=True, diskCache=True, ignoreSslErrors=True, useProxy=True):
    proxy = 'http://%s' % MIRROR_PROXY
    service_args=[]
    service_args.append('--load-images=' + ('true' if loadImages else 'false'))
    service_args.append('--disk-cache=' + ('true' if diskCache else 'false'))
    service_args.append('--ignore-ssl-errors=' + ('true' if ignoreSslErrors else 'false'))
    service_args.append('--ignore-ssl-errors=' + ('true' if ignoreSslErrors else 'false'))
    if useProxy:
        service_args.append('--proxy=' + proxy)
    driver = webdriver.PhantomJS("/usr/bin/phantomjs", service_args=service_args)
    driver.implicitly_wait(10)        #设置超时时间
    driver.set_page_load_timeout(10)  #设置超时时间
    return driver

jsDriver = phantomjs_driver()

mirrorJsDriver = phantomjs_driver_mirror()

