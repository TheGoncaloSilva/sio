<?php
    date_default_timezone_set('Europe/Lisbon');
    require_once("./database/Database.php");


    if($_SERVER['REQUEST_METHOD'] == 'GET' && isset($_GET['error_type']) && isset($_GET['error_info']))
    {
        $contact = new contacts();
        $error_type = $_GET["error_type"];
        $error_info = $_GET["error_info"];
        $contact->insert($error_type,$error_info,date('y-m-d h:i:s', time()));
        header("Location: ./info.php?type=1");
        exit(0);
    }

    header("Location: ./contact.php?error=1");



?>