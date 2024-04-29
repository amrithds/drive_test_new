$(document).ready(function(){
    var user_list_table = $('#user_list').DataTable();

    function addRow(data){
        var user_list_table = $('#user_list').DataTable();
        user_list_table.row.add($(
            `<tr>` +
            `<td>${data.id}</td>` +
            `<td>${data.unique_ref_id}</td>` +
            `<td>${data.rank}</td>` +
            `<td>${data.name}</td>` +
            `<td>${data.unit}</td>` +
            `<td><button class="center-logo-btn delete_user_button" value="${data.id}"><img src="/static/img/icons8-delete-24.png" alt="img"></button></td>` +
            `</tr>`
        )).draw();
    }

    function get_form_data(){
        var data = {}
        data['serial_number'] = $('#serial_number').val()
        data['type'] = $('#type').val()
        data['course'] = $('#course_id').val()
        data['unique_ref_id'] = $('#unique_ref_id').val()
        data['rank'] = $('#rank').val()
        data['unit'] = $('#unit').val()
        data['name'] = $('#name').val()
        console.log(data)
        return data
    }

    function refreshDataTable(course_id){
        var user_list_table = $('#user_list').DataTable();
        user_list_table.clear().draw();;
        $.ajax({
            url: '/v1/user/?course_id='+course_id, // url where to submit the request
            type : "GET", // type of action POST || GET
            dataType : 'json', // data type
            success : function(results) {
                if (results.results.length) {
                    results.results.forEach(function(user) {
                        addRow(user)
                    })
                }
            },
            error: function(xhr, resp, text) {
                console.log(xhr, resp, text);
            }
        });
    }

    $.ajax({
        url: '/v1/course/', // url where to submit the request
        type : "GET", // type of action POST || GET
        dataType : 'json', // data type
        success : function(results) {
            var values = []

            results.results.forEach(function(e) {
                values.push(e.name)
            })
            $('#course_id').autocomplete({
                source: values,
                
                select: function (event, ui) {
                    refreshDataTable(ui.item.value)
                }
            });
        },
        error: function(xhr, resp, text) {
            console.log(xhr, resp, text);
        }
    });

    // click on button submit
    $("#add_user_submit").on('click', function(){
        // send ajax
        $.ajax({
            enctype:'multipart/form-data',
            url: '/v1/user/', // url where to submit the request
            type : "POST", // type of action POST || GET
            dataType : 'json', // data type
            data : get_form_data(), // post data || get data
            success : function(result) {
                // you can see the result from the console
                // tab of the developer tools
                addRow(result);
            },
            error: function(xhr, resp, text) {
                console.log(xhr, resp, text);
            }
        })
    });

    $('#user_list').on('click', '.delete_user_button', function (e) {
        if(confirm("Do you want to delete this user?")){
            $.ajax({
                url: '/v1/user/'+$(this).attr('value'), // url where to submit the request
                type : "DELETE", // type of action POST || GET
                success : function(result) {
                    // you can see the result from the console
                    // tab of the developer tools
                    refreshDataTable($('#course_id').val())
                },
                error: function(xhr, resp, text) {
                    console.log(xhr, resp, text);
                }
            })
            // var table = $('#user_list').DataTable();
            // table
            //     .row($(this).parents('tr'))
            //     .remove()
            // .draw();
        }else{
            return false
        }
	});
    
});

