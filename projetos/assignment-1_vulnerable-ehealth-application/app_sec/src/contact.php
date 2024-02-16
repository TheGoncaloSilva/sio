<?php
  require_once "./database/Database.php";
  require_once("generate_navbar.php");
  session_start();

  include_once("session_expiration.php");
  include_once("./csrf_validate.php");
  
  if(isset($_SESSION['REFRESH'])){
    unset($_SESSION['REFRESH']);
  }else{
    $_SESSION['REFRESH'] = 1;
    generate_token();
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
  <!-- <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/jquery-nice-select/1.1.0/css/nice-select.min.css" integrity="sha256-mLBIhmBvigTFWPSCtvdu6a76T+3Xyt+K571hupeFLg4=" crossorigin="anonymous" /> -->
  <!-- datepicker -->
  <link rel="stylesheet" hhtmlref="https://cdnjs.cloudflare.com/ajax/libs/bootstrap-datepicker/1.3.0/css/datepicker.css">
  <!-- Custom styles for this template -->
  <link href="css/style.css" rel="stylesheet" />
  <!-- responsive style -->
  <link href="css/responsive.css" rel="stylesheet" />
  <script src="js/jquery-3.4.1.min.js"></script>
  <script src="js/bootstrap.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/OwlCarousel2/2.3.4/owl.carousel.min.js"></script>
  <!-- nice select -->
  <!-- <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery-nice-select/1.1.0/js/jquery.nice-select.min.js" integrity="sha256-Zr3vByTlMGQhvMfgkQ5BtWRSKBGa2QlspKYJnkjZTmo=" crossorigin="anonymous"></script> -->
  <!-- datepicker -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap-datepicker/1.3.0/js/bootstrap-datepicker.js"></script>
  <!-- custom js -->
  <script src="js/custom.js"></script>
</head>

<body class="sub_page">
  <div class="hero_area">
    <!-- header section strats -->
    <?php
    require_once("generate_navbar.php");
    $email = null;
    if(isset($_SESSION['userEmail'])){
      $userDB = new users();
      $check = $userDB->select_by_email($_SESSION['userEmail']);
      if($check->num_rows > 0){
        $email = $_SESSION['userEmail'];
      }
    }
    generate_navbar("contact" , $email)?>
    <!-- end header section -->
  </div>
  <?php
    if($_SERVER['REQUEST_METHOD'] == 'GET' && isset($_GET["error"]))
    {
      echo '<div class="modal" tabindex="-1" id="myModal">
              <div class="modal-dialog">
                <div class="modal-content">
                  <div class="modal-header">
                    <h5 class="modal-title">Error</h5>
                  </div>
                  <div class="modal-body">
                    <p>An error has occurred.</p>
                  </div>
                  <div class="modal-footer">
                    <button type="button" class="btn btn-primary" data-dismiss="modal">OK</button>
                  </div>
                </div>
              </div>
            </div>';

      echo "<script>$('#myModal').modal('show');</script>";
    }
  ?>

    <!-- service section -->
    <div class="container w-75 mt-5">
    <form action="<?php echo htmlentities("./contact_save.php"); ?>" method="GET">
      <input type="hidden" name="token" value="<?php echo $_SESSION['csrf_token']; ?>">
        <div class="form-group mt-5">
            <label class="lead">Problem</label>
            <select class="form-control mt-2 w-25" name="error_type">
                <option>Site error</option>
                <option>Medical information</option>
                <option>General question</option>
            </select>
        </div>
        <div class="form-group mt-5">
            <label class="lead">Please explain the problem</label>
            <textarea class="form-control mt-2" rows="7" name="error_info" maxlength="255" required></textarea>
        </div>
        <button type="submit" class="btn btn-primary mt-3 mb-5">Submit</button>
    </form>
</div>

  <!-- end service section -->

  <?php generate_footer() ?>

</body>

</html>