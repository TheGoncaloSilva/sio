<?php
    header("Location: admin.php");
    session_start();
    unset($_SESSION['REFRESH1']);
    unset($_SESSION['REFRESH2']);
    unset($_SESSION['REFRESH3']);
    require_once("./database/Database.php");
    $users = new users();
    if(isset($_SESSION['userEmail'])){ // user is not logged in
        if(!empty($_POST['user_id']))
			$userId = strip_tags(trim($_POST['user_id']));
        else
            header("Location: ./info.php?type=3");
        
        if(!empty($_POST['role_id']))
			$roleId = strip_tags(trim($_POST['role_id']));
        else
            header("Location: ./info.php?type=3");

        if(!validateInputs($userId, 'int') || !validateInputs($roleId, 'int')) header("Location: ./info.php?type=3");

        $users->update_role_using_id($userId , $roleId);

        if(isset($_POST["speciality_id"]))
        {
            if(!empty($_POST['speciality_id']))
			    $specId = strip_tags(trim($_POST['speciality_id']));
            else
                header("Location: ./info.php?type=3");
            
            if(!validateInputs($specId, 'int')) header("Location: ./info.php?type=3");

            $spec = new specialties_doctors();
            if($spec->select_by_doctors_id($userId)->num_rows == 0)
            {
                $spec->insert($userId , $specId);
            }
            else{
                $spec->update_using_id($userId , $specId);
            }
        }
    }
?>

