from django.db import models


class OpenAIVisionModels(models.TextChoices):
    GPT_4o_MINI = 'gpt-4o-mini', 'GPT-4o Mini (Recommended)'
    GPT_4o = 'gpt-4o', 'GPT-4o '
    GPT_4_1_MINI = 'gpt-4.1-mini', 'GPT-4.1 Mini'
    GPT_4_1 = 'gpt-4.1', 'GPT-4.1'
