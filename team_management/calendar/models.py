from django.db import models


class Holidays(models.Model):
    """
    Праздники и выходные, получает автоматически,
     через loader
    """
    holiday_date = models.DateField(
        verbose_name='Дата выходного/праздника',
    )
    sokr = models.BooleanField(
        verbose_name='True - сокращенный день False - полностью выходной',
    )

    class Meta:
        indexes = [models.Index(fields=['holiday_date'])]
        db_table = 'calendar_holidays'
