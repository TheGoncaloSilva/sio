<?php

    require_once("database/Database.php");
    require_once("generate_navbar.php");
    session_start();

    include_once("session_expiration.php");
    include_once("./csrf_validate.php");

    $email = null;
    //echo isset($_SESSION['userEmail']);
    if(isset($_SESSION['userEmail']))
    {
      $email = $_SESSION['userEmail'];
    }
    else
    {
      header("Location: ./index.php");
      exit(0);
    }

    $users = new users();
    $query_users = $users->select_by_email($email)->fetch_assoc();

    $first_name = htmlspecialchars($query_users["first_name"]);
    $last_name = htmlspecialchars($query_users["last_name"]);
    $email = htmlspecialchars($query_users["email"]);
    $image = htmlspecialchars($query_users['image']);
    $roles = new roles();
    $role_query = $roles->select_by_id($query_users["role"])->fetch_assoc();
    $role = htmlspecialchars($role_query["role"]);

    $appointments = new appointments();
    $specialties_doctors = new specialties_doctors();
    $speciality = new specialties();
    $category = "Unknown";
    
    switch($role)
    {
      case 'user': $category = "Patient"; break;
      case 'admin': $category = "Administrator";break;
      case 'employee' : $category = "Doctor";break;
    }

    
    if(strcmp($category , "Doctor") == 0)
      $query_appointments = $appointments->select_using_doctor_id(htmlspecialchars($query_users["id"]));
    else{
      $query_appointments = $appointments->select_using_client_id(htmlspecialchars($query_users["id"]));
    }

    if(isset($_SESSION['REFRESH2'])){
      unset($_SESSION['REFRESH2']);
    }else{
      $_SESSION['REFRESH2'] = 1;
      generate_token();
    }
    
?>


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
        <script src="https://cdn.jsdelivr.net/npm/popper.js@1.12.9/dist/umd/popper.min.js"></script>
        <link rel="stylesheet" type="text/css" href="css/bootstrap.css" />
        <script src="js/jquery-3.4.1.min.js"></script>
        <script src="js/bootstrap.js"></script>
        <link href="https://fonts.googleapis.com/css?family=Open+Sans:400,700|Poppins:400,600,700&display=swap" rel="stylesheet" />
        <!-- nice select -->
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/jquery-nice-select/1.1.0/css/nice-select.min.css" integrity="sha256-mLBIhmBvigTFWPSCtvdu6a76T+3Xyt+K571hupeFLg4=" crossorigin="anonymous" />
        <!-- datepicker -->
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap-datepicker/1.3.0/css/datepicker.css">
        <!-- Custom styles for this template -->
        <link href="css/style.css" rel="stylesheet" />
        <!-- responsive style -->
        <link href="css/responsive.css" rel="stylesheet" />

        <link href="css/user.css" rel="stylesheet" />

        <script src="js/user.js"></script>

        <style>
                .outer {
                    width: 100%;
                    text-align: center;
                }

                .inner {
                    display: inline-block;
                }
                .highlight:hover
                {
                  transition-duration: 0.3;
                  color:#2b2b2b;

                }

                .btn
                {
                  font-size:18px;
                  margin:5px;
                }



        </style>

