<?php
	date_default_timezone_set('Europe/Lisbon');
	require_once("./database/Database.php");
    require_once("generate_navbar.php");
	session_start();
	//$_SESSION['userEmail'] = "gls@ua.pt";	// Remove this
    include_once("session_expiration.php");

	/* Check if the specialty received exists */
	if($_SERVER['REQUEST_METHOD'] == 'GET' && isset($_GET['spec'])){
        if(!empty($_GET['spec']))
			$specialtyId = strip_tags(trim($_GET['spec']));
        else
            header("Location: ./appointment.php?spec=".$specialtyId."&msg=3");
        $specialtyDB = new specialties();
        $checkSpeacialty = $specialtyDB->select_by_id($specialtyId);

        /* Check if the specialty received is registered */
        if($checkSpeacialty->num_rows == 0){
            //http_response_code(404); // Not found
            header("Location: info.php?type=3");
            //exit;
        }
        $specialtyName = $checkSpeacialty->fetch_assoc()['name'];

	}elseif($_SERVER['REQUEST_METHOD'] == 'POST' && isset($_POST['specialty_id'])){
        if(!empty($_POST['specialty_id']))
			$specialtyId = strip_tags(trim($_POST['specialty_id']));
        else
            header("Location: ./appointment.php?spec=".$specialtyId."&msg=3");

        $specialtyDB = new specialties();
        $checkSpeacialty = $specialtyDB->select_by_id($specialtyId);

        /* Check if the specialty received is registered */
        if($checkSpeacialty->num_rows == 0){
            //http_response_code(404); // Not found
            header("Location: info.php?type=3");
            //exit;
        }
        $specialtyName = $checkSpeacialty->fetch_assoc()['name'];
    }else{
		header("Location: service.php");
    }

	$userLogged = false;
	$userDB = new users();
	if(isset($_SESSION['userEmail'])){
		$userExists = $userDB->check_email($_SESSION['userEmail']);
		if($userExists->num_rows >= 1){
			$userLogged = true;
			$userID = mysqli_fetch_array($userExists)['id'];
            $user_email = $_SESSION['userEmail'];
		}else
            $user_email = '';
	}else
        $user_email = '';

	$specialtyDoctorDB = new specialties_doctors();
	$appointmentsDB = new appointments();
	if($userLogged && $_SERVER['REQUEST_METHOD'] == 'POST' && isset($_POST['searchAppointment'])){
		if(!empty($_POST['doctor']))
			$doctorId = strip_tags(trim($_POST['doctor']));
        else
            header("Location: ./appointment.php?spec=".$specialtyId."&msg=3");

		if(!empty($_POST['appointment_date']) && validateInputs($doctorId, "int"))
			$bookedDate = strip_tags(trim($_POST['appointment_date']));
        else
            header("Location: ./appointment.php?spec=".$specialtyId."&msg=3");

		$now = strtotime(date("Y-m-d H:i:s"));
		$newDate = strtotime($bookedDate);

		if($newDate <= $now){
			//echo "Can't book an appointment for today or past";
            header("Location: ./appointment.php?spec=".$specialtyId."&msg=1");
		}else{
            
			$doctorsAppointments = $appointmentsDB->select_using_doctor_id($doctorId);
            $dateArray = array();
            while($row = $doctorsAppointments->fetch_assoc()){
                $tempDate = substr($row['date'], 0, 10);
                if($tempDate == $bookedDate)
                    $dateArray[] = $row['date'];
                //echo $tempDate." -> ".$bookedDate;
            }
			//echo "No results";
            //header("Location: ./appointment.php?spec=".$specialtyId."&msg=2");
			
		}
	}

    include_once("./csrf_validate.php");

	if($userLogged && $_SERVER['REQUEST_METHOD'] == 'GET' && isset($_GET['doctor']) && isset($_GET['date'])){
		if(!empty($_GET['doctor']))
			$doctorId = strip_tags(trim($_GET['doctor']));
        else
            header("Location: ./appointment.php?spec=".$specialtyId."&msg=3");

		if(!empty($_GET['date']) && validateInputs($doctorId, "int"))
			$bookedDate = strip_tags(trim($_GET['date']));
        else
            header("Location: ./appointment.php?spec=".$specialtyId."&msg=3");

        
        if(!empty($_GET['token']) || !check_valid_token($_GET['token'])) header("Location: ./appointment.php?spec=".$specialtyId."&msg=5");

        
        //echo $_GET['token']."\n".$_SESSION['csrf_token']; debug
        //die(); debug
        
		/* Check doctor */
		$appointedDoctor = $specialtyDoctorDB->check_doctor_specialty($doctorId, $specialtyId);
		if($appointedDoctor->num_rows == 1){
			$dateExists = $appointmentsDB->select_using_date_doctor_id($bookedDate, $doctorId);
			if($dateExists->num_rows == 0){
				$now = strtotime(date("Y-m-d H:i:s"));
				$newDate = strtotime($bookedDate);

				if($newDate <= $now){
					//echo "Can't book an appointment for today or past";
                    header("Location: ./appointment.php?spec=".$specialtyId."&msg=1");
				}else{
					if($appointmentsDB->insert($doctorId, $userID, 0, 0, $bookedDate)){
                        $inserted = $appointmentsDB->select_using_date($bookedDate)->fetch_assoc();
						//echo "Redirecting";
						header("Location: ./info.php?type=1&code=".$inserted['code']);
					}else{
						//echo "Error with Booking Appointment";
                        header("Location: ./appointment.php?spec=".$specialtyId."&msg=3");
					}
				}
			}else{
				//echo "You have been messing with date URL";
				header("Location: ./appointment.php?spec=".$specialtyId."&msg=4");
			}
		}else{
			//echo "You have been messing with URLS";
            header("Location: ./appointment.php?spec=".$specialtyId."&msg=5");
		}
	}

    if(isset($_SESSION['REFRESH3'])){
        unset($_SESSION['REFRESH3']);
    }else{
        $_SESSION['REFRESH3'] = 1;
        generate_token();
    }

    /* Warning handler */
    $msg = 0;
    if($_SERVER['REQUEST_METHOD'] == 'GET' && isset($_GET['msg'])){
        // 1 - Can't book an appointment for today or past
        // 2 - No results
        // 3 - Error with Booking Appointment
        // 4 - Date doesn't seem right
        // 5 - Error occurred
        if(!empty($_GET['msg']))
			$msg = htmlspecialchars($_GET['msg']);
            if(!validateInputs($msg, "int")) $msg = 5;
            if($msg <= 0 || $msg > 5)
                $msg = 0;
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
    <!-- responsive style -->
    <link href="css/responsive.css" rel="stylesheet" />
</head>

<body class="sub_page">
    <div class="hero_area">
        <!-- header section strats -->
        <?php generate_navbar("appointment" , $user_email)?>
        <!-- end header section -->
    </div>

    <!-- book section -->

    <section class="book_section layout_padding">
        <div class="container">
            <div class="row">
                <?php
                    if(isset($dateArray) || $msg)
                        echo "<div class='col-sm-8'>";
                    else
                        echo "<div class='col-sm-12'>";
                ?>
                
					<?php /* Use the link to avoid xss or php_self attacks -> https://html.form.guide/php-form/php-form-action-self/ */ ?>
                    <form action="<?php echo htmlentities($_SERVER['PHP_SELF']); ?>" method="POST">
                        <h4>
                            <span class="design_dot"></span>
                            BOOK APPOINTMENT <?php echo "(".htmlspecialchars($specialtyName).")"; ?>
                        </h4>
                        <div class="form-row ">
                            <input type="number" name="specialty_id" required hidden value="<?php echo $specialtyId; ?>">
                            <div class="form-group col-lg-6">
                                <label for="inputDoctorName">Doctor's Name</label>
                                <select name="doctor" class="form-control wide" id="inputDoctorName" required>
									<?php
										$doctors = $specialtyDoctorDB->select_by_specialties_id($specialtyId);
										if($doctors->num_rows > 0){
											while($row = $doctors->fetch_assoc()){
												$doctor_info = $userDB->select_using_id($row['doctors_id']);
												$doctor_info = $doctor_info->fetch_assoc();
												echo "<option value='".htmlspecialchars($doctor_info['id'])."'>".htmlspecialchars($doctor_info['first_name'])." ".htmlspecialchars($doctor_info['last_name'])."</option>";
											}
										}
									?>
                                </select>
                            </div>
							<div class="form-group col-lg-6">
                                <label for="inputDate">Choose Date </label>
                                <div class="input-group date" id="inputDate" data-date-format="yyyy-mm-dd">
                                    <input type="text" name="appointment_date" class="form-control" required"> <!-- TO DO -> lock past dates -->
                                    <span class="input-group-addon date_icon">
                                        <i class="fa fa-calendar" aria-hidden="true"></i>
                                    </span>
                                </div>
                            </div>
                        </div>
                        <div class="btn-box">
                            <button type="submit" class="btn" name="searchAppointment" <?php if(!$userLogged) echo "disabled title='To schedule or check appointment slots, please log in'";?>>
								Search
							</button>
                        </div>
                    </form>
                </div>
				    <?php
					if(isset($dateArray)){
						echo "<div class='col-sm-4 mt-4 mt-md-0'>
								<table class='table table-light table-striped'>
									<thead>
										<tr>
											<th scope='col'>Time</th>
											<th scope='col'>".htmlspecialchars($bookedDate)."</th>
										</tr>
									</thead>
									<tbody>
							";
						$arrIndex = 0;
						for($i = 9; $i < 18; $i++){
							if(!isset($dateArray[$arrIndex]) || !(substr($dateArray[$arrIndex], 11, 2) == $i)){
								$newDate = $bookedDate." ".$i.":00:00";
								echo "<tr>
										<th scope='row'>".$i.":00</th>
										<td>
											<a class='btn btn-outline-dark' role='button' href='?spec=".htmlspecialchars($specialtyId)."&doctor=".htmlspecialchars($doctorId)."&date=".htmlspecialchars($newDate)."&token=".$_SESSION['csrf_token']."' >BOOK</a>
										</td>
									</tr>";
							}else
								$arrIndex++;
						}

						if(count($dateArray) == 9){
							echo "<tr>
									<td colspan = '2'>
										No results
									</td>
								</tr>";
						}

						echo "</tbody>
							</table>
							</div>
							";
					}elseif($msg){
                        echo "<div class='col-sm-4 mt-4 mt-md-0'>";
                        switch ($msg) {
                            case 1:
                                echo "
                                    <div class='alert alert-warning' role='alert'>
                                    <strong>Warning:</strong> Can't book an appointment for today or past
                                    </div>
                                    ";
                                break;
                            case 2:
                                echo "
                                    <div class='alert alert-info' role='alert'>
                                    <strong>Info:</strong> No results
                                    </div>
                                    ";
                                break;
                            case 3:
                                echo "
                                    <div class='alert alert-danger' role='alert'>
                                    <strong>Error:</strong> Error with Booking Appointment
                                    </div>
                                    ";
                                break;
                            case 4:
                                echo "
                                    <div class='alert alert-danger' role='alert'>
                                    <strong>Error:</strong> Date doesn't seem right
                                    </div>
                                    ";
                                break;
                            case 5:
                                echo "
                                    <div class='alert alert-danger' role='alert'>
                                    <strong>Error:</strong> Please Try again
                                    </div>
                                    ";
                                break;
                            default:
                                break;
                        }
                        echo "</div>";
                    }
				?>
				<!--<div class="col-4">
					<table class="table table-success table-striped">
						<thead>
							<tr>
								<th scope="col">Time</th>
								<th scope="col">Tuesday</th>
							</tr>
						</thead>
						<tbody>
                            <tr>
								<th scope="row">09:00</th>
								<td><a class="btn btn-primary" href="#" role="button">Link</a></td>
							</tr>
							<tr>
								<th scope="row">09:30</th>
								<td>Yes</td>
							</tr>
						</tbody>
					</table>
				</div>-->
            </div>
        </div>
    </section>

    <!-- end book section -->

    <!-- comment section 

    <section class="map_section">
        <div class="container">
			<div class="row">
				<div class="col-md-4">
						Cycle doctors
				</div>
				<div class="col-md-8">
						Show Comments
				</div>
			</div>
        </div>
    </section>-->

    <!-- end map section -->

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
</body>

</html>
<?php
    
?>