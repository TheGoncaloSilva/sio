<?php
    //
    require_once("./database/Database.php");
    session_start();
    unset($_SESSION['REFRESH1']);
    unset($_SESSION['REFRESH2']);
    unset($_SESSION['REFRESH3']);
    $users = new users();
    #$users->update_role_using_id($_POST["user_id"] , $_POST["role_id"]);


    if(isset($_SESSION['userEmail']) && isset($_POST["id"]) and isset($_POST["type"]))
    {
        if(!empty($_POST['id']))
			$id = strip_tags(trim($_POST['id']));
        else
            header("Location: ./info.php?type=2");

        if(!empty($_POST['type']) && validateInputs($id, 'int'))
			$type = strip_tags(trim($_POST['type']));
        else
            header("Location: ./info.php?type=2");

        $appointments = new appointments();
        $appCheck = $appointments->select_using_id($id);

        if($appCheck->num_rows == 0) header("Location: ./info.php?type=2");

        $appCheck = $appCheck->fetch_assoc();

        $check = $users->select_by_id($appCheck['doctors_id']);
        
        if($check->num_rows == 0 || $check->fetch_assoc()["email"] != $_SESSION['userEmail']) header("Location: ./info.php?type=2");

        $cond = false;
        switch($type)
        {
            case "confirm":
                $cond = $appointments->set_confirmed_by_id($id);
                break;

            case "done":
                if(!empty($_POST['description']))
                    $text = strip_tags(trim($_POST['description']));
                else
                    header("Location: ./info.php?type=2");

                $cond = $appointments->set_report_text_using_id($id , $text);
                $cond = $appointments->set_done_by_id($id);
            break;
        }
        if($cond)
            header("Location: user.php");
        else
            header("Location: ./info.php?type=2");
    } 
?>

