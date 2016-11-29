from django import forms

from apps.web.models import Review


class ManualSentimentForm(forms.Form):
    LAYUP_SENTIMENT_HARD = "-1"
    LAYUP_SENTIMENT_SOMEWHAT_HARD = "-0.5"
    LAYUP_SENTIMENT_NEUTRAL = "0"
    LAYUP_SENTIMENT_SOMEWHAT_EASY = "0.5"
    LAYUP_SENTIMENT_EASY = "1"
    LAYUP_SENTIMENT_CHOICES = [
        (LAYUP_SENTIMENT_HARD, "Hard"),
        (LAYUP_SENTIMENT_SOMEWHAT_HARD, "Somewhat Hard"),
        (LAYUP_SENTIMENT_NEUTRAL, "Neutral"),
        (LAYUP_SENTIMENT_SOMEWHAT_EASY, "Somewhat Easy"),
        (LAYUP_SENTIMENT_EASY, "Easy"),
    ]

    QUALITY_SENTIMENT_BAD = "-1"
    QUALITY_SENTIMENT_SOMEWHAT_BAD = "-0.5"
    QUALITY_SENTIMENT_NEUTRAL = "0"
    QUALITY_SENTIMENT_SOMEWHAT_GOOD = "0.5"
    QUALITY_SENTIMENT_GOOD = "1"
    QUALITY_SENTIMENT_CHOICES = [
        (QUALITY_SENTIMENT_BAD, "Bad"),
        (QUALITY_SENTIMENT_SOMEWHAT_BAD, "Somewhat Bad"),
        (QUALITY_SENTIMENT_NEUTRAL, "Neutral"),
        (QUALITY_SENTIMENT_SOMEWHAT_GOOD, "Somewhat Good"),
        (QUALITY_SENTIMENT_GOOD, "Good"),
    ]

    review_id = forms.IntegerField(
        required=True,
        widget=forms.HiddenInput(),
    )
    layup_sentiment = forms.ChoiceField(
        choices=LAYUP_SENTIMENT_CHOICES,
        initial=LAYUP_SENTIMENT_NEUTRAL,
        required=True,
        widget=forms.RadioSelect(),
    )
    quality_sentiment = forms.ChoiceField(
        choices=QUALITY_SENTIMENT_CHOICES,
        initial=QUALITY_SENTIMENT_NEUTRAL,
        required=True,
        widget=forms.RadioSelect(),
    )

    def clean_layup_sentiment(self):
        return float(self.cleaned_data["layup_sentiment"])

    def clean_quality_sentiment(self):
        return float(self.cleaned_data["quality_sentiment"])

    def save_sentiment(self):
        review = Review.objects.get(id=self.cleaned_data["review_id"])
        review.sentiment_labeler = Review.MANUAL_SENTIMENT_LABELER
        review.layup_sentiment = self.cleaned_data["layup_sentiment"]
        review.quality_sentiment = self.cleaned_data["quality_sentiment"]
        review.save()
