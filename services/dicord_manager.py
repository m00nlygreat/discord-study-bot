import discord
import os
from datetime import datetime

import gspread.exceptions

from config import CHANNEL_NAME, VOICE_ROOM_NAME
from services.utils import get_attendance, get_answer, get_time_interval, get_date_from_str
from services.g_sheet_manager import GSpreadService

DS_CHANNEL_NAME = os.environ.get('CHANNEL_NAME')
DS_VOICE_ROOM_NAME = os.environ.get('VOICE_ROOM_NAME')


class DiscordManager(discord.Client):
    attendance = {}
    concentration_time = {'_raw': []}

    g_service = GSpreadService()
    g_sheet = []

    async def on_ready(self):
        # print('Logged on as {0}!'.format(self.user))
        await self.change_presence(status=discord.Status.online, activity=discord.Game("대기중"))

        # google auth ready
        GSpreadService.ready(self.g_service)

    async def on_voice_state_update(self, user, before, after):
        # print(user, before, after)
        user_info = '{0}#{1}'.format(user.name, user.discriminator)
        if user == self.user:
            return
        if (before.channel is not None and (before.channel.name == VOICE_ROOM_NAME or before.channel.name == DS_VOICE_ROOM_NAME)) \
                or (after.channel is not None and (after.channel.name == VOICE_ROOM_NAME or after.channel.name == DS_VOICE_ROOM_NAME)):
            # make data
            cc_data = {}
            now = datetime.today().strftime("%Y-%m-%d %H:%M:%S")

            if before.channel is None or (before.channel is not None and after.channel is not None and (after.channel.name == VOICE_ROOM_NAME or after.channel.name == DS_VOICE_ROOM_NAME)):   # Enter
                cc_data['start_time'] = now
            elif after.channel is None or (before.channel is not None and (before.channel.name == VOICE_ROOM_NAME or before.channel.name == DS_VOICE_ROOM_NAME)):  # Exit
                if user_info in self.concentration_time.keys():
                    cc_data = self.concentration_time[user_info]
                cc_data['end_time'] = now
                # raw data add
                cc_data['user'] = user_info
                cc_data['total_hours'] = get_time_interval(cc_data['start_time'], cc_data['end_time'], "%Y-%m-%d %H:%M:%S", "hour")
                self.concentration_time['_raw'].append(cc_data)

            self.concentration_time[user_info] = cc_data

    async def on_message(self, message):
        # 봇 이벤트 인 경우 종료
        if message.author == self.user:
            return
        # 설정된 채널인 경우만 아래 로직 수행
        if message.channel.name == DS_CHANNEL_NAME or message.channel.name == CHANNEL_NAME:
            user = message.author
            person = f'{user.name}#{user.discriminator}' if user.discriminator != 0 else user.name
            now = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
            # 핑 테스트 용
            if message.content == 'ping':
                await message.channel.send('pong {0.author.mention}'.format(message))
            # 출석 또는 출첵 단어가 포함된 경우
            elif '출석' in message.content or '출첵' in message.content:
                # make data
                data = list()
                data.append(now)                # (0) entry
                data.append('')                 # (1) leave -> 마무리
                data.append(person)             # (2) person
                data.append('')                 # (3) duration -> 마무리

                # add data > 출석 데이터는 무조건 add
                # print(data)
                try:
                    self.g_service.set_worksheet_by_name('sessions')
                except gspread.exceptions.WorksheetNotFound:
                    self.g_service.add_worksheet('sessions', ['entry', 'leave', 'person', 'duration'])
                self.g_service.add_row(data)

                await message.add_reaction('👍')
            elif message.content == '마무리':
                # get sheet by name
                try:
                    self.g_service.set_worksheet_by_name('sessions')
                except gspread.exceptions.WorksheetNotFound:
                    self.g_service.add_worksheet('sessions', ['entry', 'leave', 'person', 'duration'])

                # find user data
                u_data_list = self.g_service.worksheet.findall(person)
                u_data_list.reverse()
                for cell in u_data_list:
                    row_num = cell.row
                    # get leave data
                    entry = self.g_service.worksheet.acell(f'A{row_num}').value
                    leave = self.g_service.worksheet.acell(f'B{row_num}').value
                    # print(leave)
                    # print(entry)
                    # check entry data
                    if entry is not None:
                        entry_date = get_date_from_str(entry)

                        t_yyyymmdd = datetime.today().strftime("%Y-%m-%d")
                        entry_yyyymmdd = entry_date.strftime("%Y-%m-%d")
                        if t_yyyymmdd == entry_yyyymmdd:
                            if self.g_service.worksheet.acell(f'B{row_num}').value is None:
                                # update leave data
                                self.g_service.worksheet.update(f'B{row_num}', now)
                                self.g_service.worksheet.update(f'D{row_num}', get_time_interval(entry, now, "%Y-%m-%d %H:%M:%S"))
                                await message.add_reaction('👍')
                                return False
            elif message.content == '현황' or message.content == '조회':
                answer = get_attendance(self.attendance, self.concentration_time)
                await message.channel.send(answer)
            else:
                answer = get_answer(message.content)
                await message.channel.send(answer)
