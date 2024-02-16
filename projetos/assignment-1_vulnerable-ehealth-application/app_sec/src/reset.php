<?php
    session_start();
    
    if(isset($_SESSION['userEmail']) || isset($_SESSION['specialtyID'])) {
		unset($_SESSION['userEmail']);
		unset($_SESSION['specialtyID']);
	}

    if($_SERVER['REQUEST_METHOD'] == 'GET' && isset($_GET["error"]))
    {
        echo '<link rel="stylesheet" type="text/css" href="css/bootstrap.css" />
        <script src="js/jquery-3.4.1.min.js"></script>
                <script src="js/bootstrap.js"></script>';
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
                        <a href="./index.php" class="btn btn-primary">OK</a>
                    </div>
                    </div>
                </div>
                </div>';

        echo "<script>$('#myModal').modal('show');</script>";
        exit(0);
    }


    $server='mysql_db';
    $user='root';
    $password='easyPass123';
    $db = "SIO";
    $con = new mysqli($server,$user,$password);

    $sql = "DROP DATABASE SIO";
    $con->query($sql);

    $sql = "CREATE DATABASE SIO";
    if($con->query($sql) == FALSE)
    {
        header("Localtion: ./reset.php?erro=1");
        exit(1);
    }
    $con->close();

    $con = new mysqli($server,$user,$password,$db);
    $db_path = "./database/mysql_db.sql";
    $templine = '';
    $lines = file($db_path);

    foreach ($lines as $line)
    {
        if (substr($line, 0, 2) == '--' || $line == '')
            continue;

        $templine .= $line;

        if (substr(trim($line), -1, 1) == ';')
        {
            if($con->query($templine) == FALSE)
            {
                header("Location: ./reset.php?error=1");
                exit(1);
            }
            $templine = '';
        }
    }
    $con->close();

    require_once("./database/Database.php");

    $user = new users();

    $pass_default = "1234";
;;
    //NORMAL USERS
    $user->create("Mario","Italiano","luigi@gmail.com",hash('sha512',$pass_default."luigi@gmail.com"),2);
    $user->create("Samuel","Silva","samuel@gmail.com",hash('sha512',$pass_default."samuel@gmail.com"),2);
    $user->create("Papa","Joe","papajoe@gmail.com",hash('sha512',$pass_default."papajoe@gmail.com"),2);

    //MEDICS
    $user->create("Ana","Andrade","ana_andrade@gmail.com",hash('sha512',$pass_default."ana_andrade@gmail.com"),3);
    $user->create("Pedro","Gomes","pedro_doctor@gmail.com",hash('sha512',$pass_default."pedro_doctor@gmail.com"),3);
    $user->create("John","Peterson","john@gmail.com",hash('sha512',$pass_default."john@gmail.com"),3);
    $user->create("Mary","Goodfred","mary@gmail.com",hash('sha512',$pass_default."mary@gmail.com"),3);
    $user->create("Harley","Quinn","harley@asylum.arkham",hash('sha512',$pass_default."harley@asylum.arkham"),3);
    

    //ADMINS
    $user->create("Tiago","Alfredo","tiago@ua.pt",hash('sha512',$pass_default."tiago@ua.pt"),1);
    $user->create("Goncalo","Teixeira","goncalo@ua.pt",hash('sha512',$pass_default."goncalo@ua.pt"),1);
    $user->create('goncalo', 'silva', "gls@ua.pt", hash('sha512',$pass_default."gls@ua.pt"),1);
    

    $spec = new specialties();
    //SPECIALTYS
    $spec->insert("Cardiology");
    $spec->insert("Diagnosis");
    $spec->insert("Surgery");
    $spec->insert("First Aid");
    $spec->insert("Therapy");

    $spec_doc = new specialties_doctors();
    //LINK MEDICS WITH SPECIALTYS
    $spec_doc->insert(4,2);
    $spec_doc->insert(5,1);
    $spec_doc->insert(6,3);
    $spec_doc->insert(7,4);
    $spec_doc->insert(8,5);

    header("Location: ./index.php");
?>