<?php
function generateRandomString($length = 12) {
    $characters = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ';
    $charactersLength = strlen($characters);
    $randomString = '';
    for ($i = 0; $i < $length; $i++) {
        $randomString .= $characters[rand(0, $charactersLength - 1)];
    }
    return $randomString;
}

class Database{
    public $conn;

    function __construct() {
        $this->conn = $this->create_connection();
    }

    function __destruct() {
        $this->close_connection();
    }

    public function getconn(){
        return $this->conn;
    }

    private function create_connection(){
        $server='mysql_db';
        $user='root';
        $password='easyPass123';
        $db='SIO';
        
        $conn = @mysqli_connect($server, $user, $password, $db) or die("A problem occurred while connecting to database, please go to reset.php page");
        /* check connection */
        if (!$conn) {
            //echo $e->getMessage();
            // $conn->connect_errno
            //echo "Failed to connect to MySQL database: (" . $conn->connect_errno . ") " . $conn->connect_error;
            header("Location: info.php?type=3");
            //die();
        }

        return $conn;
    }

    public function make_query($query){
        return mysqli_query($this->conn, $query);
    }

    private function close_connection(){
        mysqli_close($this->conn);
    }

}

/* Example Usage:
    $user = new users();
    $user->create('test', 'test', 'test@ua.pt', 'password', 1);
*/

class users extends Database{

    function __construct() {
        parent::__construct();
    }

    function create($firstName, $lastName, $email, $password, $roleId)
    {
        $query = "INSERT INTO users(first_name,last_name,email,password,role) 
            VALUES('".$firstName."','".$lastName."','".$email."','".$password."',".$roleId.");";
        return $this->make_query($query);
    }
    
    function delete_using_email($email){
        $query = "DELETE FROM users WHERE email ='".$email."'";
        return $this->make_query($query);
    }

    function delete_using_id($id){
        $query = "DELETE FROM users WHERE id =".$id."";
        return $this->make_query($query);
    }

    function delete_everything(){
        $query = "DELETE FROM users;";
        return $this->make_query($query);
    }

    function update_using_email($email, $firstName, $lastName, $roleId){
        $query = "UPDATE users SET first_name = '".$firstName."', last_name = '".$lastName."', role = ".$roleId." WHERE email ='".$email."'";
        return $this->make_query($query);
    }

    function update_using_id($id, $firstName, $lastName, $roleId){
        $query = "UPDATE users SET first_name = '".$firstName."', last_name = '".$lastName."', role = ".$roleId." WHERE id =".$id."";
        return $this->make_query($query);
    }

    function update_role_using_id($id , $roleId)
    {
        $query = "UPDATE users SET role = ".$roleId." WHERE id =".$id."";
        return $this->make_query($query);
    }

    function change_credentials($email, $password){
        $query = "UPDATE users SET email = '".$email."', password = '".$password."' WHERE email ='".$email."'";
        return $this->make_query($query);
    }

    function check_credentials($email, $password){
        $query = "SELECT * FROM users WHERE email = '".$email."' && password = '".$password."'";
        return $this->make_query($query);
    }

    function check_email($email){
        $query = "SELECT * FROM users WHERE email = '".$email."';";
        return $this->make_query($query);
    }

    function select_using_id($userId){
        $query = "SELECT * FROM users WHERE id = ".$userId.";";
        return $this->make_query($query);
    }

    function select_everything(){
        $query = "SELECT * FROM users;";
        return $this->make_query($query);
    }

    function select_by_id($id)
    {
        $query = "SELECT * FROM users WHERE id = '".$id."'";
        return $this->make_query($query);
    }

    function select_by_email($email)
    {
        $query = "SELECT * FROM users WHERE email = '".$email."'";
        return $this->make_query($query);
    }

    function upload_image($email, $imagePath){
        $query = "UPDATE users SET email = '".$email."', image = '".$imagePath."' WHERE email ='".$email."'";
        return $this->make_query($query);
    }
}

/* Example Usage:
    $comment = new comments();
    $comment->delete_using_id(12);
*/

class comments extends Database{
    function __construct() {
        parent::__construct();
    }

    function insert($fromUserId, $toUserId, $comment, $depth){
        $query = "INSERT INTO comments(from_user_id,to_user_id,comment,depth) 
            VALUES(".$fromUserId.",".$toUserId.",'".$comment."',".$depth.");";
        return $this->make_query($query);
    }

    function delete_using_id($commentId){
        $query = "DELETE FROM comments WHERE id = ".$commentId.";";
        return $this->make_query($query);
    }

    function delete_using_user($userId){
        $query = "DELETE FROM comments WHERE from_user_id = ".$userId." OR to_user_id = ".$userId.";";
        return $this->make_query($query);
    }

