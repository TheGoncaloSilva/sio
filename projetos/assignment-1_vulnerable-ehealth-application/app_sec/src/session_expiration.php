<?php
    $session_max_time = 180; // 3 minutes
    if(isset($_SESSION['LAST_ACTIVITY']) && isset($_SESSION['userEmail']) && (time() - $_SESSION['LAST_ACTIVITY']) > $session_max_time){
        session_unset();
        session_destroy();
        header("Location: index.php");
    }else{
        session_regenerate_id(true); //Change session id for the current session, to invalidade the old one
                                       // and protect agains session fixation attacks
        $_SESSION['LAST_ACTIVITY'] = time();
    }
?>