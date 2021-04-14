class Main:
    cars = []

    def __init__(self, log_level='normal'):
        self.log_level = log_level

    def response(self, event):
        self.log(event)

    def log(self, e):
        if e['event'] == 'register':
            self._log('IP %s 注册为 %s 队 %s 车' % (e['ip'], e['team'], e['car']))
        elif e['event'] == 'lost':
            self._log('IP %s %s 队 %s 车 已离线' % (e['ip'], e['team'], e['car']))
        elif e['event'] == 'reconnect':
            self._log('IP %s %s 队 %s 车 已重连' % (e['ip'], e['team'], e['car']))
        elif e['event'] == 'communication':
            self._log('IP %s %s 队 %s 车 向 %s 车发送车间通信' % (e['ip'], e['team'], e['car'], e['message']))
        elif e['event'] == 'start':
            self._log('IP %s %s 队 %s 车 计时启动' % (e['ip'], e['team'], e['car']))
        elif e['event'] == 'stop':
            self._log('IP %s %s 队 %s 车 计时停止' % (e['ip'], e['team'], e['car']))
        elif e['event'] == 'lost_pkg':
            self._log('IP %s %s 队 %s 车 出现丢包' % (e['ip'], e['team'], e['car']))

    def _log(self, text):
        if self.log_level != 'quite':
            print(text)

