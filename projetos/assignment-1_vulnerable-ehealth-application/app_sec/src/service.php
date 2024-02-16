<?php
  require_once "./database/Database.php";
  require_once("generate_navbar.php");
  session_start();
  unset($_SESSION['REFRESH1']);
  unset($_SESSION['REFRESH2']);
  unset($_SESSION['REFRESH3']);
  include_once("session_expiration.php");

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
  <link rel="stylesheet" hhtmlref="https://cdnjs.cloudflare.com/ajax/libs/bootstrap-datepicker/1.3.0/css/datepicker.css">
  <!-- Custom styles for this template -->
  <link href="css/style.css" rel="stylesheet" />
  <!-- responsive style -->
  <link href="css/responsive.css" rel="stylesheet" />
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
    generate_navbar("services" , $email)?>
    <!-- end header section -->
  </div>

  <!-- service section -->

  <section class="service_section layout_padding">
    <div class="container">
      <div class="heading_container heading_center">
        <h2>
          <span class="design_dot"></span>
          Our Services
        </h2>
      </div>
      <?php

        $spec = new specialties();
        $all = $spec->select_everything();

        if($all->num_rows > 0)
        {
          echo '
          <form method="GET" action="'.htmlentities("./appointment.php").'"><div class="row">';

          while($row = $all->fetch_assoc())
          {
            echo '<div class="col-md-4 mx-auto">
                    <div class="box">
                    <button class="btn" name="spec" type="submit" value="'.htmlspecialchars($row["id"]).'">
                      <img src="./images/'.htmlspecialchars($row["name"]).'.png"/>
                      <p>'.htmlspecialchars($row["name"]).'</p>
                    </button>
                    </div>
                  </div>';

          }

          echo "</div></form>";
        }

      ?>
      <!-- <div class="row">
      </div> -->
        <!-- <div class="row">
        <div class="col-md-2">

        </div>
        <div class="col-md-4 mx-auto">
          <div class="box">
            <img src="images/s1.png" alt="" />
            <a href="#">
              Cardiology
            </a>
          </div>
        </div>
        <div class="col-md-4 mx-auto">
          <div class="box">
            <img src="images/s2.png" alt="" />
            <a href="#">
              Diagnosis
            </a>
          </div>
        </div>
        <div class="col-md-2">

        </div>
        <div class="col-md-4 mx-auto">
          <div class="box">
            <img src="images/s3.png" alt="" />
            <a href="#">
              Surgery
            </a>
          </div>
        </div>
        <div class="col-md-4 mx-auto">
          <div class="box">
            <img src="images/s4.png" alt="" />
            <a href="#">
              First Aid
            </a>
          </div>
        </div>
        <div class="col-md-4 mx-auto">
          <div class="box">
            <img src="images/s5.png" alt="" />
            <a href="#">
              Therapy
            </a>
          </div>
        </div>
      </div>
      <div class="btn-box">
        <a href="">
          View All
        </a>
      </div> -->
    </div>
  </section>

  <!-- end service section -->


  <?php generate_footer() ?>

  <script src="js/jquery-3.4.1.min.js"></script>
  <script src="js/bootstrap.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/OwlCarousel2/2.3.4/owl.carousel.min.js"></script>
  <!-- nice select -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery-nice-select/1.1.0/js/jquery.nice-select.min.js" integrity="sha256-Zr3vByTlMGQhvMfgkQ5BtWRSKBGa2QlspKYJnkjZTmo=" crossorigin="anonymous"></script>
  <!-- datepicker -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap-datepicker/1.3.0/js/bootstrap-datepicker.js"></script>
  <!-- custom js -->
  <script src="js/custom.js"></script>
  <!-- Google Map -->
  <script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyCh39n5U-4IoWpsVGUHWdqB6puEkhRLdmI&callback=myMap">
  </script>
  <!-- End Google Map -->
</body>

</html>