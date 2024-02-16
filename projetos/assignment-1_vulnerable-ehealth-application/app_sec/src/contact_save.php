<?php
    session_start();
    unset($_SESSION['REFRESH1']);
    unset($_SESSION['REFRESH2']);
    unset($_SESSION['REFRESH3']);
    date_default_timezone_set('Europe/Lisbon');
    require_once("./database/Database.php");
    include_once("./csrf_validate.php");


    if($_SERVER['REQUEST_METHOD'] == 'GET' && isset($_GET['error_type']) && isset($_GET['error_info']))
    {
        if(!empty($_GET['error_info']) && !empty($_GET['error_type']) && !empty($_GET['token'])){
			$error_info = strip_tags(trim($_GET['error_info']));
			$error_type = strip_tags(trim($_GET['error_type']));
            $token = $_GET['token'];
        }else{
            header("Location: ./contact.php?error=1");
        }

        if(!check_valid_token($token)){
            unset($_SESSION['csrf_token']);
            header("Location: ./contact.php?error=1");
            exit(1);
        }
        
        $contact = new contacts();
        if(!$contact->insert($error_type,$error_info,date('y-m-d h:i:s', time()))){
            header("Location: ./contact.php?error=1");
            exit(1);
        }
        header("Location: ./info.php?type=1");
        exit(0);
    }

    header("Location: ./contact.php?error=1");



?>