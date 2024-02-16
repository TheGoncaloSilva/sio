// to get current year
function getYear() {
    var currentDate = new Date();
    var currentYear = currentDate.getFullYear();
    document.querySelector("#displayYear").innerHTML = currentYear;
}

getYear();

// nice select
$(document).ready(function () {
    $('select').niceSelect();
});
var todayDate = new Date();
// date picker
$(function () {
    $("#inputDate").datepicker({
        autoclose: true,
        todayHighlight: true,
        minDate: todayDate
    }).datepicker('update', new Date());

});

/** google_map js **/
function myMap() {
    var mapProp = {
        center: new google.maps.LatLng(40.629540, -8.657072),
        zoom: 18,
    };
    var map = new google.maps.Map(document.getElementById("googleMap"), mapProp);
}