    function delete_everything(){
        $query = "DELETE FROM comments;";
        return $this->make_query($query);
    }

    function update($commentId, $newComment){
        $query = "UPDATE comments SET comment = '".$newComment."' WHERE id ='".$commentId."';";
        return $this->make_query($query);
    }

    function select_everything(){
        $query = "SELECT * FROM comments;";
        return $this->make_query($query);
    }

    function select_using_id($id){
        $query = "SELECT * FROM comments WHERE id = ".$id.";";
        return $this->make_query($query);
    }

    function select_from_user($fromUserId){
        $query = "SELECT * FROM comments WHERE from_user_id = ".$fromUserId.";";
        return $this->make_query($query);
    }

    function select_to_user($toUserId){
        $query = "SELECT * FROM comments WHERE to_user_id = ".$toUserId.";";
        return $this->make_query($query);
    }

}

/* Example Usage:
    $roles = new roles();
    $roles->insert('admin');
*/

class roles extends Database{
    function __construct() {
        parent::__construct();
    }

    function insert($role){
        $query = "INSERT INTO roles(role) VALUES('".$role."');";
        return $this->make_query($query);
    }

    function delete_using_id($roleId){
        $query = "DELETE FROM roles WHERE id = ".$roleId.";";
        return $this->make_query($query);
    }

    function delete_using_name($name){
        $query = "DELETE FROM roles WHERE role = '".$name."';";
        return $this->make_query($query);
    }

    function delete_everything(){
        $query = "DELETE FROM roles;";
        return $this->make_query($query);
    }

    function update($roleId, $newRole){
        $query = "UPDATE roles SET role = '".$newRole."' WHERE id =".$roleId.";";
        return $this->make_query($query);
    }

    function select_everything(){
        $query = "SELECT * FROM roles;";
        return $this->make_query($query);
    }

    function select_by_id($roleId){
        $query = "SELECT * FROM roles where id = ".$roleId.";";
        return $this->make_query($query);
    }

}


/* Example Usage:
    $s = new specialties();
    $s->insert('podologista');
*/

class specialties extends Database{
    function __construct(){
        parent::__construct();
    }

    function insert($name){
        $query = "INSERT INTO specialties(name) VALUES('".$name."');";
        return $this->make_query($query);
    }

    function delete_using_id($id){
        $query = "DELETE FROM specialties WHERE id = ".$id.";";
        return $this->make_query($query);
    }

    function delete_using_name($name){
        $query = "DELETE FROM specialties WHERE name = '".$name."';";
        return $this->make_query($query);
    }

    function delete_everything(){
        $query = "DELETE FROM specialties;";
        return $this->make_query($query);
    }

    function update_specialties($specialtyId, $newName){
        $query = "UPDATE specialties SET name = '".$newName."' WHERE id = ".$specialtyId.";";
        return $this->make_query($query);
    }

    function select_everything(){
        $query = "SELECT * FROM specialties;";
        return $this->make_query($query);
    }

    function select_by_id($id){
        $query = "SELECT * FROM specialties WHERE id = ".$id.";";
        return $this->make_query($query);
    }
}

class specialties_doctors extends Database{
    function __construct(){
        parent::__construct();
    }

    function insert($doctorsId, $specialtiesId){
        $query = "INSERT INTO specialties_doctors(doctors_id, specialties_id) VALUES(".$doctorsId.",".$specialtiesId.");";
        return $this->make_query($query);
    }

    function delete_using_id($id){
        $query = "DELETE FROM specialties_doctors WHERE id = ".$id.";";
        return $this->make_query($query);
    }


    function delete_using_doctors_id($doctorsId){
        $query = "DELETE FROM specialties_doctors WHERE doctors_id = ".$doctorsId.";";
        return $this->make_query($query);
    }

    function delete_using_specialties_id($specialtiesId){
        $query = "DELETE FROM specialties_doctors WHERE specialties_id = ".$specialtiesId.";";
        return $this->make_query($query);
    }

    function delete_everything(){
        $query = "DELETE FROM specialties_doctors;";
        return $this->make_query($query);
    }

    function update_using_id($id, $specialties_id){
        $query = "UPDATE specialties_doctors SET specialties_id = ".$specialties_id." WHERE doctors_id = ".$id.";";
        return $this->make_query($query);
    }

    function select_everything(){
        $query = "SELECT * FROM specialties_doctors;";
        return $this->make_query($query);
    }

    function select_by_specialties_id($specialtiesId){
        $query = "SELECT * FROM specialties_doctors WHERE specialties_id = ".$specialtiesId.";";
        return $this->make_query($query);
    }

    function select_by_doctors_id($doctorsId){
        $query = "SELECT * FROM specialties_doctors WHERE doctors_id = ".$doctorsId.";";
        return $this->make_query($query);
    }

