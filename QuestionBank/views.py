from django.shortcuts import render
from QuestionBank.models import QuestionsBank, QuestioningInfo, QuestionErrorInfo
from django.db.models import Max
import json
import re


# Create your views here.


def main_page(request):
    return render(request, "main.html")


def query_normal_questions(request):
    try:
        """
        从数据库表中获取上次做到的题目编号,将编号转换为三位数
        """
        LastQuestionID = QuestioningInfo.objects.get(ConfigName="LastQuestionID").ConfigValue
        Question_Id_str = question_id_convert(LastQuestionID)
    except:
        Question_Id_str = "001"
    """
    查询QuestionsBank，获取Question_Id，Question_Content_Details，Correct_Answer
    """
    Question_Id = query_QuestionsBank(Question_Id_str, "QuestionId")
    Question_Content_Details = query_QuestionsBank(Question_Id_str, "QuestionContent")
    Question_Content_Details_List = process_Question_Content(Question_Content_Details)
    Correct_Answer = query_QuestionsBank(Question_Id_str, "QuestionAnswer")
    print(Question_Id_str)
    Question_Correct_Rate = correct_rate_cal(Question_Id_str)
    Questions_Comments = query_QuestionsBank(Question_Id_str, "QuestionComments")
    is_normal_or_error = "0"
    """
    返回数据到前端
    """
    return render(request, "query_questions.html", locals())


def query_error_questions(request):
    try:
        """
        从数据库表中获取上次做到的题目编号,将编号转换为三位数
        """
        LastQuestionID = QuestioningInfo.objects.get(ConfigName="LastErrorQuestionID").ConfigValue
        Question_Id_str = question_id_convert(LastQuestionID)
    except:
        Question_Id_str = "001"
    """
    查询QuestionsBank，获取Question_Id，Question_Content_Details，Correct_Answer
    """
    Question_Id = query_QuestionsBank(Question_Id_str, "QuestionId")
    Question_Content_Details = query_QuestionsBank(Question_Id_str, "QuestionContent")
    Question_Content_Details_List = process_Question_Content(Question_Content_Details)
    Correct_Answer = query_QuestionsBank(Question_Id_str, "QuestionAnswer")
    Question_Correct_Rate = correct_rate_cal(Question_Id_str)
    Questions_Comments = query_QuestionsBank(Question_Id_str, "QuestionComments")
    is_normal_or_error = "1"
    """
    返回数据到前端
    """
    return render(request, "query_questions.html", locals())


def prev_question(request):
    # 从前端获取页面上的问题编号：text_QuestionNo
    currentQuestionNo = request.GET.get("text_QuestionNo")
    is_normal_or_error = request.GET.get("is_normal_or_error")
    """
    如果问题编号是空或者001，那么将prevQuestionNo_str设置为"001"，
    否则设置prevQuestionNo为当前问题编号减1。
    """
    if currentQuestionNo == "" or currentQuestionNo == "001":
        prevQuestionNo_str = "001"
    else:
        if is_normal_or_error == "0":
            """
            判断prevQuestionNo：
            当小于10时，在前面加两个0；当小于100时，在前面加一个0；当大于100时，不做改动；
            然后将其转化为字符串，存入prevQuestionNo_str
            """
            prevQuestionNo = int(currentQuestionNo) - 1
            prevQuestionNo_str = question_id_convert(prevQuestionNo)
        else:
            # 查询currentQuestionNo对应的id
            try:
                current_id = QuestionErrorInfo.objects.get(ErrorQuestionId=currentQuestionNo).id
                prev_id = current_id - 1
                prevQuestionNo = QuestionErrorInfo.objects.get(id=prev_id).ErrorQuestionId
                prevQuestionNo_str = question_id_convert(prevQuestionNo)
            except:
                prevQuestionNo_str = currentQuestionNo
    """
    根据prevQuestionNo_str查询QuestionsBank表，获取上一个问题信息。
    """
    try:
        Question_Id = query_QuestionsBank(prevQuestionNo_str, "QuestionId")
        Question_Id_str = question_id_convert(Question_Id)
        Question_Content_Details = query_QuestionsBank(prevQuestionNo_str, "QuestionContent")
        Correct_Answer = query_QuestionsBank(prevQuestionNo_str, "QuestionAnswer")
        Question_Correct_Rate = correct_rate_cal(prevQuestionNo_str)
        Questions_Comments = query_QuestionsBank(Question_Id_str, "QuestionComments")
        # 新增加，对选项进行回车换行
        Question_Content_Details_List = process_Question_Content(Question_Content_Details)
        """
        将刷题编号写入数据库QuestioningInfo中
        """
        if is_normal_or_error == "0":
            QuestioningInfo.objects.filter(ConfigName="LastQuestionID").update(ConfigValue=Question_Id_str)
        else:
            QuestioningInfo.objects.filter(ConfigName="LastErrorQuestionID").update(ConfigValue=Question_Id_str)
    except:
        checkAnswer_Notification = "查询失败"
    return render(request, "query_questions.html", locals())


