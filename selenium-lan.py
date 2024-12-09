import random
import pandas as pd
from tcping import Ping
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By

import logging
from datetime import datetime
import os

def setup_logging():
    # 确保 log 目录存在 日志存放在./se-errorLogs
    log_dir = 'se-errorLogs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    # 下面是log信息格式
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file_path = os.path.join(log_dir, f'se-log-{current_time}.txt')
    logging.basicConfig(filename=log_file_path, level=logging.ERROR,
                        format='%(asctime)s:%(levelname)s: %(message)s')

def Login(username, userpwd):
    
    # wifi版是连252 网线版是连88 这两玩意有冲突我是没想到的
    url = "http://10.0.8.88"
    # 下面这段更改为你自己的chromedriver路径
    chromedriver_bin = r'C:\Program Files\Google\Chrome\Application\chromedriver.exe'
    
    username_xpath = '//*[@id="edit_body"]/div[3]/div[1]/div/div[2]/div[1]/div/form/input[3]'
    userpwd_xpath  = '//*[@id="edit_body"]/div[3]/div[1]/div/div[2]/div[1]/div/form/input[4]'
    loginBtn_xpath = '//*[@id="edit_body"]/div[3]/div[1]/div/div[2]/div[1]/div/form/input[2]'
    
    # 设置无头模式
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.browser_version = 'stable'
    assert options.capabilities['browserVersion'] == 'stable'
    
    service = webdriver.ChromeService(executable_path=chromedriver_bin,service_args=['--disable-build-check'])
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)
    
    # 登录
    try:
        driver.find_element(By.XPATH, username_xpath).send_keys(username)
        driver.find_element(By.XPATH, userpwd_xpath).send_keys(userpwd)
        driver.find_element(By.XPATH, loginBtn_xpath).click()
    except Exception as e:
        logging.error(f"登录出错, {e}")
        driver.quit()
        return f"登录出错,{e}"
    
    driver.implicitly_wait(2)
    
    # 获取成功信息,xpath和classname这两个方法不稳定已经改用css获取
    # textSucc_xpath = '//*[@id="edit_body"]/div[2]/div[2]/form/div'
    # textSucc_class = 'PageTips'
    
    textSucc_css   = '#edit_body > div:nth-child(2) > div.edit_loginBox.ui-resizable-autohide > form > div'
    textfail_xpath = '//*[@id="message"]'
    
    # 查失败
    try:
        error_mes = driver.find_element(By.XPATH, textfail_xpath).text
        logging.error(f"登录失败: \n{error_mes}\n账号: {username}")
        driver.quit()
        return error_mes
    except Exception as e:
        logging.debug(f"未找到错误信息元素: {e}")
        pass
    
    # 查成功
    try:
        succ_mes = driver.find_element(By.CSS_SELECTOR, textSucc_css).text
        logging.info(f"登录成功: {succ_mes}")
        logging.error(f"恢复连接:{succ_mes}账号: {username}")
        driver.quit()
        return succ_mes
    except Exception as e:
        logging.error(f"未知错误: {e}")
        driver.quit()
        return f"未知错误:{e}"

# 获取信息,理论上可以改造为跑暴力破解
def excel_data():
    randomNum = random.randint(0, 3108)
    df = pd.read_excel('pd2.xlsx')
    account = str(df.iloc[randomNum, 1])
    password = str(df.iloc[randomNum, 4])
    print('******************************')
    print("     num:",randomNum)
    print("     account:", account)
    print("     pwd:", password)
    print('******************************')
    return account, password

def is_connected_to_internet():
    try:
        # 尝试访问bing的首页
        response = requests.get('https://cn.bing.com')
        # 如果响应状态码为200，表示成功连接到外网
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.ConnectionError:
        # 如果发生了连接错误，表示没有连接到外网
        return False

def main():
    # 初始化日志
    setup_logging() 
    
    while True:
        if is_connected_to_internet():
            print("已连接到外网")
        else:
            print("断连!,重新连接\n")
            logging.error("断连")
            account,password = excel_data()
            mes = Login(account, password)
            print('=============')
            print(mes)
            print('=============')

if __name__ == "__main__":
    main()