</head>
  <div class="hero_area">
    <?php generate_navbar("user_profile" , $email); ?>


  
      <div class="container">
    <div class="main-body">
    
          <!-- /Breadcrumb -->
    
          <div class="row gutters-sm">
            <div class="col-md-4 mb-3">
              <div class="card">
                <div class="card-body">
                  <div class="d-flex flex-column align-items-center text-center">
                    <img src=<?php echo ($image == null) ? "https://bootdey.com/img/Content/avatar/avatar7.png" : "./images/user_images/".$image;?> alt="Admin" class="rounded-circle" width="150">
                    <div class="mt-3">
                      <h4><?php echo $first_name." ".$last_name ?></h4>
                      <p class="text-secondary mb-1"><?php echo $category ?></p>
                      <p class="text-muted font-size-sm"></p>
                    </div>
                  </div>
                </div>
              </div>

            </div>
            <div class="col-md-8">
              <div class="card mb-3">
                <div class="card-body">
                  <div class="row">
                    <div class="col-sm-3">
                      <h6 class="mb-0">First name</h6>
                    </div>
                    <div class="col-sm-9 text-secondary">
                      <?php echo $first_name ?>
                    </div>
                  </div>
                  <hr>
                  <div class="row">
                    <div class="col-sm-3">
                      <h6 class="mb-0">Surname</h6>
                    </div>
                    <div class="col-sm-9 text-secondary">
                      <?php echo $last_name ?>
                    </div>
                  </div>
                  <hr>
                  <div class="row">
                    <div class="col-sm-3">
                      <h6 class="mb-0">Email</h6>
                    </div>
                    <div class="col-sm-9 text-secondary">
                      <?php echo $email ?>
                    </div>
                  </div>
                  <hr>
                  <div class="row">
                    <div class="col-sm-3">
                      <h6 class="mb-0">Appointments</h6>
                    </div>
                    <div class="col-sm-9 text-secondary">
                    <?php echo $query_appointments->num_rows ?>
                    </div>
                  </div>
                  <hr>
                  <div class="row">
                    <div class="col-sm-3">
                      <h6 class="mb-0">Role</h6>
                    </div>
                    <div class="col-sm-9 text-secondary">
                    <?php echo $category ?>
                    </div>
                  </div>
                  <hr>
                  <div class="row">
                    <div class="col-sm-3">
                      <h6 class="mb-0">Profile Image</h6>
                    </div>
                    <div class="col-sm-9 text-secondary">
                      <form action="<?php echo htmlentities("./submit_image.php"); ?>" method="POST"  enctype="multipart/form-data">
                        <div class="row">
                          <div class="col-sm-6">
                            <input type="email" value=<?php echo $email; ?> name="user_email" required hidden>
                            <input class="" type="file" id="user_image" name="user_image" accept="image/png, image/jpeg, image/jpg" required>
                          </div>
                          <div class="col-sm-6">
                            <button type="submit" class="btn btn-primary"" name="change_user_image">Change</button>
                          </div>
                        </div>
                      </form>
                    </div>
                  </div>
                  <hr>
                  <?php if(strcmp($category , "Doctor") == 0)
                  {
                    $speciality_query = $specialties_doctors->select_by_doctors_id($query_users["id"])->fetch_assoc();
                    $speciality_id = htmlspecialchars($speciality_query["specialties_id"]);
                    $speciality_name = htmlspecialchars($speciality->select_by_id($speciality_id)->fetch_assoc()["name"]);


                    echo '<div class="row">
                    <div class="col-sm-3">
                      <h6 class="mb-0">Speciality</h6>
                    </div>
                    <div class="col-sm-9 text-secondary">
                      '.$speciality_name.'
                    </div>
                    </div>';
                  }
                    ?>
                  
                  <hr>
                </div>
              </div>





            </div>

            <div class="outer">
              <div class="card mb-3 inner appointment" style='background-color:#ffe7de'>
                <h5>Active appointments</h5>
              </div>
            </div>
            
            <?php


            if(strcmp($category , "Patient") == 0 or strcmp($category , "Administrator") == 0)
            {
              $query_appointments = $appointments->select_using_client_id($query_users["id"]);
              while($row = $query_appointments->fetch_assoc())
              {
                if($row["completed"] == 0)
                {
                  $doctor_query = $users->select_by_id($row["doctors_id"])->fetch_assoc();
                  $doctor_name = htmlspecialchars($doctor_query["first_name"]." ".$doctor_query["last_name"]);
  
                  $date = htmlspecialchars($row["date"]);
                  $confirmed = htmlspecialchars($row["confirmed"]);
                  $completed = htmlspecialchars($row["completed"]);

                  $confirmed_str = $confirmed ? "yes" : "no";
                  $completed_str = $completed ? "yes" : "no";
  
                  $speciality_query = $specialties_doctors->select_by_doctors_id($row["doctors_id"])->fetch_assoc();
                  $speciality_id = htmlspecialchars($speciality_query["specialties_id"]);
                  $speciality_name = htmlspecialchars($speciality->select_by_id($speciality_id)->fetch_assoc()["name"]);
  
                  echo "<div class='outer'>";
                  echo "<div class='card mb-3 inner appointment' style='background-color:#ffe7de'>";
                  echo "<dl class='row highlight' style='margin:0'>";
                  echo "<dt class='col-sm-3'>Speciality</dt><dd class='col-sm-2'>".$speciality_name."</dd><div style='width:100%'></div>";
                  echo "<dt class='col-sm-3'>Doctor</dt><dd class='col-sm-2'>".$doctor_name."</dd><div style='width:100%'></div>";
                  echo "<dt class='col-sm-3'>Date</dt><dd class='col-sm-2'>".$date."</dd><div style='width:100%'></div>";
                  echo "<dt class='col-sm-3'>Confirmed</dt><dd class='col-sm-2'>".$confirmed_str."</dd><div style='width:100%'></div>";
                  echo "<dt class='col-sm-3'>Done</dt><dd class='col-sm-2'>".$completed_str."</dd><div style='width:100%'></div>";
                  echo "<dt class='col-sm-3'>Attachment</dt><dd class='col-sm-2'>
      
                  <div style='min-width:max-content'>
                  <form action='".htmlentities("./open_pdf.php")."' method='get'>
                  <input type='hidden' name='token' value='".$_SESSION['csrf_token']."'>
                  <input type='hidden' name='appointment_id' value='".$row["id"]."'>
                  <input name='code' value='Appointment code ...' maxlength='12' size='12' style='display:inline-block'/input>
                  <button class='btn btn-info' type='submit'><img src='svg/view.svg' width='20px' style='display:inline-block'/></button>
                  </form>
                  </div>
                  
                  </dd><div style='width:100%'></div>";
                  echo "</dl>";
                  echo "</div></div>";
                }
              }
            }
            else if(strcmp($category , "Doctor") == 0)
            {
              $query_appointments = $appointments->select_using_doctor_id($query_users["id"]);
              while($row = $query_appointments->fetch_assoc())
              {
                if($row["completed"] == 0)
                {
                  $patient_query = $users->select_by_id($row["client_id"])->fetch_assoc();
                  $patient_name = htmlspecialchars($patient_query["first_name"]." ".$patient_query["last_name"]);
  
                  $date = htmlspecialchars($row["date"]);
                  $confirmed = htmlspecialchars($row["confirmed"]);
                  $completed = htmlspecialchars($row["completed"]);

                  $confirmed_str = $confirmed ? "yes" : "no";
                  $completed_str = $completed ? "yes" : "no";
  
                  #find speciality
                  
                  $speciality_query = $specialties_doctors->select_by_doctors_id($row["doctors_id"])->fetch_assoc();
                  $speciality_id = htmlspecialchars($speciality_query["specialties_id"]);
                  $speciality_name = htmlspecialchars($speciality->select_by_id($speciality_id)->fetch_assoc()["name"]);

  
                  echo "<div class='outer'>";
                  echo "<div class='card mb-3 inner appointment' style='background-color:#ffe7de'>";
                  echo "<dl class='row highlight' style='margin:0'>";
                  echo "<dt class='col-sm-3'>Speciality</dt><dd class='col-sm-2'>".$speciality_name."</dd><div style='width:100%'></div>";
                  echo "<dt class='col-sm-3'>Patient name</dt><dd class='col-sm-2'>".$patient_name."</dd><div style='width:100%'></div>";
                  echo "<dt class='col-sm-3'>Date</dt><dd class='col-sm-2'>".$date."</dd><div style='width:100%'></div>";
                  echo "<dt class='col-sm-3'>Confirmed</dt><dd class='col-sm-2'>".$confirmed_str."</dd><div style='width:100%'></div>";
                  echo "<dt class='col-sm-3'>Done</dt><dd class='col-sm-2'>".$completed_str."</dd><div style='width:100%'></div>";
                  echo "<dt class='col-sm-3'>Attachment</dt><dd class='col-sm-2'>



                  <form action='".htmlentities("/open_pdf.php")."' method='get'>
                  <input type='hidden' name='token' value='".$_SESSION['csrf_token']."'>
                  <input type='hidden' name='appointment_id' value='".$row["id"]."'>
                  <input name='code' value='".htmlspecialchars($row["code"])."' type='hidden'>
                  <button class='btn btn-info' type='submit'>View <img src='svg/view.svg' width='20px' style='align:center'/></button>
                  </form>
                  
                  </dd><div style='width:100%'></div>";
                  
                  echo "</dl>";
                  if($confirmed == 0)
                  {
                    echo '
                    <form action="'.htmlentities("./confirm_appointment.php").'" method="post">
                    <input type="hidden" name="id" value="'.htmlspecialchars($row["id"]).'">
                    <input type="hidden" name="type" value="confirm">
                    <button input type="submit" class="btn btn-success" style="display:inline-flex">
                    <div style="float:left">
                    Confirm &nbsp;
                  </div>
                  <div style="float:right">
                    <img src="svg/confirm.svg" width="30px"/>
                  </div>
                  </button>
                  </form>';
                  }
                  else if($completed == 0)
                  {

                  echo '<button type="button" onclick="finish_appointment('.htmlspecialchars($row["id"]).')" class="btn btn-success" style="display:inline-flex" type="button" class="btn btn-primary" data-toggle="modal" data-target="#exampleModal">
                      <div style="float:left">
                        Done &nbsp;
                      </div>
                <div style="float:right">
                  <img src="svg/confirm.svg" width="30px"/>
                </div>
                </button>';
                  }
                  echo "</div></div>";
                }
              }
            }
            
            
            
            ?>

            <div class="outer" >
              <div class="card mb-3 inner appointment" style='background-color:#e0ffe2'>
                <h5>Completed appointments</h5>
              </div>
            </div>

            <?php



