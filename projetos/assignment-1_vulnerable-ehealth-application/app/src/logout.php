<?php
    session_start();
    unset($_SESSION['userEmail']);
    header("Location: index.php");
?>