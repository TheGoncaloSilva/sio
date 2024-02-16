<?php
    require_once("./database/Database.php");
    /* permissions were needed to grand ownsership of images/user_images folder
     * echo exec('whoami'); -> run it and see who is the user that accesses the folder
     * chown user destination_dir -> add the user as owner
     * chmod 755 destination_dir -> change permissions
    */

    if($_SERVER['REQUEST_METHOD'] == 'POST' && isset($_POST['change_user_image'])){
        if(!empty($_POST['user_email']))
			$userEmail = htmlspecialchars($_POST['user_email']);
        $userDb = new users();
        $checkUser = $userDb->check_email($userEmail);

        /* Check if the email received is registered */
        if($checkUser->num_rows == 0){
            header("Location: info.php?type=3");
        }
        $query_users = $checkUser->fetch_assoc(); 
        $userImg = $query_users['image'];
        $userName = $query_users['first_name'];
        
        $path = $_FILES['user_image']['name'];
		$tempPath = $_FILES['user_image']['tmp_name'];
        $directory = "./images/user_images/";
        $create = false;
        $explode = (explode('.',$path));
        $cond = $explode[sizeof($explode)-1];

        if($cond == "png" || $cond == "jpeg" || $cond == "jpg"){
            if($userImg == null && !empty($path)){// New image upload
                $path = $userName.time().'.'.$explode[1];
                $create = move_uploaded_file($tempPath, $directory."".$path);
            }else if(!empty($path)){ // update existing image
                $path = $userName.time().'.'.$explode[1];
                $create = move_uploaded_file($tempPath, $directory."".$path);
                unlink($directory."".$userImg);
            }else{
                header("Location: info.php?type=3");
            }

            if($create){
                if($userDb->upload_image($userEmail, $path))
                    header("Location: user.php");
                else
                    header("Location: info.php?type=3");
            }else{
                header("Location: info.php?type=5");
            }
        }else{
            header("Location: info.php?type=5");
        }
    }


?>