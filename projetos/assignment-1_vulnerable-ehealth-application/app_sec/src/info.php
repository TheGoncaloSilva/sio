<?php
    session_start();
    unset($_SESSION['REFRESH1']);
    unset($_SESSION['REFRESH2']);
    unset($_SESSION['REFRESH3']);

    include_once("session_expiration.php");

    /* Type:
     1-success
     2-errorCode
     3-Error db Connection
     4-User entered wrong appointment code
     5-File upload problem
     6-Other errors
     */

    $eCode = http_response_code();
    if($eCode != 200){
        $type = 2;
        $message = "UPS! Server responded with".$eCode;
    }elseif($_SERVER['REQUEST_METHOD'] == 'GET' && isset($_GET['type'])){
        if(!empty($_GET['type']) && $_GET['type'] >= 1 && $_GET['type'] <= 5){
            $type = $_GET['type'];
            if($type == 1){
                $message = "The operation was registered";
                if(isset($_GET['code']))
                    $message = "Booking saved with code <a title='Please save the code'><i class='fa fa-question-circle fa-2x' aria-hidden='true'></i></a> ".$_GET['code'];
            }elseif($type == 2)
                $message = "UPS! Server responded with ".$eCode;
            elseif($type == 3){
                $message = "ERROR! Server ERROR";
                unset($_SESSION['csrf_token']);
            }elseif($type == 4)
                $message = "ERROR! Invalid code entered";
            elseif($type == 5)
                $message = "UPS! Your file had a problem";
            else
                $message = "ERROR! Please try again";
        }else{
            $type = 6;
            $message = "ERROR! Url has been altered";
        }
    }else{
        header("Location: index.php");
    }
?>

<!DOCTYPE html>
<html>

<head>
    <!-- Basic -->
    <meta charset="utf-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <!-- Mobile Metas -->
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no" />
    <!-- Site Metas -->
    <meta name="keywords" content="" />
    <meta name="description" content="" />
    <meta name="author" content="" />
    <link rel="shortcut icon" href="images/s4.png" type="image/x-icon">

    <title>Thrine</title>

    <!-- bootstrap core css -->
    <link rel="stylesheet" type="text/css" href="css/bootstrap.css" />

    <!-- fonts style -->
    <link href="https://fonts.googleapis.com/css?family=Open+Sans:400,700|Poppins:400,600,700&display=swap" rel="stylesheet" />
    <!-- nice select -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/jquery-nice-select/1.1.0/css/nice-select.min.css" integrity="sha256-mLBIhmBvigTFWPSCtvdu6a76T+3Xyt+K571hupeFLg4=" crossorigin="anonymous" />
    <!-- datepicker -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap-datepicker/1.3.0/css/datepicker.css">
    <!-- Custom styles for this template -->
    <link href="css/style.css" rel="stylesheet" />
    <!-- font awesome icons -->
    <link href="css/font-awesome.min.css" rel="stylesheet" />
    <!-- responsive style -->
    <link href="css/responsive.css" rel="stylesheet" />

	<link href="css/info.css" rel="stylesheet" />
	<!-- custom js -->
	<script src="js/info.js"></script>
</head>

<body onload="countDown()">
	<div id="master-wrap">
        <?php
            if($type == 1){
                echo "
                    <div id='logo-box'>
                    <div class='animated fast fadeInUp'>
                    <div class='icon' style='background: url(./images/icon_success.svg) no-repeat center center;'></div>
                    <h1>Thank you</h1>
                    ";
            }elseif($type == 2){
                echo "
                    <div id='logo-box' style='border: 3px solid #ff5576;'>
                    <div class='animated fast fadeInUp'>
                    <div class='icon' style='background: url(./images/icon_error.svg) no-repeat center center;'></div>
                    <h1>Error occurred</h1>
                    ";
            }else{
                echo "
                    <div id='logo-box' style='border: 3px solid #ff5576;'>
                    <div class='animated fast fadeInUp'>
                    <div class='icon' style='background: url(./images/icon_error.svg) no-repeat center center;'></div>
                    <h1>Error occurred</h1>
                    ";
            }
        ?>
		
		</div>

		<div class="notice animated fadeInUp">
		<p class="lead"><?php echo $message; ?></p>
		<a class="btn animation" href="./index.php" <?php if($type != 1) echo "style='border: 2px solid #ff5576;background: #ff5576;'";?>>Home</a>
        </div>

		<div class="footer animated slow fadeInUp">
		<p id="timer">
		</p>
		<!--<p class="copyright">&copy; Redfrost.com</p>-->
        <!--<a target="_blank" href="https://icons8.com/icon/HxdOcoesMKEc/ok">Ok</a> icon by <a target="_blank" href="https://icons8.com">Icons8</a>-->
		</div>

	</div>
	<!-- /#logo-box -->
	</div>
	<!-- /#master-wrap -->

    <script src="js/jquery-3.4.1.min.js"></script>
    <script src="js/bootstrap.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/OwlCarousel2/2.3.4/owl.carousel.min.js"></script>
    <!-- nice select -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery-nice-select/1.1.0/js/jquery.nice-select.min.js" integrity="sha256-Zr3vByTlMGQhvMfgkQ5BtWRSKBGa2QlspKYJnkjZTmo=" crossorigin="anonymous"></script>
    <!-- datepicker -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap-datepicker/1.3.0/js/bootstrap-datepicker.js"></script>
</body>

</html>
<!-- A lot of this code can be credited to https://codepen.io/redfrost/pen/KzegWQ */

<?php
        //require_once("./database/close-connection.ini")
?>