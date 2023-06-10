import discord
import time
import os
from datetime import datetime

from config import CHANNEL_NAME
DS_CHANNEL_NAME = os.environ.get('CHANNEL_NAME')


class DiscordManager(discord.Client):
    attendance = {}

    async def on_ready(self):
        # 2) change bot status
        print('Logged on as {0}!'.format(self.user))
        await self.change_presence(status=discord.Status.online, activity=discord.Game("대기중"))

        # 1) send message
        # channel = self.get_channel(CHANNEL_ID)
        # await channel.send('Hell World')

    async def on_message(self, message):
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
                st = time.mktime(datetime.strptime(self.attendance[message.author]['last_start_time'], '%Y-%m-%d %H:%M:%S').timetuple())
                ed = time.mktime(datetime.today().timetuple())
                self.attendance[message.author]['total_hours'] = round((ed-st) / (3600 * 24))
                await message.add_reaction('👍')
            elif message.content == '현황' or message.content == '조회':
                answer = self.get_attendance()
                await message.channel.send(answer)
            else:
                answer = self.get_answer(message.content)
                await message.channel.send(answer)

    def get_day_of_week(self):
        weekday_list = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']

        weekday = weekday_list[datetime.today().weekday()]
        date = datetime.today().strftime("%Y년 %m월 %d일")
        result = '{}({})'.format(date, weekday)
        return result

    def get_time(self):
        return datetime.today().strftime("%H시 %M분 %S초")

    def get_answer(self, text):
        trim_text = text.replace(" ", "")

        answer_dict = {
            "안녕": "안녕하세요. MyBot입니다.",
            "요일": ":calendar: 오늘은 {}입니다.".format(self.get_day_of_week()),
            "시간": ":clock9: 현재 시간은 {}입니다.".format(self.get_time()),
            "뭐해": "음악을 듣고 있어요 🎵"
        }

        if trim_text == '' or None:
            return "알 수 없는 질의입니다. 답변을 드릴 수 없습니다."
        elif trim_text in answer_dict.keys():
            return answer_dict[trim_text]
        else:
            for key in answer_dict.keys():
                if key.find(trim_text) != -1:
                    return "연관 단어 [" + key + "]에 대한 답변입니다.\n" + answer_dict[key]

            for key in answer_dict.keys():
                if answer_dict[key].find(text[1:]) != -1:
                    return "질문과 가장 유사한 질문 [" + key + "]에 대한 답변이에요.\n" + answer_dict[key]

        return "알 수 없는 질의입니다. 답변을 드릴 수 없습니다."

    def get_attendance(self):
        result = '-'*30 + '\n'

        for user in self.attendance.keys():
            result += '- {0} : {1}\n'.format(user, self.attendance[user])

        if len(self.attendance.keys()) == 0:
            result += ':cloud_rain: 출석 현황 없음 :cloud_rain:\n'

        result += '-'*30
        return result
