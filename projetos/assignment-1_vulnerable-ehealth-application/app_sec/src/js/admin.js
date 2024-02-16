function admin_manage(fname , lname , id , isDoctor)
{
    $('#fname').html(fname);
    $('#lname').html(lname);
    $('#user_id').val(id);
    if(isDoctor != 0)
        $("#doctor_form").show();
    else{
        $("#doctor_form").hide();
    }
}

$('#myModal').on('shown.bs.modal', function () {
    $('#myInput').trigger('focus')
  })


  $('.dropdown-toggle').dropdown()