$specialties_doctors = new specialties_doctors();
$speciality = new specialties();

if(strcmp($category , "Patient") == 0 or strcmp($category , "Administrator") == 0)
{
  $query_appointments = $appointments->select_using_client_id($query_users["id"]);
  while($row = $query_appointments->fetch_assoc())
  {
    if($row["completed"] == 1)
    {
      $doctor_query = $users->select_by_id($row["doctors_id"])->fetch_assoc();
      $doctor_name = htmlspecialchars($doctor_query["first_name"]." ".$doctor_query["last_name"]);

      $date = htmlspecialchars($row["date"]);
      $confirmed = htmlspecialchars($row["confirmed"]);
      $completed = htmlspecialchars($row["completed"]);

      $confirmed_str = $confirmed ? "yes" : "no";
      $completed_str = $completed ? "yes" : "no";

      $speciality_query = htmlspecialchars($specialties_doctors->select_by_doctors_id($row["doctors_id"])->fetch_assoc());
      $speciality_id = htmlspecialchars($speciality_query["specialties_id"]);
      $speciality_name = htmlspecialchars($speciality->select_by_id($speciality_id)->fetch_assoc()["name"]);

      echo "<div class='outer'>";
      echo "<div class='card mb-3 inner appointment' style='background-color:#e0ffe2'>";
      echo "<dl class='row highlight' style='margin:0'>";
      echo "<dt class='col-sm-3'>Speciality</dt><dd class='col-sm-2'>".$speciality_name."</dd><div style='width:100%'></div>";
      echo "<dt class='col-sm-3'>Doctor</dt><dd class='col-sm-2'>".$doctor_name."</dd><div style='width:100%'></div>";
      echo "<dt class='col-sm-3'>Date</dt><dd class='col-sm-2'>".$date."</dd><div style='width:100%'></div>";
      echo "<dt class='col-sm-3'>Confirmed</dt><dd class='col-sm-2'>".$confirmed_str."</dd><div style='width:100%'></div>";
      echo "<dt class='col-sm-3'>Done</dt><dd class='col-sm-2'>".$completed_str."</dd><div style='width:100%'></div>";
      echo "<dt class='col-sm-3'>Attachment</dt><dd class='col-sm-2'>
      
      <div style='min-width:max-content'>
      <form action='".htmlentities("/open_pdf.php")."' method='get'>
      <input type='hidden' name='token' value='".$_SESSION['csrf_token']."'>
      <input type='hidden' name='appointment_id' value='".$row["id"]."'>
      <input name='code' value='Appointment code ...' maxlength='12' size='12' style='display:inline-block'/input>
      <button class='btn btn-info' type='submit'><img src='svg/view.svg' width='20px' style='display:inline-block'/></button>
      </form>
      </div>

      
      </dd><div style='width:100%'></div>";
      echo "</dl>";
      echo "</div></div>";
    }
  }
}
else if(strcmp($category , "Doctor") == 0)
{
  $query_appointments = $appointments->select_using_doctor_id($query_users["id"]);
  while($row = $query_appointments->fetch_assoc())
  {
    if($row["completed"] == 1)
    {
      $patient_query = $users->select_by_id($row["client_id"])->fetch_assoc();
      $patient_name = htmlspecialchars($patient_query["first_name"]." ".$patient_query["last_name"]);

      $date = htmlspecialchars($row["date"]);
      $confirmed = htmlspecialchars($row["confirmed"]);
      $completed = htmlspecialchars($row["completed"]);

      $confirmed_str = $confirmed ? "yes" : "no";
      $completed_str = $completed ? "yes" : "no";

      #find speciality
      
      $speciality_query = $specialties_doctors->select_by_doctors_id($row["doctors_id"])->fetch_assoc();
      $speciality_id = htmlspecialchars($speciality_query["specialties_id"]);
      $speciality_name = htmlspecialchars($speciality->select_by_id($speciality_id)->fetch_assoc()["name"]);

      echo "<div class='outer'>";
      echo "<div class='card mb-3 inner appointment' style='background-color:#e0ffe2'>";
      echo "<dl class='row highlight' style='margin:0'>";
      echo "<dt class='col-sm-3'>Speciality</dt><dd class='col-sm-2'>".$speciality_name."</dd><div style='width:100%'></div>";
      echo "<dt class='col-sm-3'>Patient name</dt><dd class='col-sm-2'>".$patient_name."</dd><div style='width:100%'></div>";
      echo "<dt class='col-sm-3'>Date</dt><dd class='col-sm-2'>".$date."</dd><div style='width:100%'></div>";
      echo "<dt class='col-sm-3'>Confirmed</dt><dd class='col-sm-2'>".$confirmed_str."</dd><div style='width:100%'></div>";
      echo "<dt class='col-sm-3'>Done</dt><dd class='col-sm-2'>".$completed_str."</dd><div style='width:100%'></div>";
      echo "<dt class='col-sm-3'>Attachment</dt><dd class='col-sm-2'>
      
      <form action='".htmlentities("/open_pdf.php")."' method='get'>
      <input type='hidden' name='token' value='".$_SESSION['csrf_token']."'>
      <input type='hidden' name='appointment_id' value='".$row["id"]."'>
      <input name='code' value='".$row["code"]."' type='hidden'> 
      <button class='btn btn-info' type='submit'>View <img src='svg/view.svg' width='20px' style='align:center'/></button>
      </form>
      
      </dd><div style='width:100%'></div>";
      
      echo "</dl>";
      if($confirmed == 0)
      {
        echo '
        <form action="'.htmlentities("confirm_appointment.php").'" method="post">
        <input type="hidden" name="id" value="'.htmlspecialchars($row["id"]).'">
        <input type="hidden" name="type" value="confirm">
        <button input type="submit" class="btn btn-success" style="display:inline-flex">
        <div style="float:left">
        Confirm &nbsp;
      </div>
      <div style="float:right">
        <img src="svg/confirm.svg" width="30px"/>
      </div>
      </button>
      </form>';
      }
      else if($completed == 0)
      {
        /*echo '<form action="confirm_appointment.php" method="post">
        <input type="hidden" name="id" value="'.$row["id"].'">
        <input type="hidden" name="type" value="done">
        <button type="button" class="btn btn-success" style="display:inline-flex" onclick="appointmentDone()"  data-toggle="modal" data-target=".bd-example-modal-sm">
        <div style="float:left">
        Done &nbsp;
      </div>
      <div style="float:right">
        <img src="svg/confirm.svg" width="30px"/>
      </div>
      </button>
      </form>';*/
      echo '<button type="button" class="btn btn-primary" data-toggle="modal" data-target="#exampleModal" onclick="finish_appointment("'.$row["id"].'")">
      <div style="float:left">
      Done &nbsp;
    </div>
    <div style="float:right">
      <img src="svg/confirm.svg" width="30px"/>
    </div>';
      }
      echo "</div></div>";
    }
  }
}


            ?>

          </div>

        </div>
    </div>

<!-- Modal -->
<div class="modal fade" id="exampleModal" tabindex="-1" role="dialog" aria-labelledby="exampleModalLabel" aria-hidden="true">
  <div class="modal-dialog" role="document">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title" id="exampleModalLabel">Appointment description</h5>
        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
      </div>
      <div class="modal-body">
        <div class="md-form">
          <form action="<?php echo htmlentities("./confirm_appointment.php"); ?>" id="doneform" method="post">
          <input type="hidden" id="id" name="id" value="?">
          <input type="hidden" name="type" value="done">
          <textarea name="description" class="md-textarea form-control" rows="3"></textarea>
        </div>
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
        <button type="submit" class="btn btn-primary">Finish appointment</button>
      </div>
    </form>
    </div>
  </div>
</div>

    

  </div>
</body>

