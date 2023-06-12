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


def get_time_interval(start, end, str_format=None):
    if type(start) == str:
        start = datetime.strptime(start, str_format).timetuple()
    if type(end) == str:
        end = datetime.strptime(end, str_format).timetuple()

    st = time.mktime(start)
    ed = time.mktime(end)
    return round((ed-st) / (3600 * 24))


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
