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
        onConfirm: function(event, element) {
            var pk = $(this).attr('id');
            row = $(this).parents('tr');

            $.ajax({
                url: '/delete_row_ajax/',
                type: 'POST',
                data: {pk: pk},
                dataType : 'json'
            })
                .done(function(json) {
                row.fadeOut(1000);
                $("#snoAlertBox")
                    .addClass("alert-success")
                    .text('Заказ '+ json['order'] + ' успешно удален')
                    .fadeIn();
                closeSnoAlertBox();
            })
                .fail(function() {
                $("#snoAlertBox")
                    .addClass("alert-danger")
                    .text('Для удаления нужно войти в систему.')
                    .fadeIn();
                closeSnoAlertBox();
            });

            $(this).confirmation('destroy');
        }
    });

});

function closeSnoAlertBox(){
	window.setTimeout(function () {
  	$("#snoAlertBox").fadeOut(300)
	}, 3000);
} 