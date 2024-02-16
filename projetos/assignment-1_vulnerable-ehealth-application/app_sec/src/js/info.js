/* info page */
var count = 65.0; // Timer
var redirect = "./index.php"; // Target URL

function countDown() {
    var timer = document.getElementById("timer"); // Timer ID
    if (count > 0) {
        count-=1;
        timer.innerHTML = "This page will redirect in " + count + " seconds."; // Timer Message
        setTimeout("countDown()", 1000);
    } else {
        window.location.href = redirect;
    }
}