    function check_doctor_specialty($doctorId, $specialtyId){
        $query = "SELECT * FROM specialties_doctors WHERE doctors_id = ".$doctorId." AND specialties_id = ".$specialtyId.";";
        return $this->make_query($query);
    }
}

/* Example Usage:
    $ap = new appointments();
    $ap->delete_everything();
*/

class appointments extends Database{
    function __construct(){
        parent::__construct();
    }


    function insert($doctorsId, $clientId, $confirmed, $completed, $date){
        $res = $this->select_everything();
        $code = 1000 +  intval(mysqli_num_rows($res));

        $query = "INSERT INTO appointments(doctors_id,client_id,confirmed,completed,date,booked_timestamp,report_text,code) 
            VALUES(".$doctorsId.", ".$clientId.", ".$confirmed.", ".$completed.", '".$date."', NOW() , NULL , '".$code."');";
        return $this->make_query($query);
    }

    function set_report_text_using_id($id , $text)
    {
        $query = "UPDATE  appointments SET report_text = '".$text."' WHERE id = ".$id.";";
        return $this->make_query($query);
    }

    function delete_using_id($id){
        $query = "DELETE FROM appointments WHERE id = ".$id.";";
        return $this->make_query($query);
    }

    function delete_using_doctorClients($id){
        $query = "DELETE FROM appointments WHERE doctors_id = ".$id." OR client_id = ".$id.";";
        return $this->make_query($query);
    }

    function set_confirmed_by_id($id)
    {
        $query = "UPDATE appointments SET confirmed = '1' WHERE id = ".$id.";";
        return $this->make_query($query);
    }

    function set_done_by_id($id)
    {
        $query = "UPDATE appointments SET completed = '1' WHERE id = ".$id.";";
        return $this->make_query($query);
    }

    function delete_everything(){
        $query = "DELETE FROM appointments;";
        return $this->make_query($query);
    }

    function set_confirmed($id){
        $query = "UPDATE appointments SET confirmed = 1 WHERE id = ".$id.";";
    }

    function set_completed($id){
        $query = "UPDATE appointments SET completed = 1 WHERE id = ".$id.";";
    }

    function select_everything(){
        $query = "SELECT * FROM appointments;";
        return $this->make_query($query);
    }

    function select_using_doctor_id($doctorsId){
        $query = "SELECT * FROM appointments WHERE doctors_id = ".$doctorsId.";";
        return $this->make_query($query);
    }

    function select_using_client_id($clientId){
        $query = "SELECT * FROM appointments WHERE client_id = ".$clientId.";";
        return $this->make_query($query);
    }

    function select_using_code($code)
    {
        $query = "SELECT * FROM appointments WHERE code = '".$code."'";
        return $this->make_query($query);
    }

    function select_using_date($date){
        $query = "SELECT * FROM appointments WHERE date = '".$date."';";
        return $this->make_query($query);
    }

    function select_using_date_doctor_id($date, $doctorID){
        $query = "SELECT * FROM appointments WHERE date = '".$date."' AND doctors_id = ".$doctorID.";";
        return $this->make_query($query);
    }
}

/* Example Usage:
    $con = new contacts();
    $con->delete_everything();
*/

class contacts extends Database{
    function __construct() {
        parent::__construct();
    }

    function insert($type, $info,$date){
        $query = "INSERT INTO contacts(type,information,timestamp) VALUES('".$type."','".$info."','".$date."');";
        return $this->make_query($query);
    }

    function delete_using_id($contactId){
        $query = "DELETE FROM contacts WHERE id = ".$contactId.";";
        return $this->make_query($query);
    }

    function delete_everything(){
        $query = "DELETE FROM contacts;";
        return $this->make_query($query);
    }

    function select_everything(){
        $query = "SELECT * FROM contacts;";
        return $this->make_query($query);
    }

    function select_by_id($contactId){
        $query = "SELECT * FROM contacts where id = ".$contactId.";";
        return $this->make_query($query);
    }

    function select_by_type($type){
        $query = "SELECT * FROM contacts where type = ".$type.";";
        return $this->make_query($query);
    }

}

function validateInputs($data, $type){
    $filter = false;
    switch($type)
    {
        case 'email':
            $filter = FILTER_VALIDATE_EMAIL;    
        break;
        case 'int':
            $filter = FILTER_VALIDATE_INT;
        break;
        case 'boolean':
            $filter = FILTER_VALIDATE_BOOLEAN;
        break;
    }
    if(!$filter || filter_var($data, $filter) === false)
        return false;
    else
        return true;
    //return ($filter === false) ? false : filter_var($data, $filter) !== false ? true : false;
}

?>
