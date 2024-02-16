<?php

    function generate_token(){
        //$commentDb = new comments();
        
        $_SESSION['csrf_token'] = hash('sha512', uniqid(mt_rand(), true));
        //$commentDb->insert(1, 1, $_SESSION['csrf_token'], 0);
    }

    function check_valid_token($token){
        if(!isset($_SESSION['csrf_token'])) return false;
        return hash_equals($_SESSION['csrf_token'], $token);
    }



?>