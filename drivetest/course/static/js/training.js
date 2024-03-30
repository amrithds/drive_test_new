$(document).ready(function(){
    $.ajax({
        url: 'v1/course/', // url where to submit the request
        type : "GET", // type of action POST || GET
        dataType : 'json', // data type
        success : function(results) {
            var values = []

            results.results.forEach(function(e) {
                values.push(e.name)
            })
            $('#training_course_id').autocomplete({
                source: values,
            });
        },
        error: function(xhr, resp, text) {
            console.log(xhr, resp, text);
        }
    });

    function populate_user_inputs(user_type,inputs) {
        $(`#${user_type}_name`).val(inputs.name)
        $(`#${user_type}_rank`).val(inputs.rank)
        $(`#${user_type}_unit`).val(inputs.unit)
    }

    function fetch_user_data(user_type, user_type_prefix) {
        if ($(`#${user_type_prefix}_unique_id`).val().length > 2 && $('#training_course_id').val().length > 0) {
            $.ajax({
                url: `v1/user/?unique_ref_id=`+$(`#${user_type_prefix}_unique_id`).val()+'&course_id='+$('#training_course_id').val()+'&type='+user_type, // url where to submit the request
                type : "GET", // type of action POST || GET
                dataType : 'json', // data type
                success : function(results) {
                    if (results.results.length > 0) {
                        user = results.results[0]
                        populate_user_inputs(user_type_prefix ,user)
                    }
                },
                error: function(xhr, resp, text) {
                    console.log(xhr, resp, text);
                }
            });
        }
    }

    $('#training_trainer_unique_id').on('input', function(){
        fetch_user_data(2, 'training_trainer')
    });

    $('#training_trainee_unique_id').on('input', function(){
        fetch_user_data(1, 'training_trainee')
    });
})