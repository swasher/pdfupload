$(document).ready(function() {

    $("[data-toggle='tooltip']").tooltip();


    $('[data-toggle="confirmation"]').confirmation({
        title: "Are you sure to remove?",
        placement: "left",
        singleton: "True",
        popout: "True",
        container: 'body',
        btnOkLabel: "&nbsp;Delete",
        btnOkClass: "btn-xs btn-danger",
        btnOkIcon: "glyphicon glyphicon-remove",
        btnCancelLabel: "&nbsp;Cancel",
        btnCancelIcon: "glyphicon glyphicon-repeat",
        rootSelector: '[data-toggle=confirmation]',
        onConfirm: function (event, element) {
            var pk = $(this).attr('id');
            row = $(this).parents('tr');

            $.ajax({
                    url: '/delete_row_ajax/',
                    type: 'POST',
                    data: {pk: pk},
                    dataType: 'json'
                })
                .done(function (json) {
                    row.fadeOut(1000);
                    $("#snoAlertBox")
                        .addClass("alert-success")
                        .text('Заказ ' + json['order'] + ' успешно удален')
                        .fadeIn();
                    closeSnoAlertBox();
                })
                .fail(function () {
                    $("#snoAlertBox")
                        .addClass("alert-danger")
                        .text('Вы должны авторизироваться.')
                        .fadeIn();
                    closeSnoAlertBox();
                });

            $(this).confirmation('destroy');
        }
    });

    // Submit через ajax выполняется только после нажатия на кнопку #ajaxprint
    $('#ajaxprint').click(function () {

        // this is the id of the form
        $("#id_datetime").submit(function (e) {
            var url = "/grid/printing"; // the script where you handle the form input.
            var w = window.open();
            $.ajax({
                type: "GET",
                url: url,
                data: $("#id_datetime").serialize(), // serializes the form's elements
                dataType: 'html',
                success: function (data) {
                    if (data){
                        console.log(data);
                        w.document.write(data);
                        w.document.close();
                        w.focus();
                        w.print();
                        w.close();
                        location.reload();
                    }
                }
                ,error: function() {
                    alert('Ajax errror!')
                }

            });
            e.preventDefault(); // avoid to execute the actual submit of the form.
        });
    });

});


function closeSnoAlertBox() {
    window.setTimeout(function () {
        $("#snoAlertBox").fadeOut(300)
    }, 3000);
}
