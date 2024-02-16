<?php
    header("Location: user.php");
    require_once("./database/Database.php");
    #$users = new users();
    #$users->update_role_using_id($_POST["user_id"] , $_POST["role_id"]);


    if(isset($_POST["id"]) and isset($_POST["type"]))
    {
        $appointments = new appointments();
        switch($_POST["type"])
        {
            case "confirm":
            $appointments->set_confirmed_by_id($_POST["id"]);
            break;

            case "done":
            $text = $_POST["description"];
            $appointments->set_report_text_using_id($_POST["id"] , $text);
            $appointments->set_done_by_id($_POST["id"]);
            break;
        }
    } 
?>

