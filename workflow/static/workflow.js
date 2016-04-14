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
            console.log("pk=", pk);

            $.ajax({
                url: '/delete_row_ajax/',
                type: 'POST',
                data: {pk: pk}
            });

            $(this).confirmation('destroy');
            $(this).parents('tr').fadeOut(1000);
        }
    });

});