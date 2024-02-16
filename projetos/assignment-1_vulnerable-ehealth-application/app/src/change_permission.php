<?php
    header("Location: admin.php");
    require_once("./database/Database.php");
    $users = new users();
    $users->update_role_using_id($_POST["user_id"] , $_POST["role_id"]);


    if(isset($_POST["speciality_id"]))
    {
        $spec = new specialties_doctors();
        if($spec->select_by_doctors_id($_POST["user_id"])->num_rows == 0)
        {
            $spec->insert($_POST["user_id"] , $_POST["speciality_id"]);
        }
        else{
            $spec->update_using_id($_POST["user_id"] , $_POST["speciality_id"]);
        }
    }
?>

