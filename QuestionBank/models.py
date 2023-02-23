from django.db import models


#  题库对应的表
class QuestionsBank(models.Model):
    QuestionId = models.IntegerField(primary_key=True)
    QuestionContent = models.TextField()
    QuestionAnswer = models.CharField(max_length=1)
    QuestionFlagged = models.BooleanField()
    QuestionCorrected = models.IntegerField()
    QuestionInCorrected = models.IntegerField()


# 记录错题信息
class QuestionErrorInfo(models.Model):
    ErrorQuestionId = models.IntegerField()


# 记录刷题的信息
class QuestioningInfo(models.Model):
    ConfigId = models.IntegerField()
    ConfigName = models.CharField(max_length=100)
    ConfigValue = models.IntegerField()





