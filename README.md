# mail-issue
邮件统计信息系统
### 安装步骤
- 第一步
生成Django镜像
```
docker build . -t django:2.0.13
```

- 第二步
执行start.sh

- 第三步
添加计划任务
```
*/5 * * * * python3 /root/hoyin/mail-issue-docker/receiv_email_v1.0.py &> /tmp/receive_email.log
```

