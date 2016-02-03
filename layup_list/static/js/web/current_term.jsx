LayupList.Web.CurrentTerm = function(forLayups) {
    var com = LayupList.Web.Common;
    var ct = LayupList.Web.CurrentTerm;
    ct.upvote = function(courseId, element) { com.vote(1, courseId, element, forLayups); };
    ct.downvote = function(courseId, element) { com.vote(-1, courseId, element, forLayups); };
};
