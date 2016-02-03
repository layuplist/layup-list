LayupList.Web.Common = function() {
    var com = LayupList.Web.Common;
    com.vote = function(value, courseId, element, forLayups) {
        var postData = {
            "value": value,
            "forLayup": forLayups
        };

        $.post("/api/course/" + courseId + "/vote", postData, function(data) {
            var $arrow = $(element);

            // color arrows
            if (data.was_unvote) {
                $arrow.siblings(".selected").removeClass("selected").addClass("unselected");
                $arrow.removeClass("selected").addClass("unselected");
            } else {
                $arrow.siblings(".selected").removeClass("selected").addClass("unselected");
                $arrow.removeClass("unselected").addClass("selected");
            }

            // update score
            $arrow.siblings(".score").text(data.new_score);

        }).fail(function() {
            var userWantsToSignUp = confirm("Please sign up to vote!");
            if (userWantsToSignUp) { window.location = "/accounts/signup"; }
        });
    };
};
