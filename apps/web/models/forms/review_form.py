from django import forms
from django.core.exceptions import ValidationError
from apps.web.models import Review, Course
from lib import constants
from lib.terms import is_valid_term

REVIEW_MINIMUM_LENGTH = 100
REVIEW_MAXIMUM_WORDS = 200

class ReviewForm(forms.ModelForm):

    def get_word_count(string): # Finds word count of given string.
        words = 1    
        for i in range(len(string)):
            if string[i] == " ":
                if string[i-1] != " " and string[i-1] != ")":
                    words += 1

            elif string[i] == "-":
                if string[i-1] != "-":
                    words += 1
        return words
    
    def clean_term(self):
        term = self.cleaned_data['term'].upper()
        if is_valid_term(term):
            return term
        else:
            raise ValidationError(
                "Please use a valid term, e.g. {}".format(
                    constants.CURRENT_TERM)
            )

    def clean_professor(self):
        professor = self.cleaned_data['professor']
        names = professor.split(' ')

        if len(names) < 2:
            raise ValidationError(
                "Please use a valid professor name, e.g. John Smith"
            )

        return " ".join([n.capitalize() for n in names])

    def clean_comments(self):
        review = self.cleaned_data['comments']

        if len(review) < REVIEW_MINIMUM_LENGTH:
            raise ValidationError(
                "Please write a longer review (at least {} characters)".format(
                    REVIEW_MINIMUM_LENGTH
                )
            )
        
        if get_word_count(review) > REVIEW_MAXIMUM_WORDS: # Check if review has > 200 words
            raise ValidationError(
                "Please limit your review to at most {} 250".format(
                    REVIEW_MAXIMUM_WORDS
                )
            )
        
        return review

    class Meta:
        model = Review
        fields = ['term', 'professor', 'comments']

        widgets = {
            'term': forms.TextInput(
                attrs={'placeholder': 'e.g. {}'.format(constants.CURRENT_TERM)}
            ),
            'professor': forms.TextInput(
                attrs={'placeholder': 'Full name please, e.g. John Smith'}
            ),
        }

        labels = {
            'comments': 'Review'
        }

        help_texts = {
            'professor': 'Please choose from the suggestions if you can.',
        }
