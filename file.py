from croniter import croniter # croniter.croniter
from datetime import datetime
from crontab import CronTab
import fileinput as files # files - elios
import configparser
import logging
import time
import os

pathConfig = "config.ini"

def config_ini():
    config = configparser.ConfigParser()
    config.read(pathConfig)
    return config

def logger_ini():
    config = config_ini()
    logger = logging.getLogger(__name__)
    logger.setLevel(config['LOG']['LEVEL']) # Reading logg's level
    file_handler = logging.FileHandler(os.path.join(os.path.dirname(os.path.realpath(__file__)), config['PATHS']['LOGS']))
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)
    return logger

def reading_tasks():
    config = config_ini()
    with files.input(config['PATHS']['CRONTASKS']) as reading:
        dataArr = [line.split(' ', 5) for line in reading]
    return dataArr

def next_tick(arr):
    temp = []
    index = 0
    while index < len(arr):
        temp.append(croniter(f"{arr[index][0]} {arr[index][1]} {arr[index][2]} {arr[index][3]} {arr[index][4]}", datetime.now()).get_next(datetime))
        index += 1
    return temp

def cron_workflow(mainArr, tempArr, logger):
    index = 0
    while True:
        if(index < len(mainArr)):
            if(datetime.now().replace(microsecond = 0) == tempArr[index]):
                process = os.fork() # Ini a child process
                if process == 0:
                    os.system(mainArr[index][5])
                    logger.info(f"Выполнение задания: {mainArr[index][5]}")
                    break
                else:
                    tempArr[index] = croniter(f"{mainArr[index][0]} {mainArr[index][1]} {mainArr[index][2]} {mainArr[index][3]} {mainArr[index][4]}", datetime.now()).get_next(datetime)
                    index += 1
                    continue
            else:
                index += 1
                continue
        else:
            index = 0
            time.sleep(1) 

def main():
    index = 0
    dataArr = reading_tasks()
    logger = logger_ini()
    logger.info("Программа запущена!")
    print(dataArr)
    logger.info(f"СRONTAB считан успешно! Найдено комманд: {len(dataArr)}\n") 
    while index < len(dataArr):
        logger.debug(f"Найденные задания: {dataArr[index]}")
        index +=1
    temp = next_tick(dataArr)
    cron_workflow(dataArr, temp, logger)

if __name__ == '__main__':
    main()