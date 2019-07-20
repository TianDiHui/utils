# -*- coding: utf-8 -*-
import os
from crontab import CronTab


def linux_crontab_add(temporal_frequency, action):
    """
    :param temporal_frequency: 计划任务频率 入参字符串格式:* * * * *
    :param action: 计划任务动作 shell命令
    :return:
    liww
    """
    try:
        my_user_cron = CronTab(user=True)
    except TypeError:
        os.system("pip uninstall crontab -y")
        my_user_cron = CronTab(user=True)

    generate_crontab = temporal_frequency + ' ' + action

    Nu = 0
    for my_user_cron_one in my_user_cron.crons:
        if str(my_user_cron_one) == generate_crontab:
            Nu = 1
    if Nu == 0:
        job = my_user_cron.new(command=action)

        job.setall(temporal_frequency)

        my_user_cron.write()

    return 1