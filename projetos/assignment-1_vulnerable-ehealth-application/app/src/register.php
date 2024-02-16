<?php
    require_once("./database/Database.php");
    session_start();

    if(isset($_SESSION['userEmail']) || isset($_SESSION['specialtyID'])) {
        unset($_SESSION['userEmail']);
        unset($_SESSION['specialtyID']);
    }
    $msg1 = 0;
    $msg2 = 0;
    $msg3 = 0;
    if($_SERVER['REQUEST_METHOD'] == 'POST' && isset($_POST['register_user'])){
        if(!empty($_POST['first_name']))
            $first_name = $_POST['first_name'];
        else
            header("Location: ./register.php?error=1");

        if(!empty($_POST['last_name']))
            $last_name = $_POST['last_name'];
        else
            header("Location: ./register.php?error=1");

        if(!empty($_POST['email']))
            $email = $_POST['email'];
        else
            header("Location: ./register.php?error=1");

        if(!empty($_POST['password'])){
            $passw = $_POST['password'];
            $passw = hash('md5',$passw);
        }else
            header("Location: ./register.php?error=1");

        if(!empty($_POST['repeat_password'])){
            $rPassw = $_POST['repeat_password'];
            $rPassw = hash('md5',$rPassw);
        }else
            header("Location: ./register.php?error=1");

        if($passw == $rPassw){
            $userDB = new users();
            if($userDB->select_by_email($email)->num_rows == 0){
                $check = $userDB->create($first_name, $last_name, $email, $passw, 2); // Default role for user
                if($check){
                    $_SESSION['userEmail'] = $email;
                    header("Location: ./index.php");
                }else{
                    $msg1 = 0;
                    $problem = "Problem creating user";
                }
            }else
                $msg2 = 1;
                $already_exists = "The account is already registered";
        }else{
            $msg3 = 1;
            $wrong_pass = "Password and Repeat Password doesn't match";
        }
    }

    if($_SERVER['REQUEST_METHOD'] == 'GET' && isset($_GET['error'])){
        $msg1 = 1;
        $problem = "Problem creating user";
    }
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="css/register.css"/>
    <!-- fonts style -->
    <link href="https://fonts.googleapis.com/css?family=Open+Sans:400,700|Poppins:400,600,700&display=swap" rel="stylesheet" />
    <!-- nice select -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/jquery-nice-select/1.1.0/css/nice-select.min.css" integrity="sha256-mLBIhmBvigTFWPSCtvdu6a76T+3Xyt+K571hupeFLg4=" crossorigin="anonymous" />
    <!-- datepicker -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap-datepicker/1.3.0/css/datepicker.css">
    <!-- Custom styles for this template -->
    <link href="css/style.css" rel="stylesheet" />
    <!-- responsive style -->
    <link href="css/responsive.css" rel="stylesheet" />
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.3.1/dist/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
    <title>Register</title>
</head>
<body>
    <div class="container-fluid pl-0 h-100">
        <div class="col-sm-4 p-5 h-100 m-5 mb-5" style="background-color: rgba(249,251,250,255); font-size: 20px;">
            <h5 class="text-center text-black fs-1 m-0" style="font-size: 30px;">
                <span class="dot"></span>
                Register
            </h5>
            <form action="<?php echo $_SERVER['PHP_SELF']; ?>" method="POST">
                <div class="form-group align-items-center">
                    <div class="row ml-0 mr-0">
                        <label for="firstname" class="text-black">First Name</label>
                    </div>
                    <input type="text" id="firstname" class="form-control" style="background-color: #deece9;" name="first_name" required> <!--First Name-->
                </div>
                <div class="form-group">
                    <div class="row ml-0 mr-0">
                        <label for="lastname" class="text-black" >Last Name</label>
                    </div>
                    <input type="text" id="lastname" class="form-control" style="background-color: #deece9;" name="last_name" required>  <!--Last Name-->
                </div>
                <div class="form-group">
                    <div class="row ml-0 mr-0">
                        <label for="email" class="text-black">Email Address</label>
                    </div>
                    <input type="email" id="email" class="form-control" style="background-color: #deece9;" name="email" required>
                </div>
                <div class="form-group">
                    <div class="row ml-0 mr-0">
                        <label for="password" class="text-black">Password</label>
                    </div>
                    <input type="password" id="password" class="form-control" style="background-color: #deece9;" name="password" required>
                </div>
                <div class="form-group">
                    <div class="row ml-0 mr-0">
                        <label for="repeatpassword" class="text-black">Repeat Password</label>
                    </div>
                    <input type="password" id="repeatpassword" class="form-control" style="background-color: #deece9;" name="repeat_password" required> <!-- Repeating the Password-->  
                </div>
                <div class="pt-1">
                    <?php
                        if($msg1 > 0){
                            echo "
                                <div class='alert alert-danger' role='danger'>
                                    ".$problem."
                                </div>
                            ";
                        }
                        elseif($msg2 > 0){
                            echo "
                                <div class='alert alert-danger' role='danger'>
                                    ".$already_exists."
                                </div>
                            ";
                        }
                        elseif($msg3 > 0){
                            echo "
                                <div class='alert alert-danger' role='danger'>
                                    ".$wrong_pass."
                                </div>
                            ";
                        }
                    ?>
                </div>
                <button type="submit" class="btn btn-lg" style="background-color: #35806e; color: white;" name="register_user">Register</button>
                <a href="login.php"><button type="button" class="btn btn-lg mx-1 px-3" style="background-color: #35806e; color: white;">Go Back</button></a>
            </form>
        </div>
    </div>
    <button class="btn btn-outline-primary">Register</button>
              
</body>
</html>