function finish_appointment(appointment_id)
{
    $('#id').val(appointment_id);
}

$('#myModal').on('shown.bs.modal', function () {
    $('#myInput').trigger('focus')
  })


  $('.dropdown-toggle').dropdown()