def next_question(request):
    currentQuestionNo = request.GET.get("text_QuestionNo")
    is_normal_or_error = request.GET.get("is_normal_or_error")
    if currentQuestionNo == "":
        nextQuestionNo_str = "001"
    else:
        print(is_normal_or_error)
        if is_normal_or_error == "0":
            nextQuestionNo = int(currentQuestionNo) + 1
            nextQuestionNo_str = question_id_convert(nextQuestionNo)
        else:
            # 查询currentQuestionNo对应的id
            try:
                current_id = QuestionErrorInfo.objects.get(ErrorQuestionId=int(currentQuestionNo)).id
                next_id = current_id + 1
                nextQuestionNo = QuestionErrorInfo.objects.get(id=next_id).ErrorQuestionId
                nextQuestionNo_str = question_id_convert(nextQuestionNo)
            except:
                nextQuestionNo_str = currentQuestionNo

    """
    根据nextQuestionNo_str查询QuestionsBank表，获取下一个问题信息。
    """
    try:
        Question_Id = query_QuestionsBank(nextQuestionNo_str, "QuestionId")
        Question_Id_str = question_id_convert(Question_Id)
        Question_Content_Details = query_QuestionsBank(nextQuestionNo_str, "QuestionContent")
        Correct_Answer = query_QuestionsBank(nextQuestionNo_str, "QuestionAnswer")
        Question_Correct_Rate = correct_rate_cal(nextQuestionNo_str)
        Questions_Comments = query_QuestionsBank(Question_Id_str, "QuestionComments")
        # 新增加，对选项进行回车换行
        Question_Content_Details_List = process_Question_Content(Question_Content_Details)
        """
        将刷题编号写入数据库QuestioningInfo中
        """
        if is_normal_or_error == "0":
            QuestioningInfo.objects.filter(ConfigName="LastQuestionID").update(ConfigValue=Question_Id_str)
        else:
            QuestioningInfo.objects.filter(ConfigName="LastErrorQuestionID").update(ConfigValue=Question_Id_str)
    except:
        checkAnswer_Notification = "查询失败"

    return render(request, "query_questions.html", locals())


def check_answer(request):
    SelectedAnswer = request.GET.get("raido_list")
    Question_Id_str = request.GET.get("text_QuestionNo")
    checkAnswer_Notification = request.GET.get("checkAnswer_Notification")
    is_normal_or_error = request.GET.get("is_normal_or_error")
    Question_Content_Details = query_QuestionsBank(Question_Id_str, "QuestionContent")
    Question_Content_Details_List = process_Question_Content(Question_Content_Details)
    Correct_Answer = query_QuestionsBank(Question_Id_str, "QuestionAnswer")
    Questions_Comments = query_QuestionsBank(Question_Id_str, "QuestionComments")
    try:
        Question_Content = QuestionsBank.objects.get(QuestionId=Question_Id_str)
        QuestionCorrected = Question_Content.QuestionCorrected
        QuestionInCorrected = Question_Content.QuestionInCorrected
        # 将前端传入的答案和正确答案对比
        print("123")
        if SelectedAnswer == Correct_Answer:
            QuestionCorrected_Count = QuestionCorrected + 1
            QuestionsBank.objects.filter(QuestionId=Question_Id_str).update(
                QuestionCorrected=QuestionCorrected_Count)
        elif SelectedAnswer != Correct_Answer:
            QuestionInCorrected_Count = QuestionInCorrected + 1
            print(QuestionInCorrected_Count)
            QuestionsBank.objects.filter(QuestionId=Question_Id_str).update(
                QuestionInCorrected=QuestionInCorrected_Count)
            """这里要加上向QuestionErrorInfo表里插Question_Id_str的步骤"""
            try:
                existed_Question_Id = QuestionErrorInfo.objects.get(ErrorQuestionId=Question_Id_str).ErrorQuestionId
            except:
                try:
                    max_Question_Id = QuestionErrorInfo.objects.aggregate(Max('id'))
                    max_Question_Id_value = max_Question_Id['id__max']
                    print(max_Question_Id_value)
                    if max_Question_Id_value is None:
                        max_Question_Id_n = 1
                    else:
                        max_Question_Id_n = max_Question_Id_value + 1
                    QuestionErrorInfo.objects.create(id=max_Question_Id_n, ErrorQuestionId=Question_Id_str)
                except:
                    DB_Notification = "数据库异常"
    except:
        checkAnswer_Notification = "对比失败！"
    # 刷新rate
    Question_Correct_Rate = correct_rate_cal(Question_Id_str)
    return render(request, "query_questions.html", locals())


