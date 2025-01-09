$(document).ready(function() {
    // 初始化 Select2 插件
    $('#studentSelect').select2({
        placeholder: "选择或搜索学生",
        allowClear: true
    });

    // 示例: 选择学生时加载数据
    $('#studentSelect').on('change', function() {
        var studentId = $(this).val();
        // 使用Ajax请求获取学生信息，并填充表单
        // $.ajax({
        //     url: 'your-api-endpoint/' + studentId,
        //     method: 'GET',
        //     success: function(data) {
        //         $('#gender').val(data.gender);
        //         $('#age').val(data.age);
        //         $('#course').val(data.course);
        //         $('#tuition').val(data.tuition);
        //     }
        // });
    });

    // 示例: 提交表单
    $('button').on('click', function() {
        var studentData = {
            gender: $('#gender').val(),
            age: $('#age').val(),
            course: $('#course').val(),
            tuition: $('#tuition').val()
        };
        console.log(studentData); // 这里可以改为通过Ajax发送数据
    });
});
