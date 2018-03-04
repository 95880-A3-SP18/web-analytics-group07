from django.db import models


class Question(models.Model):
    question_text = models.CharField(max_length=200)

    def __str__(self):
        return self.question_text


class Choice(models.Model):
    question_text = models.CharField(max_length=200, default='')
    choice_number = models.IntegerField(default=0)
    votes = models.IntegerField(default=0)



    def __str__(self):
        return self.question_text+str(self.choice_number)