import discord
import time
import os
from datetime import datetime

from config import CHANNEL_NAME, VOICE_ROOM_NAME
from services.utils import get_attendance, get_answer, get_time_interval

DS_CHANNEL_NAME = os.environ.get('CHANNEL_NAME')
DS_VOICE_ROOM_NAME = os.environ.get('VOICE_ROOM_NAME')


class DiscordManager(discord.Client):
    attendance = {}
    concentration_time = {'_raw': []}

    async def on_ready(self):
        # 2) change bot status
        print('Logged on as {0}!'.format(self.user))
        await self.change_presence(status=discord.Status.online, activity=discord.Game("대기중"))

        # 1) send message
        # channel = self.get_channel(CHANNEL_ID)
        # await channel.send('Hell World')

    async def on_voice_state_update(self, user, before, after):
        user_info = '{0}#{1}'.format(user.name, user.discriminator)
        if user == self.user:
            return
        if (before.channel is not None and (before.channel.name == VOICE_ROOM_NAME or before.channel.name == DS_VOICE_ROOM_NAME)) \
                or (after.channel is not None and (after.channel.name == VOICE_ROOM_NAME or after.channel.name == DS_VOICE_ROOM_NAME)):
            # make data
            cc_data = {}
            now = datetime.today().strftime("%Y-%m-%d %H:%M:%S")

            if before.channel is None:   # Enter
                cc_data['start_time'] = now
            elif after.channel is None:  # Exit
                if user_info in self.concentration_time.keys():
                    cc_data = self.concentration_time[user_info]
                cc_data['end_time'] = now
                # raw data add
                cc_data['user'] = user_info
                cc_data['total_hours'] = get_time_interval(cc_data['start_time'], cc_data['end_time'], "%Y-%m-%d %H:%M:%S")
                self.concentration_time['_raw'].append(cc_data)

            self.concentration_time[user_info] = cc_data

    async def on_message(self, message):
        # self.user => discord bot
        if message.author == self.user:
            return
        if message.channel.name == DS_CHANNEL_NAME or message.channel.name == CHANNEL_NAME:
            now = datetime.today().strftime("%Y-%m-%d %H:%M:%S")

            if message.content == 'ping':
                await message.channel.send('pong {0.author.mention}'.format(message))
            elif message.content == '출석' or message.content == '출첵':
                count = 1

                if message.author in self.attendance.keys():
                    total_check_in = self.attendance[message.author]['t_check_in']
                    self.attendance[message.author]['t_check_in'] = total_check_in + 1
                    self.attendance[message.author]['last_start_time'] = now
                else:
                    new_check_in = {'t_check_in': count, 'last_start_time': now, 'last_end_time': now, 'total_hours': 0}
                    self.attendance[message.author] = new_check_in

                await message.add_reaction('👍')
            elif message.content == '마무리':
                self.attendance[message.author]['last_end_time'] = now
                self.attendance[message.author]['total_hours'] = \
                    get_time_interval(self.attendance[message.author]['last_start_time'], datetime.today().timetuple(), '%Y-%m-%d %H:%M:%S')
                await message.add_reaction('👍')
            elif message.content == '현황' or message.content == '조회':
                answer = get_attendance(self.attendance, self.concentration_time)
                await message.channel.send(answer)
            else:
                answer = get_answer(message.content)
                await message.channel.send(answer)
