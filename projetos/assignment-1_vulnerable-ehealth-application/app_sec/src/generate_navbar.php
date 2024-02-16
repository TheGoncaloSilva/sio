<?php

require_once("database/Database.php");


//$page in ['home' , 'about' , 'services' , 'appointment' , 'admin' , 'user_profile']

function generate_nav_item($active , $link , $text)
{
    if($active)
    {
        echo '<li class="nav-item active">
        <a class="nav-link" href="'.$link.'"> '.$text.' </a>
      </li>';
    }
    else{
        echo '<li class="nav-item">
        <a class="nav-link" href="'.$link.'"> '.$text.' </a>
      </li>';
    }
}

function generate_navbar($page , $user_email)
{

    $home_permission = true;
    $about_permission = true;
    $appointment_permission = true;
    $admin_permission = true;
    $user_profile_permission = true;
    $services_permission = true;
    $logout_permission = true;

    $user_name = null;


    $users = new users();
    $user_query = null;
    if($user_email != null)
      $user_query = $users->select_by_email($user_email);
    if($user_email == null or $user_query->num_rows == 0) //render the most basic navbar in this case
    {
        $admin_permission = false;
        $user_profile_permission = false;
        $logout_permission = false;
    }
    else if($user_query != null and $user_query->num_rows == 1){ //logged user
        $row = $user_query->fetch_assoc();
        $role_id = $row["role"];
        $roles = new roles();
        $role_query = $roles->select_by_id($role_id)->fetch_assoc();

        $user_name = $row["first_name"]." ".$row["last_name"];

        $user_role = $role_query["role"];

        if(strcmp($user_role , "admin") != 0)
        {
            $admin_permission = false;
        }

    }
    else{ //duplicate search isn't expected
        $home_permission = false;
        $about_permission = false;
        $appointment_permission = false;
        $admin_permission = false;
        $user_profile_permission = false;
    }

    
    echo '<header class="header_section">
    <div class="container-fluid">
      <nav class="navbar navbar-expand-lg custom_nav-container ">
        <a class="navbar-brand" href="index.php">
          <h3>
            Thrine
          </h3>

        </a>';
        if(isset($user_name))
          echo '<h5 style="margin-left:40px">'.htmlspecialchars($user_name).'</h5>';

        echo '<button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button><div class="collapse navbar-collapse ml-auto" id="navbarSupportedContent">
        <ul class="navbar-nav  ml-auto">';

        if($home_permission)
            generate_nav_item(!strcmp($page , "home") , "index.php" , "Home");
        
        if($about_permission)
            generate_nav_item(!strcmp($page , "about")  , "about.php" , "About");
        
        if($services_permission)
            generate_nav_item(!strcmp($page , "services")  , "service.php" , "Services");
        
        if($admin_permission)
            generate_nav_item(!strcmp($page , "admin") , "admin.php?permission=1" , "Administration");
        
        if($user_profile_permission)
            generate_nav_item(!strcmp($page , "user_profile") , "user.php" , "My profile");
        if($home_permission)
            generate_nav_item(!strcmp($page , "contact") , "contact.php" , "Contact");

        if($logout_permission)
        {
          generate_nav_item(!strcmp($page , "logout") , "logout.php" , "Logout <img src='svg/logout.svg' width='23px'/>");
        }
        else{
          generate_nav_item(!strcmp($page , "logout") , "login.php" , "Login <img src='svg/logout.svg' width='23px'/>");
        }



        echo '</div>
      </nav>
    </div>
  </header>';
}

function generate_footer(){
  echo '
  <!-- info section -->
  <section class="info_section layout_padding">
    <div class="container">
      <div class="row">
        <div class="col-md-3">
          <div class="info_menu">
            <h5>
              QUICK LINKS
            </h5>
            <ul class="navbar-nav  ">
              <li class="nav-item ">
                <a class="nav-link" href="index.php">Home </span></a>
              </li>
              <li class="nav-item">
                <a class="nav-link" href="about.php"> About </a>
              </li>
              <li class="nav-item">
                <a class="nav-link" href="service.php"> Services </a>
              </li>
              <li class="nav-item">
                <a class="nav-link" href="contact.php"> Contact </a>
              </li>
            </ul>
          </div>
        </div>
        <div class="col-md-3">
          <div class="info_course">
            <h5>
              Thrine Hospital
            </h5>
            <p>
              We are a innovative health company, foccused on creating easier and more affordable healthcare
            </p>
          </div>
        </div>

        <div class="col-md-5 offset-md-1">
          <div class="info_news">
            <h5>
              FOR ANY QUERY, PLEASE WRITE TO US
            </h5>
            <div class="info_contact">
              <a href="https://www.ua.pt">
                <i class="fa fa-map-marker" aria-hidden="true"></i> Location
              </a>
              <a href="">
                <i class="fa fa-envelope" aria-hidden="true"></i> Thrine@gmail.com
              </a>
              <a href="">
                <i class="fa fa-phone" aria-hidden="true"></i> Call : +351 1234567890
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- end info section -->

  <!-- footer section -->
  <footer class="container-fluid footer_section">
    <div class="container">
      <p>
        &copy; <span id="displayYear"></span> All Rights Reserved By
        <a href="https://html.design/">Free Html Templates</a>
      </p>
    </div>
  </footer>
  <!-- footer section -->
  ';
}


?>