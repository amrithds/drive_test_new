var global_courses = []
$(document).ready(function(){
    $.ajax({
        url: '/v1/course/', // url where to submit the request
        type : "GET", // type of action POST || GET
        dataType : 'json', // data type
        success : function(results) {
            results.results.forEach(function(e) {
                global_courses.push(e.name)
            })
            $('#training_course_id').autocomplete({
                source: global_courses,
            });
        },
        error: function(xhr, resp, text) {
            console.log(xhr, resp, text);
        }
    });
})