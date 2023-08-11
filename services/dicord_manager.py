import discord
import os
from datetime import datetime, timedelta, timezone

from config import CHANNEL_NAME, VOICE_ROOM_NAME
from services.utils import get_attendance, get_time_interval, get_date_from_str
from services.g_sheet_manager import GSpreadService

DS_CHANNEL_NAME = os.environ.get('CHANNEL_NAME')
DS_VOICE_ROOM_NAME = os.environ.get('VOICE_ROOM_NAME')


def check_channel_enter_type(before, after):
    if before.channel is None or (before.channel is not None and after.channel is not None and (
            after.channel.name == VOICE_ROOM_NAME or after.channel.name == DS_VOICE_ROOM_NAME)):
        return 'enter'
    elif after.channel is None or (before.channel is not None and (
            before.channel.name == VOICE_ROOM_NAME or before.channel.name == DS_VOICE_ROOM_NAME)):
        return 'leave'
    else:
        return ''


class DiscordManager(discord.Client):
    attendance = {}
    concentration_time = {'_raw': []}

    g_service = GSpreadService()
    g_sheet = []

    async def on_ready(self):
        # print('Logged on as {0}!'.format(self.user))
        await self.change_presence(status=discord.Status.online)

        # google auth ready
        GSpreadService.ready(self.g_service)

    async def on_voice_state_update(self, user, before, after):
        debug_now = datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d %H:%M:%S")
        print(debug_now, ' [DEBUG] on_voice_state_update', user, before, after)
        person = f'{user.name}#{user.discriminator}' if user.discriminator != 0 else user.name
        # print(f'[DEBUG] Catch voice room event: [{person}]')
        if user == self.user:
            return
        if before.channel is not None and after.channel is not None and before.channel.id == after.channel.id:
            # print(f'[DEBUG] Pass voice room event : [{person}]')
            # 같은 채널 내 이벤트 패스
            if after.self_stream:
                print(f'{debug_now} [DEBUG] On Live: [{person}]')
            elif before.self_stream and not after.self_stream:
                print(f'{debug_now} [DEBUG] Off Live: [{person}]')
            return
        if (before.channel is not None and (
                before.channel.name == VOICE_ROOM_NAME or before.channel.name == DS_VOICE_ROOM_NAME)) \
                or (after.channel is not None and (
                after.channel.name == VOICE_ROOM_NAME or after.channel.name == DS_VOICE_ROOM_NAME)):
            now = datetime.now(timezone(timedelta(hours=9))).timestamp()

            enter_type = check_channel_enter_type(before, after)
            if enter_type == 'enter':
                # print('[DEBUG] Event type is ENTER')
                # make data
                data = list()
                data.append(now)                # (0) entry
                data.append('')                 # (1) leave -> 마무리
                data.append(person)             # (2) person
                data.append('')                 # (3) duration -> 마무리

                # 사용자 목표 시간 조회
                self.g_service.set_worksheet_by_name('members', ['id', 'name', 'goal'])
                u_data_list = self.g_service.worksheet.findall(person)
                if len(u_data_list) == 0:
                    # print('[DEBUG] Haven\'t set a goal')
                    data.append('')                 # (4) goal
                else:
                    # print('[DEBUG] Have set a goal')
                    cell = u_data_list[0]
                    row_num = cell.row
                    goal = self.g_service.worksheet.acell(f'C{row_num}').value

                    # sheet 변경
                    self.g_service.set_worksheet_by_name('sessions', ['entry', 'leave', 'person', 'duration', 'weekly_goal'])
                    # 멤버 업데이트 후 현재 날짜의 요일 확인
                    # sessions 사용자의 데이터들 중 같은 주가 데이터 수집


                    # 기존 데이터가 있는 경우 유지..
                    # 없는 경우 ..?
                    all_data_list = self.g_service.worksheet.get_all_values()
                    s_data_list = []
                    # person 은 3번째 컬럼의 데이터
                    for item in all_data_list:
                        if item[2] == person:
                            s_data_list.append(item)
                    # s_data_list = self.g_service.worksheet.findall(person)
                    print(len(s_data_list))
                    item_wk_goal = int(goal)*60*60
                    # weekday : mon(0) ~ sun(6)
                    today_weekday = datetime.today().weekday()
                    if today_weekday > 0:
                        # 기존 데이터 체크..
                        for item in s_data_list:
                            print(item)
                            # entry 데이터는 첫번째 컬럼의 데이터
                            start_week = datetime.now() - timedelta(days=today_weekday)
                            if '-' in item[0]:
                                # data 포맷이 날짜 형식
                                if item[0] > start_week.strftime("%Y-%m-%d 00:00:00"):
                                    item_wk_goal = int(item[4])*60*60
                            else:
                                # timestamp 포맷
                                if item[0] > time.mktime(datetime.strptime(start_week.strftime("%Y-%m-%d 00:00:00"), "%Y-%m-%d %H:%M:%S").timetuple()):
                                    item_wk_goal = int(item[4])*60*60

                    data.append(item_wk_goal)               # (4) goal

                ###################

                # add data > 출석 데이터는 무조건 add
                # print(data)

                self.g_service.add_row(data)
            elif enter_type == 'leave':
                # print('[DEBUG] Event type is LEAVE')
                # get sheet by name
                self.g_service.set_worksheet_by_name('sessions', ['entry', 'leave', 'person', 'duration', 'weekly_goal'])

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
                        t_yyyymmdd = datetime.fromtimestamp(now).strftime("%Y-%m-%d")
                        if '-' not in entry:
                            entry_date = datetime.fromtimestamp(int(entry)).strftime("%Y-%m-%d")
                        else:
                            entry_date = get_date_from_str(entry).strftime("%Y-%m-%d")
                        entry_yyyymmdd = entry_date
                        if t_yyyymmdd == entry_yyyymmdd:
                            if self.g_service.worksheet.acell(f'B{row_num}').value is None:
                                # update leave data
                                self.g_service.worksheet.update(f'B{row_num}', now)
                                self.g_service.worksheet.update(f'D{row_num}',
                                                                get_time_interval(entry, now, "%Y-%m-%d %H:%M:%S"))
                                return False


                # 멤버 업데이트 후 현재 날짜의 요일 확인
                # sessions 사용자의 데이터들 중 같은 주가 데이터 수집
                # 기존 데이터가 있는 경우 유지..
                # 없는 경우 ..?

                # weekday : mon(0) ~ sun(6)
                # today_weekday = datetime.today().weekday()
                # if today_weekday > 0:

    async def on_message(self, message):
        debug_now = datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d %H:%M:%S")
        print(f'{debug_now} [DEBUG] on_message', message)
        # print(f'[DEBUG] Catch message event: [{message.author}]')
        # 봇 이벤트 인 경우 종료
        if message.author == self.user:
            return
        # 설정된 채널인 경우만 아래 로직 수행
        if message.channel.name == DS_CHANNEL_NAME or message.channel.name == CHANNEL_NAME:
            # 핑 테스트 용
            if message.content == 'ping':
                await message.channel.send('pong {0.author.mention}'.format(message))
            # 출석/마무리는 리액션만 처리
            elif '출석' in message.content or '출첵' in message.content or '마무리' in message.content:
                await message.add_reaction('👍')
            elif '현황' in message.content or '조회' in message.content:
                answer = get_attendance(self.attendance, self.concentration_time)
                await message.channel.send(answer)
        # 목표 시간 등록 > !t{n} ex) !t3 : 3시간 목표
        if '!t' in message.content:
            self.g_service.set_worksheet_by_name('members', ['id', 'name', 'goal'])

            user_goal = int(message.content.replace("!t", ""))
            user = message.author
            person = f'{user.name}#{user.discriminator}' if user.discriminator != 0 else user.name
            nick_name = '' if message.author.nick is None else message.author.nick
            u_data_list = self.g_service.worksheet.findall(person)

            if len(u_data_list) == 0:
                data = list()
                data.append(person)             # (0) person
                data.append(nick_name)          # (1) name
                data.append(user_goal)          # (2) goal
                self.g_service.add_row(data)
            else:
                cell = u_data_list[0]
                row_num = cell.row
                # update goal data
                self.g_service.worksheet.update(f'C{row_num}', user_goal)
                self.g_service.worksheet.update(f'B{row_num}', nick_name)

            await message.add_reaction('👍')
            # 알수 없는 대답 일단 주석 처리
            # else:
            #     answer = get_answer(message.content)
            #     await message.channel.send(answer)
        # 리포트 전송
        # 차트 전송 참고: https://quickchart.io/documentation/send-charts-discord-bot/
        if '리포트' in message.content:
            await message.channel.send("리포트다")

# test
if __name__ == '__main__':
    chk = datetime.now() - timedelta(days=3)
    print(chk.strftime("%Y-%m-%d 00:00:00"))
