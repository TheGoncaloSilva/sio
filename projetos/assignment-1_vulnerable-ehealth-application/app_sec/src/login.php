<?php
	require_once("./database/Database.php");
	session_start();
    unset($_SESSION['REFRESH1']);
    unset($_SESSION['REFRESH2']);
    unset($_SESSION['REFRESH3']);

	if(isset($_SESSION['userEmail']) || isset($_SESSION['specialtyID'])) {
		session_unset();
	}

    $msg = 0;
	if($_SERVER['REQUEST_METHOD'] == 'POST' && isset($_POST['submit_login'])){
		if(!empty($_POST['user_email']))
			$email = strip_tags(trim($_POST['user_email']));
        else
            header("Location: ./login.php?error=1");

		if(!empty($_POST['user_passw']) && validateInputs($email, "email")){
			$passw = strip_tags(trim($_POST['user_passw']));
			$passw = hash('sha512',$passw."".$email);
        }else
            header("Location: ./login.php?error=1");


		$userDB = new users();
		$check = $userDB->check_credentials($email, $passw);
		if($check->num_rows > 0){
			$_SESSION['userEmail'] = $email;
            $_SESSION['LAST_ACTIVITY'] = time();
			header("Location: ./index.php");
		}else{
            $msg = 1;
            $authentication_error = "Wrong Credentials";
		}

	}

    if($_SERVER['REQUEST_METHOD'] == 'GET' && isset($_GET['error'])){
        $msg = 1;
        $authentication_error = "Wrong Credentials";
    }


?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="css/login.css" />
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
    <title>Login</title>
</head>
<body>
    <div class="container-fluid pl-0 pr-0 h-100">
        <div class="row h-100">
            <div class="col-4 h-100"></div>
            <div class="col-4 h-100 d-flex justify-content-center align-items-center">
                <?php /* Use the link to avoid xss or php_self attacks -> https://html.form.guide/php-form/php-form-action-self/ */ ?>
                <form action="<?php echo htmlentities($_SERVER['PHP_SELF']); ?>" method="POST" class="rounded shadow" style="background-color: rgba(249,251,250,255); min-height: 200px; min-width: 250px; width:380px;height:380px">
                    <h1 class="text-dark d-flex justify-content-center align-items-center pt-2">
                        <span class="dot mr-2"></span>
                        Login
                    </h1>
                    <div class="px-3 form-group">
                        <label for="exampleFormControlInput1" class="pt-2 h4 text-dark">Email address</label>
                        <input type="email" class="form-control" style="background-color: #deece9;" id="exampleFormControlInput1" placeholder="name@example.com" name="user_email" required>
                        <label for="exampleFormControlInput1" class="h4 text-dark mt-1">Password</label>
                        <input type="password" class="form-control" style="background-color: #deece9;" id="exampleFormControlInput2" placeholder="password" name="user_passw" required>
                        <div class="pt-2 error-display">
                            <?php
                                if($msg > 0){
                                    echo "
                                        <div class='alert alert-danger' role='danger'>
                                            ".$authentication_error."
                                        </div>
                                    ";
                                }
                            ?>
                        </div>
                        <div class="d-flex justify-content-center">
                            <button type="submit" class="btn btn-lg px-4 mx-1" style="background-color: #35806e; color: white;" name="submit_login">Login</button>
                            <a href="register.php"><button type="button" class="btn btn-lg mx-1 px-3" style="background-color: #35806e; color: white;">Register</button></a>
                        </div>
                        <div class="d-flex justify-content-center mt-1 mr-3">
                            <a href="index.php"><button type="button" class="btn btn-sm" style="background-color: #35806e; color: white;">Go Back</button></a>
                        </div>
                    </div>
                </form>
            </div>
        </div>
    </div>
</body>
</html>