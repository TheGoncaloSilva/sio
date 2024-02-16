<?php
    require_once("./database/Database.php");
    require_once("generate_navbar.php");
    session_start();
	unset($_SESSION['REFRESH1']);
    unset($_SESSION['REFRESH2']);
    unset($_SESSION['REFRESH3']);

	include_once("session_expiration.php");

    if(!isset($_SESSION['userEmail'])) {
      // Maybe trow error of bad credentials or no access
      header("Location: ./index.php");
	  exit(0);
    }

    $userDB = new users();
	$check = $userDB->select_by_email($_SESSION['userEmail']);
	if($check->num_rows == 0){
		// Maybe trow error of bad credentials or no access
		header("Location: ./index.php");
		exit(0);
    }
	$user_email = $_SESSION['userEmail'];
	$user = $check->fetch_assoc();
	$user_perm = $user["role"];

	if($user_perm != 1)
	{
		header("Location: ./index.php");
		exit(0);
	}

	$contacts = new contacts();
	if($_POST && isset($_POST["id"]))
	{
		if(!empty($_POST['id'])){
			$id = strip_tags(trim($_POST['id']));
		}else
            header("Location: ./info.php?type=3");

		if(!validateInputs($id, 'int'))
			header("Location: ./info.php?type=3");
		else
			$contacts->delete_using_id($id);
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
	<link href="css/admin.css" rel="stylesheet" />


	<!-- admin js -->
	<script type="text/javascript" src="js/admin.js"></script>
</head>


<body>
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
      generate_navbar("admin" , $email)?>
	<div class="outer">
		<div class="inner">
			<!--
				Show list of users
			-->
			<h3 style="text-align:center">Manage users</h3>
			<h4 style="text-align:center">(List of platform users)</h4>
	  		
			<table class="table">
				<thead class="thead-light">
					<tr>
						<th scope="col">First name</th>
						<th scope="col">Last name</th>
						<th scope="col">Email</th>
						<th scope="col">Role</th>
						<th scope="col">Manage</th>
					</tr>
				</thead>
				<tbody>

					<?php
					
					$result = $userDB->select_everything();

					if ($result->num_rows > 0) {
						// output data of each row
						while($row = $result->fetch_assoc()) {
						echo "<tr>\n";
						echo "<th scope='row'>".htmlspecialchars($row["first_name"])."</th>\n";
						echo "<td>".htmlspecialchars($row["last_name"])."</td>\n";
						echo "<td>".htmlspecialchars($row["email"])."</td>\n";
						$roles = new roles();
						$role_result = $roles->select_by_id($row["role"]);
						$is_doctor = 0;
						if($role_result->num_rows != 0)
						{
							$role_row = $role_result->fetch_assoc();
							echo "<td>".htmlspecialchars($role_row["role"])."</td>";
							if(strcmp($role_row["role"] , 'employee') == 0)
							$is_doctor =1;
						}
						else if($role_result->num_rows == 0)
						{
							echo "<td>Unknown role</td>";
						}

						echo "<td>\n";
						echo "<button type='button' class='btn btn-info' onclick='admin_manage(".'"'.htmlspecialchars($row['first_name']).'","'.htmlspecialchars($row['last_name']).'","'.htmlspecialchars($row['id']).'",'.htmlspecialchars($is_doctor).")'".' data-toggle="modal" data-target="#exampleModal">'."\n";
						echo '<img src="svg/pen.svg">'."\n";
						echo '</button>'."\n";
						echo "</td>\n";
						

						echo "</tr>\n";
						

						}
					}

					?>

					

					
				</tbody>
			</table>

			<h3 style="text-align:center">Manage reports</h3>
			<h4 style="text-align:center">(List of reports)</h4>

			<table class="table" style="max-width:75vw">
				<thead class="thead-light">
					<tr>
						<th scope="col">Report ID</th>
						<th scope="col">Report type</th>
						<th scope="col">Report information</th>
						<th scope="col">Time</th>
						<th scope="col">Remove report</th>
					</tr>
				</thead>

				<tbody>

					<?php
						$contacts_query = $contacts->select_everything();
						while($row = $contacts_query->fetch_assoc())
						{
							$id = htmlspecialchars($row["id"]);
							$type = htmlspecialchars($row["type"]);
							$information = htmlspecialchars($row["information"]);
							$timestamp = htmlspecialchars($row["timestamp"]);

							echo "<tr>
							<td>".$id."</td>
							<td>".$type."</td>
							<td>".$information."</td>
							<td>".$timestamp."</td>
							<td>
							<form action='".htmlentities($_SERVER['PHP_SELF'])."' id='removeReport' method='POST'>
								<input type='hidden' name='id' value=".$id."> 
							</form>
							<button class='btn btn-danger' form='removeReport' type='submit'>
							<img src='svg/trash.svg' style='width:15px'>
							</button>
							</tr>";

						}

					?>

				</tbody>

		</div>
	</div>


	
	<!-- Modal -->
	<div class="modal fade" id="exampleModal" tabindex="-1" role="dialog" aria-labelledby="exampleModalLabel" aria-hidden="true">
		<div class="modal-dialog" role="document">
		<div class="modal-content">
			<div class="modal-header">
			<h5 class="modal-title" id="exampleModalLabel">
				Edit user information &nbsp;
					<h5>(</h5>
					<h5 id="fname"></h5>&nbsp;<h5></h5><h5 id="lname"></h5><h5>)</h5>
			</h5>
			<button type="button" class="close" data-dismiss="modal" aria-label="Close">
				<span aria-hidden="true">&times;</span>
				</button>
			</div>
			<form action="<?php echo htmlentities("change_permission.php"); ?>" id="form_changes" method="post">
			<div class="modal-body">
				<h6>Change role:</h6>
					<select input name="role_id" class="form-select" aria-label="Default select example" form="form_changes">
					<?php
					$result = $roles->select_everything();
					if($result->num_rows > 0)
					{
						while($row = $result->fetch_assoc())
						{
						echo "<option value=".htmlspecialchars($row["id"]).">".htmlspecialchars($row["role"])."</option>";
						}
					}
					?>
				</select>

				<input type="hidden" name="user_id" value="?" id="user_id">
				
				<div id="doctor_form">
					<h6>Change speciality:</h6>
					<h4></h4>
					<select input name="speciality_id" class="form-select" aria-label="Default select example" form="form_changes">
					<?php

						$specialties = new specialties();
						$result = $specialties->select_everything();
						if($result->num_rows > 0)
						{
						while($row = $result->fetch_assoc())
						{
							echo "<option value=".htmlspecialchars($row["id"]).">".htmlspecialchars($row["name"])."</option>";
						}
						}
						
					?>
					</select>
					</div>
					
			</div>
			<div class="modal-footer">
				<button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
				<button type="submit" form="form_changes" class="btn btn-primary">Save changes</button>
			</div>
			</form>
		</div>
		</div>
	</div>

</body>


</html>




<?php
    unset($userDB);
?>