# 这里是插入comment值的
def insert_comment(request):
    comments_posted = request.GET.get('Comments_posted')
    print(comments_posted)
    Question_Id_str = request.GET.get("text_QuestionNo")
    try:
        prev_comment = query_QuestionsBank(Question_Id_str, "QuestionComments")
        current_comment = prev_comment + "\n" + comments_posted
        QuestionsBank.objects.filter(QuestionId=Question_Id_str).update(QuestionComments=current_comment)
    except:
        checkAnswer_Notification = "插入备注失败！"

    Question_Content_Details = query_QuestionsBank(Question_Id_str, "QuestionContent")
    Question_Content_Details_List = process_Question_Content(Question_Content_Details)
    Correct_Answer = query_QuestionsBank(Question_Id_str, "QuestionAnswer")
    Question_Correct_Rate = correct_rate_cal(Question_Id_str)
    Questions_Comments = query_QuestionsBank(Question_Id_str, "QuestionComments")
    return render(request, "query_questions.html", locals())


# 问题id转换
def question_id_convert(LastQuestionID):
    if LastQuestionID < 10:
        Question_Id_str = "00" + str(LastQuestionID)
    elif LastQuestionID < 100:
        Question_Id_str = "0" + str(LastQuestionID)
    else:
        Question_Id_str = str(LastQuestionID)
    return Question_Id_str


# 查询QuestionBank方法，根据flag返回对应的值,flag 是QuestionBank对应的字段
def query_QuestionsBank(query_string, flag):
    try:
        Question_Content = QuestionsBank.objects.get(QuestionId=query_string)
        if flag == "QuestionId":
            return Question_Content.QuestionId
        elif flag == "QuestionContent":
            return Question_Content.QuestionContent
        elif flag == "QuestionAnswer":
            return Question_Content.QuestionAnswer
        elif flag == "QuestionFlagged":
            return Question_Content.QuestionFlagged
        elif flag == "QuestionCorrected":
            return Question_Content.QuestionCorrected
        elif flag == "QuestionInCorrected":
            return Question_Content.QuestionInCorrected
        elif flag == "QuestionComments":
            return Question_Content.QuestionComments.replace('\r', '\\r').replace('\n', '\\n')
    except:
        return ""


# 更新QuestionBank，根据flag返回对应的值,flag 是QuestionBank对应的字段
def update_QuestionsBank(question_id, updated_filed, updated_filed_value):
    try:
        pass
    except:
        pass


# 更新QuestioningInfo表
def update_QuestioningInfo(update_name, update_value):
    try:
        QuestioningInfo.objects.filter(ConfigName=update_name).update(ConfigValue=update_value)
        return "数据操作成功"
    except:
        return "数据库操作失败"


# 根据Question_Id返回正确率
def correct_rate_cal(Question_Id):
    Question_Corrected = query_QuestionsBank(Question_Id, "QuestionCorrected")
    Question_InCorrected = query_QuestionsBank(Question_Id, "QuestionInCorrected")
    if Question_InCorrected == 0:
        Question_Correct_Rate = "100%"
        if Question_Corrected == 0:
            Question_Correct_Rate = "0%"
    else:
        Question_Correct_Rate = '{:.0%}'.format(Question_Corrected / (Question_Corrected + Question_InCorrected))
    return Question_Correct_Rate


# 处理问题内容，并分段
def process_Question_Content(Question_Content):
    return_List = Question_Content.split('\n')
    return return_List
