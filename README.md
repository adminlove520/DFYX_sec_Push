### 企业微信推送-local
## 参数配置
''''
        self.corpid = ''
        self.agentid = ''
        self.thumbmediaid = ''
        self.corpsecret = ''
        ''''''
        本地配置：
        其中thumbmediaid&access_token这两个参数需要在 https://developer.work.weixin.qq.com/devtool/interface/alone?id=10112 中调用得到；
## 更新记录
- [1] fix 修复thumb_media_id短期失效问题
- [2] feat 优化代码逻辑
- [3] feat 考虑github actions运行(可信IP问题尚未解决) 
## 使用说明
本地请运行  main_local_dev.py