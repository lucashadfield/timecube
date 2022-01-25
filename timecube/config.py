# class Config:
#     pass
#
#
# def config_mode(self):
#     if self.state != 'config':
#         # enter config mode
#         self.interval_task.cancel()
#         if isinstance(self.state, Interval):
#             self.saved_interval_duration += self._transition_state('config')
#         else:
#             self._transition_state('config')
#
#         self.config_hash = hash(str(self.config))
#         self.config_id = 0
#         self.config_next()
#         # do config things
#     else:
#         # exit config mode
#         if self.config_hash != hash(str(self.config)):
#             # new config
#             self.initialise()
#             self.start()
#         else:
#             self._transition_state(self._current_interval)
#             self.interval_task = asyncio.create_task(self._start_interval_task(self.saved_interval_duration))
#
#     def config_next(self):
#         self.config_id = (self.config_id + 1) % len(self.config)
#         config_item = list(self.config.keys())[self.config_id]
#         print('configuring {}: {}'.format(config_item, self.config[config_item]))
#
#     def config_increment(self):
#         config_item = list(self.config.keys())[self.config_id]
#         self.config[config_item] = min(self.config[config_item] + 1, 30000)
#         print('{}: {}'.format(config_item, self.config[config_item]))
#
#     def config_decrement(self):
#         config_item = list(self.config.keys())[self.config_id]
#         self.config[config_item] = max(self.config[config_item] - 1, 1)
#         print('{}: {}'.format(config_item, self.config[config_item]))
