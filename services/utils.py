import time
from datetime import datetime


def get_day_of_week():
    weekday_list = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']

    weekday = weekday_list[datetime.today().weekday()]
    date = datetime.today().strftime("%Y년 %m월 %d일")
    result = '{}({})'.format(date, weekday)
    return result


def get_time():
    return datetime.today().strftime("%H시 %M분 %S초")


def get_time_interval(start, end, str_format=None, calc=None):
    if type(start) == str:
        if '-' in start:
            start = datetime.strptime(start, str_format).timetuple()
    if type(end) == str:
        if '-' in start:
            end = datetime.strptime(end, str_format).timetuple()

    if type(start) is str and '-' in start:
        st = time.mktime(start)
    else:
        st = float(start)

    if type(end) is str and '-' in end:
        ed = time.mktime(end)
    else:
        ed = end

    # print(type(start), start, type(end), end)
    if calc == 'hour':
        return round((ed-st) / (3600 * 24))
    else:
        return int(ed-st)


def get_date_from_str(str_date, str_format='%Y-%m-%d %H:%M:%S'):
    if type(str_date) != str:
        return None

    return datetime.strptime(str_date, str_format)


def get_answer(text):
    trim_text = text.replace(" ", "")

    answer_dict = {
        "안녕": "안녕하세요. MyBot입니다.",
        "요일": ":calendar: 오늘은 {}입니다.".format(get_day_of_week()),
        "시간": ":clock9: 현재 시간은 {}입니다.".format(get_time()),
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


def get_attendance(attendance, concentration_time):
    result = '='*30 + '\n'

    for user in attendance.keys():
        result += '- {0} : {1}\n'.format(user, attendance[user])

    result += '-'*30 + '\n'

    for user in concentration_time.keys():
        result += '- {0} : {1}\n'.format(user, concentration_time[user])

    if len(attendance.keys()) == 0 and len(concentration_time.keys()) == 0:
        result += ':cloud_rain: 출석 현황 없음 :cloud_rain:\n'

    result += '='*30
    return result

def get_percentage_working_time(curr, total):
    # 반올림, 자리수 소수점 1번째까지.
    return round(float(curr) / float(total) * 100, 0)

def get_progressbar(curr, total):
    percent = get_percentage_working_time(curr, total)
    empty_square = '□'*20
    full_square = '■'*20

    return full_square[:int(percent*0.2)] + empty_square[int(percent*0.2):]

def get_user_stat(user_name, curr, total):
    BACKTICKS_LINE = '```\n'

    if type(curr) == str:
        curr = int(curr)
    if type(total) == str:
        total = int(float(total)) if total != '' else 0
    # print(f'[DEBIG] >> curr : {curr}, total : {total} ')
    return BACKTICKS_LINE + \
        user_name + '\n' + \
        get_progressbar(curr, total) + ' ' + str(get_percentage_working_time(curr, total)) + '%\n' + \
        str(int(curr/60/60)) + ' / ' + str(int(total/60/60)) + '시간\n' + \
        BACKTICKS_LINE
