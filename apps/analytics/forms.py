from django import forms

from apps.web.models import Review


class ManualSentimentForm(forms.Form):
    DIFFICULTY_SENTIMENT_HARD = "-1"
    DIFFICULTY_SENTIMENT_SOMEWHAT_HARD = "-0.5"
    DIFFICULTY_SENTIMENT_NEUTRAL = "0"
    DIFFICULTY_SENTIMENT_SOMEWHAT_EASY = "0.5"
    DIFFICULTY_SENTIMENT_EASY = "1"
    DIFFICULTY_SENTIMENT_CHOICES = [
        (DIFFICULTY_SENTIMENT_HARD, "Hard"),
        (DIFFICULTY_SENTIMENT_SOMEWHAT_HARD, "Somewhat Hard"),
        (DIFFICULTY_SENTIMENT_NEUTRAL, "Neutral"),
        (DIFFICULTY_SENTIMENT_SOMEWHAT_EASY, "Somewhat Easy"),
        (DIFFICULTY_SENTIMENT_EASY, "Easy"),
    ]

    QUALITY_SENTIMENT_BAD = "-1"
    QUALITY_SENTIMENT_SOMEWHAT_BAD = "-0.5"
    QUALITY_SENTIMENT_NEUTRAL = "0"
    QUALITY_SENTIMENT_SOMEWHAT_QUALITY = "0.5"
    QUALITY_SENTIMENT_QUALITY = "1"
    QUALITY_SENTIMENT_CHOICES = [
        (QUALITY_SENTIMENT_BAD, "Bad"),
        (QUALITY_SENTIMENT_SOMEWHAT_BAD, "Somewhat Bad"),
        (QUALITY_SENTIMENT_NEUTRAL, "Neutral"),
        (QUALITY_SENTIMENT_SOMEWHAT_QUALITY, "Somewhat Good"),
        (QUALITY_SENTIMENT_QUALITY, "Good"),
    ]

    review_id = forms.IntegerField(
        required=True,
        widget=forms.HiddenInput(),
    )
    difficulty_sentiment = forms.ChoiceField(
        choices=DIFFICULTY_SENTIMENT_CHOICES,
        initial=DIFFICULTY_SENTIMENT_NEUTRAL,
        required=True,
        widget=forms.RadioSelect(),
    )
    quality_sentiment = forms.ChoiceField(
        choices=QUALITY_SENTIMENT_CHOICES,
        initial=QUALITY_SENTIMENT_NEUTRAL,
        required=True,
        widget=forms.RadioSelect(),
    )

    def clean_difficulty_sentiment(self):
        return float(self.cleaned_data["difficulty_sentiment"])

    def clean_quality_sentiment(self):
        return float(self.cleaned_data["quality_sentiment"])

    def save_sentiment(self):
        review = Review.objects.get(id=self.cleaned_data["review_id"])
        review.sentiment_labeler = Review.MANUAL_SENTIMENT_LABELER
        review.difficulty_sentiment = self.cleaned_data["difficulty_sentiment"]
        review.quality_sentiment = self.cleaned_data["quality_sentiment"]
        review.save()
