class Main:
    cars = {}

    def __init__(self, onChange, log_level='normal'):
        self.log_level = log_level
        self.onChange = onChange

    def response(self, event):
        if event['team'] not in self.cars.keys():
            self.cars[event['team']] = {}
        self.cars[event['team']][event['car']] = {
            'connect_time': event['time'],
            'connect': True,
            'status': 'ready',
            'timer': 0,
            'lost': 0,
            'start_time': 0
        }
        if event['event'] == 'register':
            self.cars[event['team']][event['car']] = {
                'connect_time': event['time'],
                'connect': True,
                'status': 'ready',
                'timer': 0,
                'lost': 0,
                'start_time': 0
            }
        elif event['event'] == 'lost':
            self.cars[event['team']][event['car']]['connect'] = False
        elif event['event'] == 'remove':
            del self.cars[event['team']][event['car']]
        elif event['event'] == 'reconnect':
            self.cars[event['team']][event['car']]['connect'] = True
        elif event['event'] == 'start':
            self.cars[event['team']][event['car']]['status'] = 'timing'
            self.cars[event['team']][event['car']]['start_time'] = event['time']
        elif event['event'] == 'stop':
            self.cars[event['team']][event['car']]['status'] = 'finish'
            delta = event['time'].timestamp() * 1000 - self.cars[event['team']][event['car']]['start_time']
            self.cars[event['team']][event['car']]['timer'] = '%i分%i秒' % (int(delta / 60000), (int(delta / 1000)) % 60)
        elif event['event'] == 'lost_pkg':
            self.cars[event['team']][event['car']]['lost'] += 1
        self.onChange(self.cars)
        self.log(event)

    def log(self, e):
        if e['event'] == 'register':
            self._log('IP %s 注册为 %s 队 %s 车' % (e['ip'], e['team'], e['car']))
        elif e['event'] == 'lost':
            self._log('IP %s %s 队 %s 车 已离线' % (e['ip'], e['team'], e['car']))
        elif e['event'] == 'remove':
            self._log('IP %s %s 队 %s 车 资源已被释放' % (e['ip'], e['team'], e['car']))
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
        elif e['event'] == 'report':
            self._log('IP %s %s 队 %s 车 上报信息' % (e['ip'], e['team'], e['car']))

    def _log(self, text):
        if self.log_level != 'quite':
            print(text)



